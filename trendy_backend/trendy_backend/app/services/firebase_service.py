import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import get_settings

settings = get_settings()

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    # Initialize Firebase
    if not firebase_admin._apps:
        try:
            cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("Firebase Initialized")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"⚠️ Firebase credentials could not be loaded from env var. Error: {e}. Firebase authentication disabled.")

# Call initialization on module import
initialize_firebase()
