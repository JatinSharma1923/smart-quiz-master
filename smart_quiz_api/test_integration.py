#!/usr/bin/env python3
"""
Smart Quiz Master API - Integration Test Suite

This script tests the integration of all components to ensure they work together properly.
Run this script to verify that the entire system is functioning correctly.
"""

import sys
import os
import logging
from typing import List, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smart_quiz_api.config import settings

def test_required_env_vars():
    required_vars = [
        'app_name',
        'app_version',
        'environment',
        'database_url',
        'db_pool_size',
        'enable_ai_features',
        'enable_websockets',
        'enable_caching',
        'enable_rate_limiting',
        'openai_api_key',
        'admin_api_key',
        'redis_url',
        'firebase_cred_path',
        'scraper_model',
        'google_application_credentials',
    ]
    missing: list[str] = []
    for var in required_vars:
        if getattr(settings, var, None) in (None, ""):
            missing.append(var)
    assert not missing, f"Missing required env variables: {missing}"

def test_configuration():
    """Test configuration loading and validation."""
    print("🔧 Testing configuration...")
    
    try:
        
        # Test basic configuration
        assert settings.app_name == "Smart Quiz Master API"
        assert settings.app_version == "2.0.0"
        assert settings.environment in ["development", "staging", "production"]
        
        # Test database configuration
        assert settings.database_url is not None
        assert settings.db_pool_size > 0
        
        # Test Redis configuration
        assert settings.redis_url is not None
        
        # Test feature flags
        assert isinstance(settings.enable_ai_features, bool)
        assert isinstance(settings.enable_websockets, bool)
        assert isinstance(settings.enable_caching, bool)
        assert isinstance(settings.enable_rate_limiting, bool)
        
        print("✅ Configuration test passed")
        assert True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        assert False

def test_cors_config():
    print('CORS Allowed Origins:', settings.cors_allowed_origins)
    print('CORS Allowed Methods:', settings.cors_allowed_methods)
    print('CORS Allowed Headers:', settings.cors_allowed_headers)
    print('CORS Allow Credentials:', settings.cors_allow_credentials)
    assert isinstance(settings.cors_allowed_origins, list)
    assert isinstance(settings.cors_allowed_methods, list)
    assert isinstance(settings.cors_allowed_headers, list)
    assert isinstance(settings.cors_allow_credentials, bool)
    print('✅ CORS config test passed')
    assert True

def test_database_connection():
    """Test database connection and basic operations."""
    print("🗄️ Testing database connection...")
    
    try:
        from smart_quiz_api.database import engine, SessionLocal
        
        # Test engine creation
        assert engine is not None
        
        # Test session creation
        with SessionLocal() as db:
            # Test basic query
            from sqlalchemy import text
            result = db.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        print("✅ Database test passed")
        assert True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        assert False

def test_firebase_services():
    """Test Firebase service initialization."""
    print("📱 Testing Firebase services...")
    
    try:
        from smart_quiz_api.services.firebase import initialize_firebase, simple_limiter
        
        # Test initialization
        initialize_firebase()
        
        # Test rate limiter
        assert simple_limiter is not None
        assert hasattr(simple_limiter, 'allow_request')
        
        print("✅ Firebase services test passed")
        assert True
        
    except Exception as e:
        print(f"❌ Firebase services test failed: {str(e)}")
        assert False

def test_openai_services():
    """Test OpenAI service availability."""
    print("🤖 Testing OpenAI services...")
    
    try:
        from smart_quiz_api.services.openai_service import openai_client, call_openai
        
        # Test client availability
        assert openai_client is not None
        
        # Test basic functions
        assert callable(call_openai)
        
        print("✅ OpenAI services test passed")
        assert True
        
    except Exception as e:
        print(f"❌ OpenAI services test failed: {str(e)}")
        assert False

def test_scraper_services():
    """Test scraper service availability."""
    print("🔍 Testing scraper services...")
    
    try:
        from smart_quiz_api.services.scraper_services import (
            scrape_and_generate_quiz,
            generate_quiz_from_url,
            QuizType
        )
        
        # Test function availability
        assert callable(scrape_and_generate_quiz)
        assert callable(generate_quiz_from_url)
        
        # Test QuizType options
        assert 'MCQ' in QuizType.__args__
        assert 'TF' in QuizType.__args__ or 'TRUE_FALSE' in QuizType.__args__
        assert 'IMAGE' in QuizType.__args__
        print(f"✅ Scraper services test passed: QuizType options are {QuizType.__args__}")
        assert True
        
    except Exception as e:
        print(f"❌ Scraper services test failed: {str(e)}")
        assert False

def test_service_manager():
    """Test service manager integration."""
    print("⚙️ Testing service manager...")
    
    try:
        from smart_quiz_api.services import (
            service_manager,
            initialize_services,
            get_service_status,
            health_check
        )
        
        # Test service manager
        assert service_manager is not None
        assert hasattr(service_manager, 'initialize')
        assert hasattr(service_manager, 'health_check')
        
        # Test initialization
        initialize_services()
        
        # Test status
        status = get_service_status()
        assert isinstance(status, dict)
        assert 'initialized' in status
        
        # Test health check
        health = health_check()
        assert isinstance(health, dict)
        assert 'overall' in health
        assert 'services' in health
        
        print("✅ Service manager test passed")
        assert True
        
    except Exception as e:
        print(f"❌ Service manager test failed: {str(e)}")
        assert False

def test_models():
    """Test database models."""
    print("📊 Testing database models...")
    
    try:
        from smart_quiz_api.models import (
            User,
            Quiz
        )
        
        # Test model imports
        assert User is not None
        assert Quiz is not None
        
        print("✅ Database models test passed")
        assert True
        
    except Exception as e:
        print(f"❌ Database models test failed: {str(e)}")
        assert False

def test_routers():
    """Test router imports."""
    print("🛣️ Testing routers...")
    
    try:
        from smart_quiz_api.routers import quiz_router, user_router, admin_router
        
        # Test router imports
        assert quiz_router is not None
        assert user_router is not None
        assert admin_router is not None
        
        print("✅ Routers test passed")
        assert True
        
    except Exception as e:
        print(f"❌ Routers test failed: {str(e)}")
        assert False

def test_utils():
    """Test utility functions."""
    print("🔧 Testing utilities...")
    
    try:
        from smart_quiz_api.utils import (
            log_auth_attempt
        )
        
        # Test utility imports
        assert callable(log_auth_attempt)
        
        print("✅ Utilities test passed")
        assert True
        
    except Exception as e:
        print(f"❌ Utilities test failed: {str(e)}")
        assert False

def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Starting Smart Quiz Master API Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("Firebase Services", test_firebase_services),
        ("OpenAI Services", test_openai_services),
        ("Scraper Services", test_scraper_services),
        ("Service Manager", test_service_manager),
        ("Database Models", test_models),
        ("Routers", test_routers),
        ("Utilities", test_utils),
    ]
    
    results: List[Tuple[str, bool]] = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
        else:
            results.append((test_name, True))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! The system is ready.")
        assert True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        assert False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Run tests
    success = run_integration_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 