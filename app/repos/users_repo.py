from sqlalchemy.orm import Session
import uuid
from app.models.user import User

from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def link_cafe_to_user(db: Session, user: User, cafe_id: uuid.UUID) -> User:
    user.cafe_id = cafe_id
    db.commit()
    db.refresh(user)
    return user

def verify_user_email(db: Session, user: User) -> User:
    user.email_verified = True
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, user: User, new_password_hash: str) -> User:
    user.password_hash = new_password_hash
    db.commit()
    db.refresh(user)
    return user

