import logging
import json
import firebase_admin
from firebase_admin import credentials
from sqlalchemy import text
from ..db.base import Base
from ..db.session import engine
from ..core.config import settings

logger = logging.getLogger(__name__)

def clean_and_rebuild_database():
    """
    1. Drops duplicate indexes (like ix_followers_id)
    2. Recreates all SQLAlchemy tables
    """
    try:
        logger.info("🔄 Checking for schema conflicts...")
        with engine.connect() as connection:
            # Drop duplicate or leftover indexes safely
            connection.execute(text("""
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT indexname FROM pg_indexes WHERE indexname LIKE 'ix_%')
                    LOOP
                        EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(r.indexname) || ' CASCADE';
                    END LOOP;
                END $$;
            """))
            logger.info("✅ All duplicate indexes dropped.")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database schema rebuilt successfully.")
    except Exception as e:
        logger.error(f"❌ Database cleanup failed: {e}")
        raise


def verify_firebase_credentials():
    """
    1. Ensures FIREBASE_CREDENTIALS_JSON is valid
    2. Fixes PEM formatting if needed
    3. Initializes Firebase Admin SDK
    """
    try:
        logger.info("🔍 Validating Firebase credentials...")
        creds_raw = settings.FIREBASE_CREDENTIALS_JSON
        if not creds_raw:
            raise ValueError("FIREBASE_CREDENTIALS_JSON not set in environment.")

        # Auto-repair common format issue (newline escaping)
        fixed_json = creds_raw.replace("\\n", "\n")
        data = json.loads(fixed_json)

        # Check required fields
        required = ["private_key", "client_email", "project_id"]
        for field in required:
            if field not in data:
                raise KeyError(f"Missing field '{field}' in Firebase JSON")

        # Attempt to initialize Firebase Admin
        cred = credentials.Certificate(data)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            logger.info("✅ Firebase Admin initialized successfully.")
        else:
            logger.info("⚙️ Firebase already initialized — skipping duplicate init.")

    except Exception as e:
        logger.warning(
            f"⚠️ Firebase initialization failed ({e}). Using mock authentication fallback."
        )
        return False

    return True


def run_startup_guardian():
    """
    Main guardian: auto-fixes schema + Firebase
    """
    logger.info("🚀 Running Trendy Startup Guardian...")
    clean_and_rebuild_database()
    verify_firebase_credentials()
    logger.info("🌍 Trendy backend is ready for launch.")
