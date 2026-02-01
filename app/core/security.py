from datetime import datetime, timedelta
from typing import Optional, Union, Any

from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    return serializer.dumps(data)

def verify_access_token(token: str, max_age: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60) -> Optional[dict]:
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except Exception:
        return None
