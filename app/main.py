from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.web import routes_auth
import sentry_sdk

# Explicitly import models to ensure persistence/metadata awareness
from app.models import cafe, user, mission, rating, transaction, redeem, portfolio

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
from app.web import routes_cafe, routes_provider
app.include_router(routes_cafe.router)
app.include_router(routes_provider.router)
from app.web import routes_wallet, routes_redeem, routes_portfolio
app.include_router(routes_wallet.router)
app.include_router(routes_redeem.router)
app.include_router(routes_portfolio.router)

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home(request: Request):
    user_id = request.session.get("user_id")
    # If logged in, maybe still show landing but with "Dashboard" button?
    # Or redirect to Dashboard? 
    # Usually Landing Page is for non-logged users.
    if user_id:
        role = request.session.get("role")
        target = "/cafe" if role == "CAFE_ADMIN" else "/provider"
        return RedirectResponse(target)
    
    return templates.TemplateResponse("landing.html", {"request": request})

# Placeholder for dashboards to prevent 404 during incremental build
@app.get("/cafe")
async def cafe_dashboard():
    return "Cafe Dashboard (Coming Soon)"

@app.get("/provider")
async def provider_dashboard():
    return "Provider Dashboard (Coming Soon)"
