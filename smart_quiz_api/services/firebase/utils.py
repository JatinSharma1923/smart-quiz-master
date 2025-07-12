# smart_quiz_api/services/firebase/utils.py

import logging
from typing import Dict, Any
from fastapi import HTTPException, status
from firebase_admin import auth  # type: ignore

# === Logger Setup ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === Token Extractor ===
def extract_token_from_header(auth_header: str) -> str:
    """
    Extracts the bearer token from the Authorization header.
    Raises 401 if header is missing or malformed.
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or malformed Authorization header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )
    
    parts = auth_header.split(" ")
    if len(parts) != 2:
        logger.warning("Invalid Authorization header format.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
        )
    
    return parts[1]

# === Firebase Token Verifier ===
def verify_firebase_token(token: str) -> Dict[str, Any]:
    """
    Verifies the Firebase ID token using Firebase Admin SDK.
    Returns the decoded token if valid.
    Raises 401 on failure.
    """
    try:
        decoded_token = auth.verify_id_token(token)  # type: ignore
        uid = decoded_token.get("uid")  # type: ignore
        if not uid:
            logger.warning("Firebase token does not contain a UID.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token: UID missing",
            )
        logger.info(f"✅ Firebase token verified for UID: {uid}")
        return decoded_token  # type: ignore
    except Exception as e:
        logger.error(f"❌ Firebase token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token verification failed",
        )
