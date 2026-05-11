from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.web import routes_auth
import sentry_sdk

# Explicitly import models to ensure persistence/metadata awareness

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )

app = FastAPI(title="Modo Colab")

# Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Routes
app.include_router(routes_auth.router)
from app.web import routes_business, routes_provider  # noqa: E402
app.include_router(routes_business.router)
app.include_router(routes_provider.router)
from app.web import routes_wallet, routes_redeem, routes_portfolio  # noqa: E402
app.include_router(routes_wallet.router)
app.include_router(routes_redeem.router)
app.include_router(routes_portfolio.router)

templates = Jinja2Templates(directory="app/templates")

from starlette.exceptions import HTTPException as StarletteHTTPException  # noqa: E402
from fastapi.responses import HTMLResponse  # noqa: E402

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)
    if exc.status_code == 500:
        return templates.TemplateResponse("errors/500.html", {"request": request}, status_code=500)
    return HTMLResponse(content=f"Error {exc.status_code}: {exc.detail}", status_code=exc.status_code)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return templates.TemplateResponse("errors/500.html", {"request": request}, status_code=500)

@app.get("/")
async def home(request: Request):
    from app.core.db import SessionLocal
    from app.models.user import User
    from app.models.mission import Mission, MissionStatus
    from app.models.business import Business

    db = SessionLocal()
    try:
        user = None
        user_id = request.session.get("user_id")
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()

        missions = (
            db.query(Mission)
            .join(Mission.business)
            .filter(Mission.status == MissionStatus.OPEN)
            .filter(Business.is_verified)
            .order_by(Mission.created_at.desc())
            .limit(6)
            .all()
        )
    finally:
        db.close()

    return templates.TemplateResponse(
        "landing.html",
        {"request": request, "user": user, "missions": missions},
    )

