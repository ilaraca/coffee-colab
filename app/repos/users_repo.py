from sqlalchemy.orm import Session
import uuid
from app.models.user import User

from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()
