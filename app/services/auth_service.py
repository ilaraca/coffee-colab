from sqlalchemy.orm import Session
from typing import Optional
from app.repos import users_repo
from app.core.security import verify_password
from app.models.user import User

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = users_repo.get_user_by_email(self.db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
