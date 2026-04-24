"""
Main FastAPI application for TRENDY App
Complete implementation with all enhanced features
Deploy: Fixed database migration for Render - v1.1
"""
import logging
import sys
import os
# Configure logging for clearer Render output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .utils.startup_guardian import run_startup_guardian
# from .db.auto_repair import repair_all
# from .db.auto_reset import auto_fix_database
# from .auth.middleware import AuthMiddleware
from .routes import (
    agora,
    auth,
    followers_new,
    user_relationships,
    enhanced_content,
    monetization,
    ads,
    revenue_analytics,
    ai_assistant,
    rooms,
    chat_ws,
    analytics_dash,
    stripe_webhooks,
    health,
    posts,
    notifications,
    user,
    external_apis
)
from .auth import email_verification
from .routes import social_auth
# from .ws import watch_party_ws # Not found
# Auto-fix DB + Firebase issues at startup
run_startup_guardian()
# repair_all()
# auto_fix_database()

# Initialize Firebase
from .services.firebase_service import initialize_firebase
initialize_firebase()
# Initialize default CORS origins
# Initialize CORS origins from environment or defaults
CORS_ORIGINS_STR = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STR.split(",")]

# Remove wildcard in production
if "*" in CORS_ORIGINS and os.getenv("APP_ENV") == "production":
    logger.warning("Removing wildcard CORS in production")
    CORS_ORIGINS.remove("*")
    if not CORS_ORIGINS:
        CORS_ORIGINS = ["https://yourdomain.com"]
# Create FastAPI app
app = FastAPI(
    title="TRENDY API",
    description="TRENDY App Backend API",
    version="1.0.0"
)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# Add authentication middleware
# app.add_middleware(AuthMiddleware)
Base.metadata.create_all(bind=engine)
# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(agora.router, prefix="/api/agora", tags=["Agora"])
app.include_router(followers_new.router, prefix="/api/followers", tags=["Followers"])
app.include_router(user_relationships.router, prefix="/api/relationships", tags=["Relationships"])
app.include_router(enhanced_content.router, prefix="/api/content", tags=["Enhanced Content"])
app.include_router(ai_assistant.router, prefix="/api/ai", tags=["AI Assistant"])
app.include_router(monetization.router, prefix="/api/monetization", tags=["Monetization"])
app.include_router(ads.router, prefix="/api/ads", tags=["Ads"])
app.include_router(revenue_analytics.router, prefix="/api/revenue", tags=["Revenue Analytics"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["Rooms"])
app.include_router(chat_ws.router, prefix="/api/chat", tags=["Chat"])
app.include_router(analytics_dash.router, prefix="/api/analytics", tags=["Analytics Dashboard"])
app.include_router(stripe_webhooks.router, prefix="/api/webhooks", tags=["Stripe Webhooks"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
# app.include_router(watch_party_ws.router, prefix="/api/watch-party", tags=["Watch Party"])
app.include_router(email_verification.router, prefix="/api/email", tags=["Email Verification"])
app.include_router(social_auth.router, prefix="/api/social", tags=["Social Auth"])
app.include_router(posts.router, prefix="/api", tags=["Posts"])
app.include_router(notifications.router, prefix="/api", tags=["Notifications"])
app.include_router(user.router, prefix="/api", tags=["Users"])
app.include_router(external_apis.router, prefix="/api/external", tags=["External APIs"])

# Mount static files
# Mount static files if directory exists
static_dir = os.path.join(os.path.dirname(__file__), "../static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification"""
    return {"status": "healthy", "service": "TRENDY API"}
# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {
        "service": "TRENDY API",
        "version": "1.0.0",
        "status": "running"
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
