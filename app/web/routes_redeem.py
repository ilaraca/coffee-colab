from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.web.deps import get_cafe_admin
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
    # Public-ish view? Or Cafe only.
    # Prompt: "Confirmar resgate exige usuário cafeteria logado (CAFE_ADMIN)"
    # But viewing details might be allowed or requires login?
    # Let's require login via basic session check or redirect.
    # "Ao resgatar consumo... verificar saldo... criar SPEND".
    # /redeem/{token} mostra detalhes.
    
    # Check if logged in as admin?
    # If not logged in, asking to login?
    # Let's assume user visits link.
    
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(f"/login?next=/redeem/{token}")
    
    user = users_repo.get_user_by_id(db, user_id) # Need UUID conversion
    # Assume str to UUID logic in repo helper or cast here.
    # Repo `get_user_by_id` takes UUID.
    import uuid
    user = users_repo.get_user_by_id(db, uuid.UUID(user_id))
    
    if user.role.value != "CAFE_ADMIN":
         return templates.TemplateResponse("redeem_error.html", {"request": request}, status_code=403)

    service = RedeemService(db)
    try:
        token_obj = service.verify_token(token)
        provider = users_repo.get_user_by_id(db, token_obj.provider_id)
        
        return templates.TemplateResponse("redeem.html", {
            "request": request,
            "token": token, # raw token passed to form
            "token_obj": token_obj,
            "provider": provider,
            "can_confirm": True
        })
    except HTTPException as e:
         return templates.TemplateResponse("redeem.html", {
            "request": request,
            "error": e.detail,
            "can_confirm": False
        })

@router.post("/{token}/confirm")
async def confirm_redeem(
    token: str,
    request: Request,
    user = Depends(get_cafe_admin),
    db: Session = Depends(get_db)
):
    service = RedeemService(db)
    service.confirm_redemption(token, user.id)
    
    return templates.TemplateResponse("redeem_success.html", {
        "request": request
    })
