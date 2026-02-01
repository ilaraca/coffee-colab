from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.web.deps import get_cafe_admin
from app.repos import missions_repo

router = APIRouter(prefix="/cafe")
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def cafe_dashboard(request: Request, user = Depends(get_cafe_admin), db: Session = Depends(get_db)):
    missions = missions_repo.get_missions_by_cafe(db, user.cafe_id)
    return templates.TemplateResponse("cafe_dashboard.html", {
        "request": request, 
        "user": user,
        "missions": missions
    })

@router.post("/missions")
async def create_mission(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    credit_value: int = Form(...),
    user = Depends(get_cafe_admin),
    db: Session = Depends(get_db)
):
    if credit_value <= 0:
         # Simplified error handling suitable for MVP (could be HTMX swap w/ error)
         raise HTTPException(status_code=400, detail="Credit value must be positive")
         
    missions_repo.create_mission(db, user.cafe_id, title, description, credit_value)
    return RedirectResponse(url="/cafe", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/missions/{mission_id}/approve")
async def approve_mission(
    mission_id: str,
    score: int = Form(...),
    recommendation_text: str = Form(...),
    allow_public: bool = Form(False),
    user = Depends(get_cafe_admin),
    db: Session = Depends(get_db)
):
    import uuid
    from app.services.mission_service import MissionService
    
    service = MissionService(db)
    service.approve_mission(
        uuid.UUID(mission_id),
        user.id,
        score,
        recommendation_text,
        allow_public
    )
    
    return RedirectResponse(url="/cafe", status_code=status.HTTP_303_SEE_OTHER)
