from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.db import get_db
from app.repos import users_repo
from app.web.deps import get_provider
from app.models.portfolio import PortfolioItem
from app.models.rating import Rating

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/u/{provider_id}/portfolio", response_class=HTMLResponse)
async def public_portfolio(
    provider_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    import uuid
    try:
        p_id = uuid.UUID(provider_id)
    except ValueError:
        raise HTTPException(404, "Invalid provider ID")
        
    provider = users_repo.get_user_by_id(db, p_id)
    if not provider:
         raise HTTPException(404, "Provider not found")
         
    # Get public items (with mission relationship eager-loaded)
    items = db.query(PortfolioItem).filter(
        PortfolioItem.provider_id == p_id,
        PortfolioItem.is_public == True  # noqa: E712
    ).order_by(PortfolioItem.created_at.desc()).all()
    
    # Calculate Avg Rating
    avg_score = db.query(func.avg(Rating.score)).filter(Rating.to_user_id == p_id).scalar()
    avg_score = round(avg_score, 1) if avg_score else None
    
    # Total completed missions (APPROVED)
    from app.models.mission import Mission, MissionStatus
    total_missions = db.query(func.count(Mission.id)).filter(
        Mission.provider_id == p_id,
        Mission.status == MissionStatus.APPROVED
    ).scalar() or 0
    
    # Total ratings received
    total_ratings = db.query(func.count(Rating.id)).filter(Rating.to_user_id == p_id).scalar() or 0
    
    # Build a dict of mission_id -> Rating for quick lookup in template
    ratings_map = {}
    ratings = db.query(Rating).filter(Rating.to_user_id == p_id).all()
    for r in ratings:
        ratings_map[str(r.mission_id)] = r
    
    return templates.TemplateResponse("portfolio_public.html", {
        "request": request,
        "provider": provider,
        "items": items,
        "avg_score": avg_score,
        "total_missions": total_missions,
        "total_ratings": total_ratings,
        "ratings_map": ratings_map
    })

@router.post("/provider/portfolio/{item_id}/toggle")
async def toggle_visibility(
    item_id: str,
    user = Depends(get_provider),
    db: Session = Depends(get_db)
):
    import uuid
    item = db.query(PortfolioItem).filter(
        PortfolioItem.id == uuid.UUID(item_id),
        PortfolioItem.provider_id == user.id
    ).first()
    
    if not item:
        raise HTTPException(404)
        
    item.is_public = not item.is_public
    db.commit()
    
    return RedirectResponse(url="/provider?tab=portfolio", status_code=status.HTTP_303_SEE_OTHER)
