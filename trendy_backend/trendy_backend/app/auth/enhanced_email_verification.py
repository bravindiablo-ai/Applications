from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import os
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.jwt import create_access_token

router = APIRouter(prefix="/auth/email", tags=["Email Verification"])

class EmailRequest(BaseModel):
    email: EmailStr

class VerificationRequest(BaseModel):
    email: EmailStr
    code: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class EmailVerificationResponse(BaseModel):
    message: str
    token: str = None

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@trendyapp.com")

def send_verification_email(email: str, token: str, username: str = None):
    """Send verification email to user"""
    subject = "Verify your Trendy account"
    verification_link = f"http://localhost:3000/verify-email?token={token}"
    
    body = f"""
    Hi {username or 'there'}!
    
    Please click the link below to verify your email address:
    {verification_link}
    
    This link will expire in 24 hours.
    
    Best regards,
    The Trendy Team
    """
    
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@router.post("/send-verification", response_model=EmailVerificationResponse)
async def send_verification(
    request: EmailRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """Send verification email to user"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate verification token
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    db.commit()
    
    # Send email in background
    background_tasks.add_task(
        send_verification_email, 
        request.email, 
        token, 
        user.username
    )
    
    return {"message": "Verification email sent successfully"}

@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    token: str, 
    db: Session = Depends(get_db)
):
    """Verify email with token"""
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user.email_verified = True
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    # Create JWT token for immediate login
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "message": "Email verified successfully",
        "token": access_token
    }

@router.post("/resend-verification", response_model=EmailVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Resend verification email"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate new verification token
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    db.commit()
    
    # Send email in background
    background_tasks.add_task(
        send_verification_email,
        request.email,
        token,
        user.username
    )
    
    return {"message": "Verification email resent successfully"}
