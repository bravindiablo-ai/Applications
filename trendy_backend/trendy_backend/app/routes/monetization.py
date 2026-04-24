"""
Monetization API Routes for TRENDY App
Handles Stripe payments, subscriptions, and revenue tracking
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
import stripe

from app.database import get_db
from app.auth.middleware import get_current_user
from app.services.stripe_service import stripe_service
from app.models.user import User
from app.models.subscription_corrected import Subscription, Payment
from app.schemas.subscription import SubscriptionResponse, SubscriptionCreate
from app.schemas.ads import AdImpressionCreate, AdImpressionResponse

router = APIRouter(prefix="/monetization", tags=["monetization"])

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    try:
        plans = await stripe_service.get_subscription_plans()
        return {"plans": plans}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription plans: {str(e)}"
        )

@router.post("/create-checkout-session")
async def create_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session for subscription"""
    try:
        session_data = await stripe_service.create_checkout_session(
            current_user, price_id, success_url, cancel_url
        )
        
        # Create subscription record in database
        subscription = Subscription(
            user_id=current_user.id,
            stripe_subscription_id=None,  # Will be updated via webhook
            plan_id=price_id,
            status="pending"
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return {
            "session_id": session_data["session_id"],
            "url": session_data["url"],
            "subscription_id": subscription.id
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/create-payment-intent")
async def create_payment_intent(
    amount: int,
    currency: str = "usd",
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a payment intent for one-time payments"""
    try:
        intent_data = await stripe_service.create_payment_intent(
            current_user, amount, currency, description
        )
        
        # Create payment record in database
        payment = Payment(
            user_id=current_user.id,
            stripe_payment_intent_id=intent_data["payment_intent_id"],
            amount=amount / 100,  # Convert from cents to dollars
            currency=currency.upper(),
            status="pending",
            description=description
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return {
            "client_secret": intent_data["client_secret"],
            "payment_intent_id": intent_data["payment_intent_id"],
            "payment_id": payment.id
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}"
        )

@router.get("/subscriptions")
async def get_user_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subscriptions for the current user"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    
    return [
        SubscriptionResponse(
            id=sub.id,
            user_id=sub.user_id,
            provider="stripe",
            subscription_id=sub.stripe_subscription_id,
            product_id=sub.plan_id,
            status=sub.status,
            current_period_start=sub.current_period_start,
            current_period_end=sub.current_period_end,
            cancel_at_period_end=sub.cancel_at_period_end,
            metadata=sub.subscription_metadata,
            created_at=sub.created_at,
            updated_at=sub.updated_at
        )
        for sub in subscriptions
    ]

@router.get("/payments")
async def get_user_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payments for the current user"""
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return [
        {
            "id": payment.id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "payment_method": payment.payment_method,
            "description": payment.description,
            "created_at": payment.created_at,
            "paid_at": payment.paid_at
        }
        for payment in payments
    ]

@router.post("/webhook")
async def handle_stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        result = await stripe_service.handle_webhook_event(payload, sig_header)
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )

@router.post("/cancel-subscription/{subscription_id}")
async def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    if subscription.stripe_subscription_id:
        try:
            # Cancel subscription in Stripe
            stripe.Subscription.delete(subscription.stripe_subscription_id)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to cancel subscription: {str(e)}"
            )
    
    # Update subscription status in database
    subscription.status = "canceled"
    db.commit()
    
    return {"message": "Subscription canceled successfully"}

@router.get("/subscription-status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription status"""
    active_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    return {
        "has_active_subscription": active_subscription is not None,
        "subscription_tier": current_user.subscription_tier,
        "is_premium": current_user.is_premium,
        "subscription": active_subscription.dict() if active_subscription else None
    }
