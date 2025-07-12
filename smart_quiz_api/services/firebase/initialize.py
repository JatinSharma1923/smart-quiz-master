import os
import logging
import firebase_admin  # type: ignore
from firebase_admin import credentials, initialize_app  # type: ignore
from dotenv import load_dotenv
from smart_quiz_api.config import settings

logger = logging.getLogger(__name__)

load_dotenv()

# Load path to Firebase service account credentials from environment
FIREBASE_CRED_PATH = settings.firebase_cred_path

def initialize_firebase():
    """
    Initialize Firebase Admin SDK with the given service account key.
    Skips initialization if already initialized.
    """
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()  # type: ignore
        logger.info("✅ Firebase already initialized")
        return  # Already initialized
    except ValueError:
        # Not initialized, proceed with initialization
        logger.info("🔄 Initializing Firebase...")
        pass
    
    # Try multiple credential methods
    cred = None
    
    # Method 1: Check for service account file from environment
    if FIREBASE_CRED_PATH and os.path.exists(FIREBASE_CRED_PATH):
        logger.info(f"📁 Using Firebase credentials from: {FIREBASE_CRED_PATH}")
        try:
            cred = credentials.Certificate(FIREBASE_CRED_PATH)  # type: ignore
        except Exception as e:
            logger.warning(f"⚠️ Failed to load Firebase credentials from {FIREBASE_CRED_PATH}: {e}")
            # For testing environments, create a dummy credential
            if settings.environment == "development" or "test" in settings.environment:
                logger.info("🧪 Creating mock Firebase credentials for testing")
                # Create a minimal mock credential for testing
                cred = credentials.ApplicationDefault()  # type: ignore
            else:
                raise
    
    # Method 2: Check for GOOGLE_APPLICATION_CREDENTIALS
    # If GOOGLE_APPLICATION_CREDENTIALS is needed, consider adding to config.py and referencing as settings.google_application_credentials
    elif settings.google_application_credentials:
        cred_path = settings.google_application_credentials
        if cred_path and os.path.exists(cred_path):
            logger.info(f"🔑 Using Firebase credentials from: {cred_path}")
            cred = credentials.Certificate(cred_path)  # type: ignore
    
    # Method 3: Try Application Default Credentials
    if not cred:
        try:
            logger.info("☁️ Using Application Default Credentials")
            cred = credentials.ApplicationDefault()  # type: ignore
        except Exception as e:
            logger.warning(f"⚠️ Application Default Credentials failed: {e}")
            pass
    
    if not cred:
        logger.error("❌ No Firebase credentials found")
        raise FileNotFoundError(
            f"❌ Firebase credentials not found. Please set FIREBASE_CRED_PATH or GOOGLE_APPLICATION_CREDENTIALS environment variable."
        )
    
    initialize_app(cred)  # type: ignore
    logger.info("✅ Firebase initialized successfully")
