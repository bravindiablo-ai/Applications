from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.post import Post
from app.auth.utils import get_current_user
import stripe

router = APIRouter()

# Stripe configuration (replace with your keys)
stripe.api_key = "your_stripe_secret_key"

@router.get("/monetization/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "id": "basic",
                "name": "Trendy Basic",
                "price": 4.99,
                "features": ["Ad-free experience", "Basic analytics", "Custom themes"]
            },
            {
                "id": "creator",
                "name": "Trendy Creator",
                "price": 19.99,
                "features": ["Advanced analytics", "Creator tools", "Priority support", "NFT minting"]
            },
            {
                "id": "pro",
                "name": "Trendy Pro",
                "price": 49.99,
                "features": ["All features", "Brand partnerships", "AI tools", "Exclusive content"]
            }
        ]
    }

@router.post("/monetization/subscribe")
async def create_subscription(plan_id: str, user_id: str, db: Session = Depends(get_db)):
    """Create a new subscription"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Trendy {plan_id.title()}',
                    },
                    'unit_amount': get_plan_price(plan_id) * 100,  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://trendy.app/success',
            cancel_url='https://trendy.app/cancel',
            customer_email=user.email,
        )
        
        return {"session_id": session.id, "url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/monetization/earnings/{user_id}")
async def get_creator_earnings(user_id: str, db: Session = Depends(get_db)):
    """Get creator earnings dashboard"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate earnings from various sources
    total_earnings = calculate_total_earnings(user_id, db)
    
    return {
        "total_earnings": total_earnings,
        "breakdown": {
            "subscriptions": total_earnings * 0.4,
            "tips": total_earnings * 0.3,
            "nft_sales": total_earnings * 0.2,
            "brand_partnerships": total_earnings * 0.1
        },
        "monthly_projections": generate_monthly_projections(user_id, db)
    }

@router.post("/monetization/tips/send")
async def send_tip(sender_id: str, receiver_id: str, amount: float, db: Session = Depends(get_db)):
    """Send tip to creator"""
    try:
        # Process payment through Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency='usd',
            metadata={'sender_id': sender_id, 'receiver_id': receiver_id}
        )
        
        # Record transaction
        record_tip_transaction(sender_id, receiver_id, amount, db)
        
        return {"success": True, "payment_intent": payment_intent.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_plan_price(plan_id: str) -> float:
    prices = {"basic": 4.99, "creator": 19.99, "pro": 49.99}
    return prices.get(plan_id, 4.99)

def calculate_total_earnings(user_id: str, db: Session):
    # Placeholder - implement actual calculation
    return 1250.50

def generate_monthly_projections(user_id: str, db: Session):
    # Placeholder - implement actual projection
    return {"next_month": 1500.00, "three_months": 5000.00}

def record_tip_transaction(sender_id: str, receiver_id: str, amount: float, db: Session):
    # Placeholder - implement actual transaction recording
    pass
