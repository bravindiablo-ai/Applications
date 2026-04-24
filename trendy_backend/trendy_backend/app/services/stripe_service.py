import stripe
import os
from typing import Dict, Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.user import User
from app.models.subscription_corrected import Subscription, Payment
from app.core.config import get_settings
from app.database import SessionLocal
from app.models.payment_webhook import WebhookEvent

class StripeService:
    def __init__(self):
        # Initialize Stripe with API key from environment
        settings = get_settings()
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY") or settings.stripe_secret_key
        if not stripe.api_key:
            # For development/testing, use a dummy key or skip initialization
            stripe.api_key = "sk_test_dummy"  # Dummy key for testing
            print("Warning: Using dummy Stripe key for testing. Set STRIPE_SECRET_KEY for production.")
    
    async def create_customer(self, user: User, email: str) -> str:
        """Create a Stripe customer for a user"""
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    "user_id": str(user.id),
                    "username": user.username
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create customer: {str(e)}"
            )
    
    async def create_checkout_session(
        self, 
        user: User, 
        price_id: str, 
        success_url: str, 
        cancel_url: str
    ) -> Dict:
        """Create a Stripe checkout session for subscription"""
        try:
            # Get or create customer
            customer_id = await self.get_or_create_customer(user)
            
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user.id),
                    "username": user.username
                }
            )
            
            return {
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create checkout session: {str(e)}"
            )
    
    async def get_or_create_customer(self, user: User) -> str:
        """Get existing customer or create a new one"""
        try:
            # Check if user already has a Stripe customer ID
            if user.subscriptions:
                for subscription in user.subscriptions:
                    if subscription.stripe_customer_id:
                        return subscription.stripe_customer_id
            
            # Create new customer
            customer_id = await self.create_customer(user, user.email)
            return customer_id
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get or create customer: {str(e)}"
            )
    
    async def create_payment_intent(
        self, 
        user: User, 
        amount: int, 
        currency: str = "usd",
        description: str = None
    ) -> Dict:
        """Create a payment intent for one-time payments"""
        try:
            customer_id = await self.get_or_create_customer(user)
            
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                description=description,
                metadata={
                    "user_id": str(user.id),
                    "username": user.username
                }
            )
            
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": intent.amount,
                "currency": intent.currency
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create payment intent: {str(e)}"
            )
    
    async def handle_webhook_event(self, payload: bytes, sig_header: str) -> Dict:
        """Handle Stripe webhook events"""
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
            )
            event_id = event.get('id')
            # dedupe: if we've already processed this event id, skip
            try:
                with SessionLocal() as db:
                    existing = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
                    if existing:
                        return {"status": "skipped", "event": event['type']}
            except Exception:
                # if DB is unavailable, proceed (webhook should be retried by Stripe)
                pass
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                await self._handle_checkout_completed(event)
            elif event['type'] == 'customer.subscription.updated':
                await self._handle_subscription_updated(event)
            elif event['type'] == 'customer.subscription.deleted':
                await self._handle_subscription_deleted(event)
            elif event['type'] == 'payment_intent.succeeded':
                await self._handle_payment_succeeded(event)
            # mark processed
            try:
                with SessionLocal() as db:
                    we = WebhookEvent(id=event_id, event_type=event['type'])
                    db.add(we)
                    db.commit()
            except Exception:
                # don't fail webhook if recording fails
                pass

            return {"status": "success", "event": event['type']}
            
        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook error: {str(e)}"
            )
    
    async def _handle_checkout_completed(self, event: Dict):
        """Handle checkout session completed event"""
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')
        subscription_id = session.get('subscription')
        # Update user subscription in database (mark pending subscription as active)
        try:
            if not user_id:
                return
            with SessionLocal() as db:
                # find pending subscription created when checkout session was initiated
                sub = db.query(Subscription).filter(Subscription.user_id == int(user_id), Subscription.status == 'pending').order_by(Subscription.created_at.desc()).first()
                if sub:
                    sub.stripe_subscription_id = subscription_id
                    sub.stripe_customer_id = session.get('customer')
                    sub.status = 'active'
                    # best-effort: set current period if available on session
                    # commit
                    db.add(sub)
                    db.commit()
        except Exception:
            # swallow errors to avoid failing webhook processing; they can be retried
            return
        
    async def _handle_subscription_updated(self, event: Dict):
        """Handle subscription updated event"""
        subscription = event['data']['object']
        try:
            stripe_id = subscription.get('id')
            with SessionLocal() as db:
                sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_id).first()
                if not sub:
                    return
                # update status and period boundaries if present
                sub.status = subscription.get('status', sub.status)
                # timestamps may be provided as epoch seconds
                if subscription.get('current_period_start'):
                    sub.current_period_start = datetime.fromtimestamp(int(subscription.get('current_period_start')), tz=timezone.utc)
                if subscription.get('current_period_end'):
                    sub.current_period_end = datetime.fromtimestamp(int(subscription.get('current_period_end')), tz=timezone.utc)
                sub.cancel_at_period_end = subscription.get('cancel_at_period_end', sub.cancel_at_period_end)
                sub.subscription_metadata = subscription.get('metadata', sub.subscription_metadata)
                db.add(sub)
                db.commit()
        except Exception:
            return
        
    async def _handle_subscription_deleted(self, event: Dict):
        """Handle subscription deleted event"""
        subscription = event['data']['object']
        try:
            stripe_id = subscription.get('id')
            with SessionLocal() as db:
                sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_id).first()
                if not sub:
                    return
                sub.status = 'canceled'
                sub.canceled_at = datetime.now(timezone.utc)
                db.add(sub)
                db.commit()
        except Exception:
            return
        
    async def _handle_payment_succeeded(self, event: Dict):
        """Handle payment succeeded event"""
        payment_intent = event['data']['object']
        try:
            pi_id = payment_intent.get('id')
            # amount_received in cents
            amount = payment_intent.get('amount_received')
            currency = payment_intent.get('currency')
            charges = payment_intent.get('charges', {}).get('data', [])
            payment_method = None
            invoice_id = None
            if charges:
                ch = charges[0]
                payment_method = ch.get('payment_method_details', {}).get('type')
                invoice_id = ch.get('invoice')

            with SessionLocal() as db:
                pay = db.query(Payment).filter(Payment.stripe_payment_intent_id == pi_id).first()
                if not pay:
                    # create a best-effort payment record if missing
                    pay = Payment(
                        subscription_id=None,
                        user_id=int(payment_intent.get('metadata', {}).get('user_id') or 0),
                        stripe_payment_intent_id=pi_id,
                        amount=(float(amount) / 100.0) if amount else 0.0,
                        currency=(currency or 'USD').upper(),
                        status='succeeded',
                        description=payment_intent.get('description'),
                        payment_metadata=payment_intent
                    )
                    db.add(pay)
                    db.commit()
                    db.refresh(pay)
                if pay:
                    if amount is not None:
                        # store in dollars
                        try:
                            pay.amount = float(amount) / 100.0
                        except Exception:
                            pass
                    if currency:
                        pay.currency = currency.upper()
                    pay.status = 'succeeded'
                    pay.paid_at = datetime.now(timezone.utc)
                    pay.payment_method = payment_method
                    pay.payment_metadata = payment_intent
                    if invoice_id:
                        pay.stripe_invoice_id = invoice_id
                    db.add(pay)
                    db.commit()
        except Exception:
            return
    
    async def get_subscription_plans(self) -> List[Dict]:
        """Get available subscription plans"""
        try:
            prices = stripe.Price.list(active=True, type='recurring')
            plans = []
            
            for price in prices.data:
                product = stripe.Product.retrieve(price.product)
                plans.append({
                    "id": price.id,
                    "product_id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "amount": price.unit_amount,
                    "currency": price.currency,
                    "interval": price.recurring.interval,
                    "interval_count": price.recurring.interval_count,
                    "metadata": product.metadata
                })
            
            return plans
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get subscription plans: {str(e)}"
            )

# Create global instance
stripe_service = StripeService()
