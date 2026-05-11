import uuid
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.web.deps import get_business_admin
from app.repos import missions_repo, businesses_repo, users_repo

router = APIRouter(prefix="/business")
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def business_dashboard(request: Request, user = Depends(get_business_admin), db: Session = Depends(get_db)):
    business = None
    missions = []
    if user.business_id:
        business = businesses_repo.get_business_by_id(db, user.business_id)
        missions = missions_repo.get_missions_by_business(db, user.business_id)
        
    return templates.TemplateResponse("business_dashboard.html", {
        "request": request, 
        "user": user,
        "business": business,
        "missions": missions
    })

@router.post("/register_profile")
async def register_profile(
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    website_url: str = Form(None),
    instagram_url: str = Form(None),
    user = Depends(get_business_admin),
    db: Session = Depends(get_db)
) -> RedirectResponse:
    if user.business_id:
        raise HTTPException(status_code=400, detail="Estabelecimento já cadastrado.")
        
    new_business = businesses_repo.create_business(db, name, category, website_url, instagram_url)
    users_repo.link_business_to_user(db, user, new_business.id)
    
    return RedirectResponse(url="/business", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/missions")
async def create_mission(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    credit_value: int = Form(...),
    user = Depends(get_business_admin),
    db: Session = Depends(get_db)
) -> RedirectResponse:
    if not user.business_id:
        raise HTTPException(status_code=400, detail="Must register business profile first")
        
    if credit_value <= 0:
         raise HTTPException(status_code=400, detail="Credit value must be positive")
         
    missions_repo.create_mission(db, user.business_id, title, description, credit_value)
    return RedirectResponse(url="/business", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/missions/{mission_id}/approve")
async def approve_mission(
    mission_id: uuid.UUID,
    score: int = Form(...),
    recommendation_text: str = Form(...),
    allow_public: bool = Form(False),
    user = Depends(get_business_admin),
    db: Session = Depends(get_db)
) -> RedirectResponse:
    from app.services.mission_service import MissionService
    
    service = MissionService(db)
    service.approve_mission(
        mission_id,
        user.id,
        score,
        recommendation_text,
        allow_public
    )
    
    return RedirectResponse(url="/business", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/redeem")
async def redeem_manual_redirect(request: Request, token: str = ""):
    if token:
        return RedirectResponse(url=f"/business/redeem/{token.upper()}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/business", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/redeem/{token}", response_class=HTMLResponse)
async def view_redeem(
    token: str,
    request: Request,
    user = Depends(get_business_admin),
    db: Session = Depends(get_db)
):
    from app.services.redeem_service import RedeemService
    service = RedeemService(db)
    
    try:
        token_obj = service.verify_token(token)
        provider = users_repo.get_user_by_id(db, token_obj.provider_id)
        if token_obj.business_id != user.business_id:
             raise HTTPException(403, "Token não pertence a este estabelecimento.")
             
        return templates.TemplateResponse("business_redeem.html", {
            "request": request,
            "token_str": token,
            "token_obj": token_obj,
            "provider": provider
        })
    except HTTPException as e:
        return templates.TemplateResponse("business_redeem.html", {
            "request": request,
            "error": e.detail
        })

@router.post("/redeem/{token}", response_class=HTMLResponse)
async def confirm_redeem(
    token: str,
    request: Request,
    user = Depends(get_business_admin),
    db: Session = Depends(get_db)
):
    from app.services.redeem_service import RedeemService
    service = RedeemService(db)
    
    try:
        token_obj_pre = service.verify_token(token)
        if token_obj_pre.business_id != user.business_id:
             raise HTTPException(403, "Não autorizado")
             
        service.confirm_redemption(token, user.id)
        
        return templates.TemplateResponse("business_redeem.html", {
            "request": request,
            "success": True
        })
    except HTTPException as e:
        return templates.TemplateResponse("business_redeem.html", {
            "request": request,
            "error": e.detail
        })
