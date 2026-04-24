import sys, traceback
from app.database import engine, SessionLocal
from app.database import get_db
print("=== Verify DB connect ===")
try:
    db = SessionLocal()
    from sqlalchemy import text
    res = db.execute(text("SELECT 1"))
    print("DB OK", res.scalar())
except Exception as e:
    print("DB ERROR", e)
finally:
    try:
        db.close()
    except Exception:
        pass

print("=== Verify imports ===")
try:
    import app.services.hybrid_feed as hf
    import app.services.moderation_engine as mod
    # Check for redis fallback in redis_client
    try:
        from app.services import redis_client
        fallback_used = getattr(redis_client, '_FALLBACK', None) is not None and 'redis' not in globals()
        if fallback_used:
            print("Imports OK (note: in-memory Redis fallback will be used — install 'redis' package for full functionality)")
        else:
            print("Imports OK")
    except Exception:
        print("Imports OK")
except Exception as e:
    print("Import ERROR")
    traceback.print_exc()
