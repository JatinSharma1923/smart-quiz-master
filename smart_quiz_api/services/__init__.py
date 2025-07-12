# smart_quiz_api/services/__init__.py
"""
Smart Quiz Master API - Services Integration Module

This module provides a unified interface to all services in the application.
It handles service initialization, dependency injection, and provides
type-safe access to all service components.
"""

from typing import Dict, Any
import logging

# Import all service modules
from .firebase import (
    initialize_firebase,
    simple_limiter
)

from .openai_service import (
    openai_client,
    call_openai,
    classify_topic,
    generate_explanation,
    generate_tags,
    grade_answer,
    estimate_confidence,
    get_cached_response,
    set_cached_response
)

from .scraper_services import (
    scrape_and_generate_quiz,
    generate_quiz_from_url,
    QuizType,
    fetch_article_html,
    is_valid_url,
    extract_clean_text,
    classify_topic as classify_topic_scraper,
    estimate_difficulty,
    get_cached_quiz,
    set_cached_quiz
)

from smart_quiz_api.config import settings

# Initialize logger
logger = logging.getLogger(__name__)

class ServiceManager:
    """
    Centralized service manager that handles initialization and provides
    access to all application services.
    """
    
    def __init__(self):
        self._initialized = False
        self._services: Dict[str, Any] = {}
        
    def initialize(self) -> None:
        """Initialize all services in the correct order."""
        if self._initialized:
            logger.warning("Services already initialized")
            return
        
        try:
            logger.info("🚀 Initializing Smart Quiz Master services...")
            
            # 1. Initialize Firebase (required for auth)
            logger.info("📱 Initializing Firebase services...")
            initialize_firebase()
            self._services['firebase'] = True
            
            # 2. Check OpenAI availability
            if settings.enable_ai_features:
                logger.info("🤖 OpenAI services enabled...")
                self._services['openai'] = True
            
            # 3. Initialize scraper services
            logger.info("🔍 Scraper services available...")
            self._services['scraper'] = True
            
            self._initialized = True
            logger.info("✅ All services initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {str(e)}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if services are initialized."""
        return self._initialized
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of all services."""
        return {
            'initialized': self._initialized,
            'services': list(self._services.keys()),
            'firebase_available': 'firebase' in self._services,
            'openai_available': 'openai' in self._services,
            'scraper_available': 'scraper' in self._services
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services."""
        health_status: Dict[str, Any] = {
            'overall': 'healthy',
            'services': {}
        }
        
        try:
            # Check Firebase
            if 'firebase' in self._services:
                health_status['services']['firebase'] = 'healthy'  # type: ignore
            else:
                health_status['services']['firebase'] = 'unavailable'  # type: ignore
                health_status['overall'] = 'degraded'
            
            # Check OpenAI
            if 'openai' in self._services:
                health_status['services']['openai'] = 'healthy'  # type: ignore
            else:
                health_status['services']['openai'] = 'disabled'  # type: ignore
            
            # Check Scraper services
            if 'scraper' in self._services:
                health_status['services']['scraper'] = 'healthy'  # type: ignore
            else:
                health_status['services']['scraper'] = 'unavailable'  # type: ignore
                health_status['overall'] = 'degraded'
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            health_status['overall'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status

# Global service manager instance
service_manager = ServiceManager()

def initialize_services() -> None:
    """Initialize all services."""
    service_manager.initialize()

def get_service_status() -> Dict[str, Any]:
    """Get the status of all services."""
    return service_manager.get_service_status()

def health_check() -> Dict[str, Any]:
    """Perform health check on all services."""
    return service_manager.health_check()

# Export all service functions for backward compatibility
__all__ = [
    # Firebase services
    'initialize_firebase',
    'simple_limiter',
    
    # OpenAI services
    'openai_client',
    'call_openai',
    'classify_topic',
    'generate_explanation',
    'generate_tags',
    'grade_answer',
    'estimate_confidence',
    'get_cached_response',
    'set_cached_response',
    
    # Scraper services
    'scrape_and_generate_quiz',
    'generate_quiz_from_url',
    'QuizType',
    'fetch_article_html',
    'is_valid_url',
    'extract_clean_text',
    'classify_topic_scraper',
    'estimate_difficulty',
    'get_cached_quiz',
    'set_cached_quiz',
    
    # Service management
    'service_manager',
    'initialize_services',
    'get_service_status',
    'health_check'
]
