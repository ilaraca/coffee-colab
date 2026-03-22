from fastapi import APIRouter, Request, Depends, Form, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import AuthService
from app.services.email_service import send_verification_email
from app.core.tokens import confirm_verification_token
from app.repos import users_repo
from app.models.user import UserRole

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------------------------

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    error = request.session.pop("flash_error", None)
    unverified_email = request.session.pop("unverified_email", None)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error, "unverified_email": unverified_email},
    )


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(email, password)

    if not user:
        request.session["flash_error"] = "Email ou senha inválidos."
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Block unverified users
    if not user.email_verified:
        request.session["flash_error"] = "Você precisa verificar seu e-mail antes de entrar."
        request.session["unverified_email"] = user.email
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

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


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    error = request.session.pop("flash_error", None)
    return templates.TemplateResponse("register.html", {"request": request, "error": error})


@router.post("/register")
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        user_role = UserRole(role)
        auth_service.register_user(name=name, email=email, password=password, role=user_role)

        # Send verification email in the background (non-blocking)
        background_tasks.add_task(send_verification_email, email.lower())

        # Redirect to "check your email" page
        return RedirectResponse(
            url=f"/verify-email-sent?email={email.lower()}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except ValueError as e:
        request.session["flash_error"] = str(e)
        return RedirectResponse(url="/register", status_code=status.HTTP_303_SEE_OTHER)


# ---------------------------------------------------------------------------
# Email Verification
# ---------------------------------------------------------------------------

@router.get("/verify-email-sent", response_class=HTMLResponse)
async def verify_email_sent_page(request: Request, email: str = ""):
    return templates.TemplateResponse(
        "verify_email_sent.html",
        {"request": request, "email": email},
    )


@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email(request: Request, token: str = "", db: Session = Depends(get_db)):
    email = confirm_verification_token(token)

    if not email:
        return templates.TemplateResponse(
            "verify_email_sent.html",
            {
                "request": request,
                "email": "",
                "error": "Link inválido ou expirado. Solicite um novo e-mail de verificação.",
            },
        )

    user = users_repo.get_user_by_email(db, email)
    if not user:
        return templates.TemplateResponse(
            "verify_email_sent.html",
            {
                "request": request,
                "email": "",
                "error": "Usuário não encontrado.",
            },
        )

    if not user.email_verified:
        users_repo.verify_user_email(db, user)

    return templates.TemplateResponse(
        "verify_email_success.html",
        {"request": request},
    )


@router.post("/resend-verification")
async def resend_verification(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    """Resend verification email. Always shows success to avoid user enumeration."""
    user = users_repo.get_user_by_email(db, email.lower())

    if user and not user.email_verified:
        background_tasks.add_task(send_verification_email, email.lower())

    return RedirectResponse(
        url=f"/verify-email-sent?email={email.lower()}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
