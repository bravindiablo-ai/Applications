#!/usr/bin/env python3
"""
Production validation script for pre-deployment checks.
Validates environment variables, database connectivity, and service dependencies.
"""
import os
import sys
import subprocess
import requests
from pathlib import Path

def check_environment_variables():
    """Validate required environment variables are set."""
    print("🔍 Checking environment variables...")

    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLIC_KEY",
        "FIREBASE_PROJECT_ID",
        "AGORA_APP_ID",
        "AGORA_APP_CERTIFICATE"
    ]

    optional_vars = [
        "REDIS_URL",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "ADMOB_APP_ID_ANDROID",
        "ADMOB_APP_ID_IOS"
    ]

    missing_required = []
    missing_optional = []

    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)

    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)

    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        return False

    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {missing_optional}")

    print("✅ Environment variables validated")
    return True

def check_database_connectivity():
    """Test database connection."""
    print("🔍 Checking database connectivity...")

    try:
        from app.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database query failed")
                return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_redis_connectivity():
    """Test Redis connection if configured."""
    print("🔍 Checking Redis connectivity...")

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("⚠️  Redis URL not configured, skipping Redis check")
        return True

    try:
        from app.services.redis_client import get_redis_client
        redis_client = get_redis_client()
        redis_client.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def check_external_services():
    """Test external service connectivity."""
    print("🔍 Checking external services...")

    services_ok = True

    # Test Stripe API
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    if stripe_key:
        try:
            import stripe
            stripe.api_key = stripe_key
            # Test with a simple API call (list customers with limit 1)
            stripe.Customer.list(limit=1)
            print("✅ Stripe API connection successful")
        except Exception as e:
            print(f"❌ Stripe API connection failed: {e}")
            services_ok = False
    else:
        print("⚠️  Stripe key not configured")

    # Test Firebase (basic check)
    firebase_project = os.getenv("FIREBASE_PROJECT_ID")
    if firebase_project:
        print("✅ Firebase project configured")
    else:
        print("⚠️  Firebase project not configured")

    return services_ok

def check_application_imports():
    """Test that all application modules can be imported."""
    print("🔍 Checking application imports...")

    modules_to_test = [
        "app.main",
        "app.database",
        "app.services.redis_client",
        "app.services.stripe_service",
        "app.services.firebase_service",
        "app.routes.health",
        "app.routes.user",
        "app.routes.posts"
    ]

    failed_imports = []

    for module in modules_to_test:
        try:
            __import__(module)
        except ImportError as e:
            failed_imports.append(f"{module}: {e}")

    if failed_imports:
        print(f"❌ Failed imports: {failed_imports}")
        return False

    print("✅ All application imports successful")
    return True

def check_file_permissions():
    """Check critical file permissions."""
    print("🔍 Checking file permissions...")

    critical_files = [
        "app/main.py",
        "requirements.txt",
        "Dockerfile"
    ]

    permissions_ok = True

    for file_path in critical_files:
        if os.path.exists(file_path):
            if not os.access(file_path, os.R_OK):
                print(f"❌ Cannot read: {file_path}")
                permissions_ok = False
        else:
            print(f"⚠️  File not found: {file_path}")

    if permissions_ok:
        print("✅ File permissions OK")

    return permissions_ok

def run_health_checks():
    """Run health check endpoints."""
    print("🔍 Running health checks...")

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

    endpoints = [
        "/health",
        "/health/detailed"
    ]

    health_ok = True

    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Health check passed: {endpoint}")
            else:
                print(f"❌ Health check failed: {endpoint} (status: {response.status_code})")
                health_ok = False
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Health check unreachable: {endpoint} ({e})")

    return health_ok

def main():
    """Run all production validation checks."""
    print("🚀 Starting production validation checks...\n")

    checks = [
        ("Environment Variables", check_environment_variables),
        ("Database Connectivity", check_database_connectivity),
        ("Redis Connectivity", check_redis_connectivity),
        ("External Services", check_external_services),
        ("Application Imports", check_application_imports),
        ("File Permissions", check_file_permissions),
        ("Health Checks", run_health_checks)
    ]

    results = []

    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
            print()
        except Exception as e:
            print(f"❌ {check_name} check failed with exception: {e}\n")
            results.append((check_name, False))

    # Summary
    print("=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)

    all_passed = True
    for check_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 ALL VALIDATION CHECKS PASSED")
        print("✅ Ready for production deployment")
        return 0
    else:
        print("❌ SOME VALIDATION CHECKS FAILED")
        print("🔧 Please fix the issues before deploying to production")
        return 1

if __name__ == "__main__":
    sys.exit(main())
