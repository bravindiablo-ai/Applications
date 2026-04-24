from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.redis_client import get_redis_client
import psutil
import time
import os
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/healthz")
def healthz():
    """Basic health check for load balancers."""
    return {"status": "ok"}

@router.get("/health")
def health():
    """Standard health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
def detailed_health(db: Session = Depends(get_db)):
    """Detailed health check with service status and metrics."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": time.time() - psutil.boot_time(),
        "services": {},
        "metrics": {}
    }

    # Database health check
    try:
        db.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Redis health check
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # System metrics
    health_status["metrics"] = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "process_count": len(psutil.pids())
    }

    # Environment validation
    required_env_vars = [
        "DATABASE_URL", "SECRET_KEY", "STRIPE_SECRET_KEY",
        "FIREBASE_PROJECT_ID", "AGORA_APP_ID"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        health_status["services"]["environment"] = f"missing: {missing_vars}"
        health_status["status"] = "degraded"
    else:
        health_status["services"]["environment"] = "healthy"

    return health_status

@router.get("/status")
def status():
    """Legacy status endpoint for backward compatibility."""
    return {
        "status": "ok",
        "services": ["db", "redis", "trends", "personalization"],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
def metrics():
    """Prometheus-style metrics endpoint."""
    metrics_data = {
        "cpu_usage_percent": psutil.cpu_percent(),
        "memory_usage_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "uptime_seconds": time.time() - psutil.boot_time(),
        "active_connections": 0,  # Would need to track this
        "request_count": 0,  # Would need middleware to track
        "error_count": 0  # Would need error tracking
    }

    # Format as Prometheus metrics
    prometheus_output = ""
    for key, value in metrics_data.items():
        prometheus_output += f"trendy_backend_{key} {value}\n"

    return prometheus_output

@router.get("/welcome")
def welcome(request: Request):
    """
    Returns a welcome message and logs request metadata.
    """
    logger.info(f"Request received: {request.method} {request.url.path}")
    return {"message": "Welcome to the TRENDY API Service!"}
