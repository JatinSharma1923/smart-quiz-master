# smart_quiz_api/services/firebase/health.py
import os
import firebase_admin  # type: ignore
from firebase_admin import credentials  # type: ignore
from typing import Any, Dict
from smart_quiz_api.config import settings

def check_firebase_health() -> Dict[str, Any]:
    """
    Check Firebase health and return status information.
    """
    try:
        # Try to get existing app first
        try:
            app = firebase_admin.get_app()  # type: ignore
            return {"status": "healthy", "firebase_app": app.name}
        except ValueError:
            # App doesn't exist, try to initialize it
            return _initialize_firebase_app()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def _initialize_firebase_app() -> Dict[str, Any]:
    """
    Initialize Firebase app with available credentials.
    """
    try:
        # Check for service account file
        service_account_path = settings.google_application_credentials or None
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)  # type: ignore
            app = firebase_admin.initialize_app(cred)  # type: ignore
            return {"status": "healthy", "firebase_app": app.name, "method": "service_account"}
        
        # Check for default credentials (useful in cloud environments)
        try:
            cred = credentials.ApplicationDefault()  # type: ignore
            app = firebase_admin.initialize_app(cred)  # type: ignore
            return {"status": "healthy", "firebase_app": app.name, "method": "application_default"}
        except Exception:
            pass
        
        # If no credentials found, return unhealthy status
        return {
            "status": "unhealthy", 
            "error": "No Firebase credentials found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable or use Application Default Credentials."
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": f"Failed to initialize Firebase: {str(e)}"}