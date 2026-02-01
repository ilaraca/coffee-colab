from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import AuthService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(email, password)
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email ou senha inválidos."
        }, status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Set session
    request.session["user_id"] = str(user.id)
    request.session["role"] = user.role.value
    request.session["name"] = user.name
    
    if user.role.value == "CAFE_ADMIN":
        return RedirectResponse(url="/cafe", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return RedirectResponse(url="/provider", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
