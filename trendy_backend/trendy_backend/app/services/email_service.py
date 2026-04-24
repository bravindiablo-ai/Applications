"""
Email Service for TRENDY App
Handles sending verification emails and other email-related functionalities
"""

import os
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import Dict, Any
import secrets
from datetime import datetime, timedelta

class EmailService:
    def __init__(self):
        # Configure SMTP settings
        self.conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME", "test@example.com"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "password"),
            MAIL_FROM=os.getenv("MAIL_FROM", "test@example.com"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "TRENDY App"),
            MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
            MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render HTML template with context
        """
        template_path = f"app/templates/{template_name}"
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template {template_name} not found")
        
        with open(template_path, "r") as file:
            template = file.read()
        
        # Simple template rendering
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        
        return template
    
    async def send_verification_email(self, email: EmailStr, username: str, token: str):
        """
        Send verification email to the user
        """
        try:
            verification_link = f"http://localhost:8000/api/v1/auth/email/verify?token={token}"
            html_content = self._render_template("email_verification.html", {
                "username": username,
                "verification_link": verification_link
            })
            
            message = MessageSchema(
                subject="Email Verification - TRENDY App",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            fm = FastMail(self.conf)
            await fm.send_message(message)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send verification email: {str(e)}"
            )
    
    async def send_password_reset_email(self, email: EmailStr, username: str, token: str):
        """
        Send password reset email to the user
        """
        try:
            reset_link = f"http://localhost:3000/reset-password?token={token}"
            html_content = self._render_template("password_reset.html", {
                "username": username,
                "reset_link": reset_link
            })
            
            message = MessageSchema(
                subject="Password Reset - TRENDY App",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            fm = FastMail(self.conf)
            await fm.send_message(message)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send password reset email: {str(e)}"
            )
    
    async def send_welcome_email(self, email: EmailStr, username: str):
        """
        Send welcome email to the user
        """
        try:
            html_content = f"""
            <html>
            <body>
                <h1>Welcome to TRENDY App, {username}!</h1>
                <p>Thank you for joining our community. We're excited to have you on board!</p>
                <p>Start exploring and connecting with others today.</p>
                <p>Best regards,<br>The TRENDY Team</p>
            </body>
            </html>
            """
            
            message = MessageSchema(
                subject="Welcome to TRENDY App!",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            fm = FastMail(self.conf)
            await fm.send_message(message)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send welcome email: {str(e)}"
            )

email_service = EmailService()
