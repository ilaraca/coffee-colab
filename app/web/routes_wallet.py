from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.web.deps import get_provider
from app.services.redeem_service import RedeemService
from app.repos import wallet_repo

router = APIRouter(prefix="/wallet")
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def wallet_view(
    request: Request,
    user = Depends(get_provider),
    db: Session = Depends(get_db)
):
    grouped_wallets = wallet_repo.build_provider_grouped_wallets(db, user.id)

    return templates.TemplateResponse(request, "wallet.html", {
        "user": user,
        "grouped_wallets": grouped_wallets,
    })

@router.get("/token")
async def token_redirect():
    return RedirectResponse("/provider?tab=wallet")

@router.post("/token")
async def generate_token(
    request: Request,
    business_id: str = Form(...),
    amount: int = Form(...),
    user = Depends(get_provider),
    db: Session = Depends(get_db)
):
    import uuid
    from app.repos import businesses_repo

    try:
        b_id = uuid.UUID(business_id)
        business = businesses_repo.get_business_by_id(db, b_id)
    except ValueError:
        business = None

    if not business:
        raise HTTPException(400, "Business not found")

    service = RedeemService(db)

    try:
        raw_token, token_obj = service.generate_token(user.id, business.id, amount)
        qr_url = service.generate_qr_image(f"{request.base_url}redeem/{raw_token}")

        return templates.TemplateResponse(request, "provider_dashboard.html", {
            "user": user,
            "tab": "wallet",
            "grouped_wallets": wallet_repo.build_provider_grouped_wallets(db, user.id),
            "new_qr": qr_url,
            "new_token_expiry": token_obj.expires_at,
            "redeem_link": f"{request.base_url}business/redeem/{raw_token}",
            "raw_token": raw_token,
        })

    except HTTPException as e:
        return templates.TemplateResponse(request, "provider_dashboard.html", {
            "user": user,
            "tab": "wallet",
            "grouped_wallets": wallet_repo.build_provider_grouped_wallets(db, user.id),
            "error": e.detail,
        })
