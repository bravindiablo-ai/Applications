"""
Security service for handling authentication, encryption, and security-related functionality.
"""
import bcrypt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from jose import JWTError, jwt
from typing import Optional, Dict, Any
from app.core.config import get_settings
from app.database import SessionLocal
from collections import Counter
import logging

class SecurityService:
    """Handles all security-related operations."""
    
    def __init__(self):
        """Initialize the security service with settings."""
        self.settings = get_settings()
        self.fernet = Fernet(self.settings.ENCRYPTION_KEY.encode())
        
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode(),
            hashed_password.encode()
        )
        
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        return encoded_jwt
        
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
            
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data using Fernet."""
        return self.fernet.encrypt(data.encode())
        
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data using Fernet."""
        return self.fernet.decrypt(encrypted_data).decode()
        
    logger = logging.getLogger(__name__)
        
    def track_login_attempt(self, user_id: str, ip_address: str, device_info: str):
        """Track login attempts for fraud detection."""
        try:
            with SessionLocal() as db:
                # Create login attempt record
                attempt = LoginAttempt(
                    user_id=user_id,
                    ip_address=ip_address,
                    device_info=device_info,
                    timestamp=datetime.utcnow(),
                    success=True  # Assuming this is called after successful auth
                )
                db.add(attempt)
                db.commit()
                
                # Check for suspicious patterns
                if self.check_suspicious_activity(user_id):
                    self.logger.warning(f"Suspicious activity detected for user {user_id}")
                    # TODO: Trigger alert or additional verification
                    
        except Exception as e:
            self.logger.error(f"Failed to track login attempt: {str(e)}")
        
    def check_suspicious_activity(self, user_id: str) -> bool:
        """Check for suspicious login patterns."""
        try:
            with SessionLocal() as db:
                # Get recent login attempts (last 24 hours)
                recent_attempts = db.query(LoginAttempt).filter(
                    LoginAttempt.user_id == user_id,
                    LoginAttempt.timestamp >= datetime.utcnow() - timedelta(hours=24)
                ).all()
                
                if not recent_attempts:
                    return False
                
                # Check for multiple IPs
                ip_addresses = [attempt.ip_address for attempt in recent_attempts]
                unique_ips = set(ip_addresses)
                if len(unique_ips) > 5:  # More than 5 different IPs in 24h
                    self.logger.warning(f"User {user_id} logged in from {len(unique_ips)} different IPs")
                    return True
                
                # Check for rapid login attempts
                if len(recent_attempts) > 20:  # More than 20 logins in 24h
                    self.logger.warning(f"User {user_id} has {len(recent_attempts)} login attempts in 24h")
                    return True
                
                # Check for geographically impossible travel
                # (requires IP geolocation - implement in Phase 3)
                
                # Check for unusual device patterns
                devices = [attempt.device_info for attempt in recent_attempts]
                unique_devices = set(devices)
                if len(unique_devices) > 3:  # More than 3 different devices
                    self.logger.warning(f"User {user_id} logged in from {len(unique_devices)} different devices")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to check suspicious activity: {str(e)}")
            return False  # Fail open to avoid blocking legitimate users

# Standalone utility functions for importing
def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode()
    )
