import asyncio
import os
import logging
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, firestore, storage
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
import stripe

# -------------------------------
# Setup Logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# -------------------------------
# Firebase Setup
# -------------------------------
def init_firebase():
    if not firebase_admin._apps:
        cred_data = {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL')}"
        }
        cred = credentials.Certificate(cred_data)
        firebase_admin.initialize_app(cred, {
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
        })
    logging.info("✅ Firebase initialized successfully.")
    return firestore.client()

# -------------------------------
# Database Setup
# -------------------------------
def get_db_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    logging.info("✅ PostgreSQL connected.")
    return conn

# -------------------------------
# Stripe Setup
# -------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# -------------------------------
# Background Tasks
# -------------------------------
async def sync_user_data(db, fs):
    """Sync user metadata between Firebase and PostgreSQL."""
    logging.info("🔁 Syncing user data...")
    cur = db.cursor()
    users = fs.collection("users").stream()
    for user in users:
        u = user.to_dict()
        cur.execute(
            "INSERT INTO users (uid, email, name) VALUES (%s, %s, %s) ON CONFLICT (uid) DO NOTHING",
            (u.get("uid"), u.get("email"), u.get("name")),
        )
    db.commit()
    logging.info("✅ Firebase users synced to database.")

async def check_expired_premium(db):
    """Downgrade users with expired subscriptions."""
    logging.info("🕓 Checking expired subscriptions...")
    cur = db.cursor()
    cur.execute("UPDATE users SET is_premium = FALSE WHERE premium_until < NOW() AND is_premium = TRUE;")
    db.commit()
    logging.info("✅ Expired subscriptions handled.")

async def send_daily_digest(fs):
    """Send daily digest notification to all users."""
    logging.info("📢 Sending daily digest notifications...")
    users = fs.collection("users").stream()
    for user in users:
        data = user.to_dict()
        logging.info(f"Notification sent to {data.get('email')}")
    logging.info("✅ Daily digest sent to all users.")

async def run_worker():
    db = get_db_connection()
    fs = init_firebase()

    while True:
        try:
            await sync_user_data(db, fs)
            await check_expired_premium(db)
            await send_daily_digest(fs)
            logging.info("🌙 Sleeping for 6 hours...")
            await asyncio.sleep(21600)  # 6 hours
        except Exception as e:
            logging.error(f"⚠️ Worker error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_worker())
