from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.repos import users_repo
import uuid

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return users_repo.get_user_by_id(db, uuid.UUID(user_id))

def get_current_active_user(user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

def get_cafe_admin(user = Depends(get_current_active_user)):
    if user.role.value != "CAFE_ADMIN":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires Cafe Admin")
    return user

def get_provider(user = Depends(get_current_active_user)):
    if user.role.value != "PROVIDER":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires Provider")
    return user
