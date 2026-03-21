from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.web import routes_auth
import sentry_sdk

# Explicitly import models to ensure persistence/metadata awareness

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )

app = FastAPI(title="Coffee Co-lab")

# Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static") 


# Routes
app.include_router(routes_auth.router)
from app.web import routes_cafe, routes_provider  # noqa: E402
app.include_router(routes_cafe.router)
app.include_router(routes_provider.router)
from app.web import routes_wallet, routes_redeem, routes_portfolio  # noqa: E402
app.include_router(routes_wallet.router)
app.include_router(routes_redeem.router)
app.include_router(routes_portfolio.router)

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home(request: Request):
    user = None
    user_id = request.session.get("user_id")
    if user_id:
        from app.core.db import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    return templates.TemplateResponse(
        "landing.html", {"request": request, "user": user}
    )
