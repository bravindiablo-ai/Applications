"""
Comprehensive test script to validate all backend services.
"""
import asyncio
import pytest
from typing import Dict, Any
from app.core.security import SecurityService
from app.services.cache_service import CacheService
from app.services.moderation_service import ModerationService
from app.services.hybrid_feed_engine import HybridFeedEngine
from app.models.content import ContentType
from app.core.config import get_settings

@pytest.mark.asyncio
async def test_security_service():
    """Test security service functionality."""
    security = SecurityService()
    
    # Test password hashing
    password = "test_password123"
    hashed = security.hash_password(password)
    assert security.verify_password(password, hashed)
    print("✅ Password hashing works")
    
    # Test JWT tokens
    user_data = {"user_id": "123", "role": "user"}
    token = security.create_access_token(user_data)
    decoded = security.verify_token(token)
    assert decoded["user_id"] == user_data["user_id"]
    print("✅ JWT token creation and verification works")
    
    # Test encryption
    sensitive_data = "sensitive information"
    encrypted = security.encrypt_data(sensitive_data)
    decrypted = security.decrypt_data(encrypted)
    assert decrypted == sensitive_data
    print("✅ Data encryption works")

@pytest.mark.asyncio
async def test_cache_service():
    """Test Redis caching functionality."""
    cache = CacheService()
    
    # Test basic cache operations
    await cache.set("test_key", {"data": "test"})
    value = await cache.get("test_key")
    assert value["data"] == "test"
    print("✅ Redis cache operations work")
    
    # Test trending cache
    trending_items = [{"id": "1", "title": "Test"}]
    await cache.cache_trending(trending_items)
    cached_trending = await cache.get_trending()
    assert cached_trending == trending_items
    print("✅ Trending cache works")

@pytest.mark.asyncio
async def test_moderation_service():
    """Test AI moderation functionality."""
    moderation = ModerationService()
    
    # Test clean content
    clean_content = "This is a family-friendly post"
    is_allowed, scores = await moderation.moderate_content(
        clean_content,
        ContentType.POST
    )
    assert is_allowed
    print("✅ Clean content moderation works")
    
    # Test problematic content
    bad_content = "This contains hate speech and violence"
    is_allowed, scores = await moderation.moderate_content(
        bad_content,
        ContentType.POST
    )
    assert not is_allowed
    print("✅ Problematic content detection works")

@pytest.mark.asyncio
async def test_feed_engine():
    """Test hybrid feed engine functionality."""
    engine = HybridFeedEngine()
    
    # Test discover feed
    discover = await engine.get_discover_feed("test_user")
    assert isinstance(discover, list)
    print("✅ Discover feed generation works")
    
    # Test personalized feed
    personalized = await engine.get_personalized_feed("test_user")
    assert isinstance(personalized, list)
    print("✅ Personalized feed generation works")
    
    # Test trending feed
    trending = await engine.get_trending_feed("test_user")
    assert isinstance(trending, list)
    print("✅ Trending feed generation works")

async def run_all_tests():
    """Run all backend service tests."""
    try:
        print("\n🔒 Testing Security Service...")
        await test_security_service()
        
        print("\n📦 Testing Cache Service...")
        await test_cache_service()
        
        print("\n🛡️ Testing Moderation Service...")
        await test_moderation_service()
        
        print("\n🔄 Testing Feed Engine...")
        await test_feed_engine()
        
        print("\n✅ All backend services are working correctly!")
        
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(run_all_tests())