"""
Email Verification Module for TRENDY App
Handles email verification workflow and user activation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.database import get_db
from app.models.user import User
from app.core.config import get_settings
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth/email", tags=["email-verification"])

class EmailVerificationRequest(BaseModel):
    email: str

class EmailVerificationConfirm(BaseModel):
    email: str
    token: str

class ResendVerificationRequest(BaseModel):
    email: str

class EmailService:
    """Email service for sending verification emails"""
    
    @staticmethod
    async def send_verification_email(email: str, token: str, background_tasks: BackgroundTasks):
        """Send verification email to user"""
        
        settings = get_settings()
        subject = "Verify your TRENDY account"
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}&email={email}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Verify your TRENDY account</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #1a73e8; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ background: #1a73e8; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to TRENDY!</h1>
                </div>
                <div class="content">
                    <h2>Verify your email address</h2>
                    <p>Thank you for signing up for TRENDY! Please click the button below to verify your email address.</p>
                    <p>
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p>{verification_url}</p>
                    <p>This link will expire in 24 hours.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        background_tasks.add_task(
            send_email_async,
            email=email,
            subject=subject,
            html_content=html_content
        )

@router.post("/send-verification")
async def send_verification_email(
    request: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send email verification to user"""
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    user.email_verification_token = verification_token
    user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    db.commit()
    
    # Send verification email
    await EmailService.send_verification_email(
        email=request.email,
        token=verification_token,
        background_tasks=background_tasks
    )
    
    return {"message": "Verification email sent successfully"}

@router.post("/verify")
async def verify_email(request: EmailVerificationConfirm, db: Session = Depends(get_db)):
    """Verify email address with token"""
    
    user = db.query(User).filter(
        User.email == request.email,
        User.email_verification_token == request.token
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    if user.email_verification_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token expired")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Mark email as verified
    user.is_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Resend verification email"""
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate new verification token
    verification_token = secrets.token_urlsafe(32)
    user.email_verification_token = verification_token
    user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    db.commit()
    
    # Send verification email
    await EmailService.send_verification_email(
        email=request.email,
        token=verification_token,
        background_tasks=background_tasks
    )
    
    return {"message": "Verification email resent successfully"}

async def send_email_async(email: str, subject: str, html_content: str):
    """Send email asynchronously"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = email
        
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
