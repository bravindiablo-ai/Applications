"""
Test script for email service functionality
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.email_service import email_service

async def test_email_service():
    """Test email service functionality"""
    print("Testing email service...")
    
    try:
        # Test sending verification email
        print("Sending verification email...")
        await email_service.send_verification_email(
            "test@example.com", 
            "Test User", 
            "test_token_123"
        )
        print("✓ Verification email sent successfully")
        
        # Test sending password reset email
        print("Sending password reset email...")
        await email_service.send_password_reset_email(
            "test@example.com", 
            "Test User", 
            "reset_token_123"
        )
        print("✓ Password reset email sent successfully")
        
        # Test sending welcome email
        print("Sending welcome email...")
        await email_service.send_welcome_email(
            "test@example.com", 
            "Test User"
        )
        print("✓ Welcome email sent successfully")
        
        print("\nAll email service tests passed! 🎉")
        
    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_email_service())
