from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import AuthService
from app.models.user import UserRole

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

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    
    try:
        user_role = UserRole(role)
        new_user = auth_service.register_user(name=name, email=email, password=password, role=user_role)
        
        # Log the user in
        request.session["user_id"] = str(new_user.id)
        request.session["role"] = new_user.role.value
        request.session["name"] = new_user.name
        
        if new_user.role.value == "CAFE_ADMIN":
            return RedirectResponse(url="/cafe", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return RedirectResponse(url="/provider", status_code=status.HTTP_303_SEE_OTHER)
            
    except ValueError as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e)
        }, status_code=status.HTTP_400_BAD_REQUEST)

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
