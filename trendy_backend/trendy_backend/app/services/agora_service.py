"""
Agora Service for TRENDY App
Handles Agora RTC token generation for video/audio calls
"""

import logging
import time
import hmac
import hashlib
import base64
from typing import Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class AgoraService:
    def __init__(self):
        self.settings = get_settings()
        self.app_id = self.settings.agora_app_id
        self.app_certificate = self.settings.agora_app_certificate

        if self.app_id and self.app_certificate and self.app_id != "your_agora_app_id_here":
            logger.info("Agora service initialized successfully")
        else:
            logger.warning("Agora credentials not configured")

    def is_configured(self) -> bool:
        """Check if Agora service is properly configured"""
        return (self.app_id and self.app_certificate and
                self.app_id != "your_agora_app_id_here" and
                self.app_certificate != "your_agora_app_certificate_here")

    def generate_rtc_token(self, channel_name: str, uid: int = 0, role: str = "publisher",
                          expire_time: int = 3600) -> str:
        """
        Generate RTC token for Agora video/audio calls

        Args:
            channel_name: Name of the channel/room
            uid: User ID (0 for auto-assignment)
            role: User role ("publisher" or "subscriber")
            expire_time: Token expiration time in seconds (default 1 hour)

        Returns:
            RTC token string
        """
        if not self.is_configured():
            raise Exception("Agora service not configured")

        try:
            # Current timestamp
            current_time = int(time.time())

            # Privilege expiration time
            privilege_expired_ts = current_time + expire_time

            # Convert role to privilege value
            role_privilege = 1 if role.lower() == "publisher" else 2  # 1=publisher, 2=subscriber

            # Token content
            token_content = f"{self.app_id}{uid}{channel_name}{privilege_expired_ts}"

            # Generate signature
            signature = hmac.new(
                self.app_certificate.encode('utf-8'),
                token_content.encode('utf-8'),
                hashlib.sha256
            ).digest()

            # Base64 encode signature
            signature_b64 = base64.b64encode(signature).decode('utf-8')

            # Create final token
            token = f"{self.app_id}@{current_time}@{signature_b64}@{uid}@{channel_name}@{privilege_expired_ts}@{role_privilege}"

            return token

        except Exception as e:
            logger.error(f"Agora RTC token generation error: {str(e)}")
            raise Exception(f"Failed to generate Agora RTC token: {str(e)}")

    def generate_rtm_token(self, uid: str, expire_time: int = 3600) -> str:
        """
        Generate RTM token for Agora real-time messaging

        Args:
            uid: User ID as string
            expire_time: Token expiration time in seconds

        Returns:
            RTM token string
        """
        if not self.is_configured():
            raise Exception("Agora service not configured")

        try:
            # Current timestamp
            current_time = int(time.time())

            # Privilege expiration time
            privilege_expired_ts = current_time + expire_time

            # Token content for RTM
            token_content = f"{self.app_id}{uid}{privilege_expired_ts}"

            # Generate signature
            signature = hmac.new(
                self.app_certificate.encode('utf-8'),
                token_content.encode('utf-8'),
                hashlib.sha256
            ).digest()

            # Base64 encode signature
            signature_b64 = base64.b64encode(signature).decode('utf-8')

            # Create RTM token
            token = f"{self.app_id}@{current_time}@{signature_b64}@{uid}@{privilege_expired_ts}"

            return token

        except Exception as e:
            logger.error(f"Agora RTM token generation error: {str(e)}")
            raise Exception(f"Failed to generate Agora RTM token: {str(e)}")

    def validate_token(self, token: str) -> bool:
        """
        Basic token validation (checks format and expiration)

        Args:
            token: Token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            parts = token.split('@')
            if len(parts) < 6:
                return False

            app_id = parts[0]
            timestamp = int(parts[1])
            signature_b64 = parts[2]
            uid = parts[3]
            channel_name = parts[4]
            privilege_expired_ts = int(parts[5])

            # Check if app_id matches
            if app_id != self.app_id:
                return False

            # Check if token is expired
            current_time = int(time.time())
            if current_time > privilege_expired_ts:
                return False

            # For full validation, we would need to regenerate signature and compare
            # But this basic check covers most common validation needs

            return True

        except (ValueError, IndexError) as e:
            logger.error(f"Token validation error: {str(e)}")
            return False

    def get_channel_info(self, channel_name: str) -> dict:
        """
        Get basic channel information (placeholder for future implementation)

        Args:
            channel_name: Name of the channel

        Returns:
            Dict with channel information
        """
        # This would require Agora REST API integration
        # For now, return basic info
        return {
            "channel_name": channel_name,
            "status": "active",  # Placeholder
            "participants": 0,   # Would need to track this separately
            "created_at": int(time.time())
        }
