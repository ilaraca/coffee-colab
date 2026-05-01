"""
Token generation and validation for email verification.
Uses itsdangerous (already installed via SessionMiddleware dependency).
"""
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from typing import Optional
from app.core.config import settings

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
_SALT = "email-verification"


def generate_verification_token(email: str) -> str:
    """Generate a signed, time-limited token for email verification."""
    return _serializer.dumps(email, salt=_SALT)



def confirm_verification_token(token: str, expiration: int = 86400) -> Optional[str]:
    """
    Validate a verification token.
    Returns the email address if valid, or None if expired/invalid.
    expiration: seconds (default 86400 = 24h)
    """
    try:
        email = _serializer.loads(token, salt=_SALT, max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None

_RESET_SALT = "password-reset"

def generate_password_reset_token(email: str) -> str:
    """Generate a signed, time-limited token for password reset."""
    return _serializer.dumps(email, salt=_RESET_SALT)

def confirm_password_reset_token(token: str, expiration: int = 7200) -> Optional[str]:
    """
    Validate a password reset token.
    Returns the email address if valid, or None if expired/invalid.
    expiration: seconds (default 7200 = 2h)
    """
    try:
        email = _serializer.loads(token, salt=_RESET_SALT, max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None

