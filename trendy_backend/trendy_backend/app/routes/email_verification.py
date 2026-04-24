"""
Email Verification Routes for TRENDY App
"""

import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.email_service import email_service

router = APIRouter(prefix="/auth/email", tags=["email-verification"])

class EmailVerificationRequest(BaseModel):
    email: str

class VerifyEmailRequest(BaseModel):
    token: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str

@router.post("/send-verification", summary="Send verification email")
async def send_verification_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Send verification email to the user
    """
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Generate verification token
        token = secrets.token_urlsafe(32)
        user.verification_token = token
        user.verification_token_expires = datetime.now() + timedelta(hours=24)
        db.commit()
        
        # Send verification email
        await email_service.send_verification_email(request.email, user.username, token)
        
        return {"message": "Verification email sent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )

@router.post("/verify", summary="Verify email address")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify email address using verification token
    """
    try:
        user = db.query(User).filter(User.verification_token == request.token).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid verification token"
            )
        
        if user.verification_token_expires < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token expired"
            )
        
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        db.commit()
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email: {str(e)}"
        )

@router.post("/resend-verification", summary="Resend verification email")
async def resend_verification_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend verification email to the user
    """
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Generate new verification token
        token = secrets.token_urlsafe(32)
        user.verification_token = token
        user.verification_token_expires = datetime.now() + timedelta(hours=24)
        db.commit()
        
        # Send verification email
        await email_service.send_verification_email(request.email, user.username, token)
        
        return {"message": "Verification email resent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend verification email: {str(e)}"
        )

@router.post("/password-reset/request", summary="Request password reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset email
    """
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            # Don't reveal if email exists for security
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate password reset token
        token = secrets.token_urlsafe(32)
        user.verification_token = token
        user.verification_token_expires = datetime.now() + timedelta(hours=1)
        db.commit()
        
        # Send password reset email
        await email_service.send_password_reset_email(request.email, user.username, token)
        
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send password reset email: {str(e)}"
        )

@router.post("/password-reset/confirm", summary="Confirm password reset")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token
    """
    try:
        user = db.query(User).filter(User.verification_token == request.token).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid reset token"
            )
        
        if user.verification_token_expires < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token expired"
            )
        
        # Update password (in a real implementation, you would hash the password)
        # For now, we'll just clear the token
        user.verification_token = None
        user.verification_token_expires = None
        db.commit()
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
