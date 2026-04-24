import os
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.user import User  # adjust if your model paths differ
from app.core.security import get_password_hash  # ensure exists

# Import Config if it exists, otherwise create a simple one
try:
    from app.models.config import Config
except ImportError:
    class Config:
        def __init__(self, app_name, version, maintenance_mode):
            self.app_name = app_name
            self.version = version
            self.maintenance_mode = maintenance_mode

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL missing in environment variables.")

def reset_schema():
    """Drop and recreate schema if duplicate tables or indexes exist."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
        tables = cur.fetchall()
        if tables:
            print("⚠️ Existing tables detected. Resetting schema...")
            cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            print("✅ Schema reset complete.")
        else:
            print("🧩 Schema already clean.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Auto-reset skipped: {e}")

def clean_duplicate_indexes(engine):
    """Drop any duplicate indexes that cause SQLAlchemy errors."""
    try:
        print("🔍 Cleaning duplicate indexes...")
        with engine.connect() as conn:
            conn.execute(text("""
                DO $$
                DECLARE rec RECORD;
                BEGIN
                    FOR rec IN SELECT indexname FROM pg_indexes WHERE schemaname='public' LOOP
                        BEGIN
                            EXECUTE format('DROP INDEX IF EXISTS %I;', rec.indexname);
                        EXCEPTION WHEN OTHERS THEN NULL;
                        END;
                    END LOOP;
                END
                $$;
            """))
        print("✅ Index cleanup complete.")
    except Exception as e:
        print(f"⚠️ Could not clean indexes: {e}")

def seed_initial_data(SessionLocal):
    """Seed default admin account and app configuration."""
    print("🌱 Seeding default data...")
    try:
        db = SessionLocal()

        # Seed default admin user
        admin = db.query(User).filter_by(email="admin@trendyapp.com").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@trendyapp.com",
                hashed_password=get_password_hash("Trendy@2025"),
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            print("✅ Admin user created (admin@trendyapp.com / Trendy@2025).")

        # Seed default app config
        config = db.query(Config).first()
        if not config:
            config = Config(
                app_name="Trendy",
                version="1.0",
                maintenance_mode=False
            )
            db.add(config)
            print("✅ Default configuration added.")

        db.commit()
        db.close()
        print("🌱 Data seeding complete.")
    except Exception as e:
        print(f"⚠️ Data seeding failed: {e}")

def repair_all():
    """Main recovery entry point."""
    print("🚀 Starting Trendy backend auto-repair...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    reset_schema()
    clean_duplicate_indexes(engine)
    seed_initial_data(SessionLocal)

    print("✅ Auto-repair finished successfully. Trendy is ready.")
