from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.web.deps import get_business_admin
from app.services.redeem_service import RedeemService
from app.repos import users_repo

router = APIRouter(prefix="/redeem")
templates = Jinja2Templates(directory="app/templates")

@router.get("/{token}")
async def view_redeem(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(f"/login?next=/redeem/{token}")

    import uuid
    user = users_repo.get_user_by_id(db, uuid.UUID(user_id))

    if user.role.value != "BUSINESS_ADMIN":
        return templates.TemplateResponse(request, "redeem_error.html", {}, status_code=403)

    service = RedeemService(db)
    try:
        token_obj = service.verify_token(token)
        provider = users_repo.get_user_by_id(db, token_obj.provider_id)

        return templates.TemplateResponse(request, "redeem.html", {
            "token": token,
            "token_obj": token_obj,
            "provider": provider,
            "can_confirm": True,
        })
    except HTTPException as e:
        return templates.TemplateResponse(request, "redeem.html", {
            "error": e.detail,
            "can_confirm": False,
        })

@router.post("/{token}/confirm")
async def confirm_redeem(
    token: str,
    request: Request,
    user = Depends(get_business_admin),
    db: Session = Depends(get_db)
):
    service = RedeemService(db)
    service.confirm_redemption(token, user.id)

    return templates.TemplateResponse(request, "redeem_success.html", {})
