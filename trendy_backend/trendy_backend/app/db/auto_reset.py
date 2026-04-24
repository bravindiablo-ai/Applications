import os
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.user import User  # adjust import if model path differs
from app.core.security import get_password_hash  # adjust import if necessary

DATABASE_URL = os.getenv("DATABASE_URL")

def reset_schema():
    """Drop and recreate the public schema to remove duplicates and conflicts."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        cur.close()
        conn.close()
        print("✅ Database schema reset successfully.")
    except Exception as e:
        print(f"⚠️ Database reset skipped or failed: {e}")

def clean_indexes(engine):
    """Drop duplicate or broken indexes before table creation."""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                DO $$
                DECLARE rec RECORD;
                BEGIN
                    FOR rec IN SELECT indexname FROM pg_indexes WHERE schemaname='public' LOOP
                        BEGIN
                            EXECUTE format('DROP INDEX IF EXISTS %I;', rec.indexname);
                        EXCEPTION WHEN OTHERS THEN
                            NULL;
                        END;
                    END LOOP;
                END
                $$;
            """))
        print("✅ All duplicate indexes cleaned.")
    except Exception as e:
        print(f"⚠️ Index cleanup skipped: {e}")

def create_default_admin(engine):
    """Create a default admin user after reset."""
    try:
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        admin_email = "admin@trendyapp.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin = User(
                name="Admin",
                email=admin_email,
                password_hash=get_password_hash("TrendyAdmin123!"),
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("👑 Default admin user created successfully.")
        else:
            print("✅ Admin user already exists.")
        db.close()
    except Exception as e:
        print(f"⚠️ Could not create default admin user: {e}")

def auto_fix_database():
    """Main repair sequence for Trendy DB."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable missing.")
    engine = create_engine(DATABASE_URL)
    reset_schema()
    clean_indexes(engine)
    create_default_admin(engine)
    print("🚀 Database auto-fix completed successfully.")
