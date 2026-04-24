from fastapi import APIRouter, Request, Header, HTTPException
import os
import stripe
from app.core.config import get_settings
from app.services.stripe_service import StripeService
import logging

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

@router.post("/stripe/webhook")
async def stripe_webhook(req: Request, stripe_signature: str = Header(None)):
    settings = get_settings()
    webhook_secret = settings.stripe_webhook_secret
    payload = await req.body()
    
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, webhook_secret)
        
        # Add logging for received webhook events
        logger = logging.getLogger(__name__)
        logger.info(f"Received Stripe webhook: event_type={event['type']}, event_id={event['id']}")
        
        # Delegate event handling to StripeService
        stripe_service = StripeService()
        result = await stripe_service.handle_webhook_event(payload, stripe_signature)
        return result
        
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")