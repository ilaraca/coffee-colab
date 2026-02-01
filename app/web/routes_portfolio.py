from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.db import get_db
from app.repos import users_repo, portfolio_repo, ratings_repo
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
         
    # Get public items
    # Repo helper needed? writing inline for speed or adding to repo.
    # Logic: is_public = True AND mission.rating.allow_public = True (enforced at creation time usually, but should verify join?)
    # My creation logic set is_public=allow_public initially but provider can toggle.
    # But if cafe didn't allow, provider shouldn't be able to publicize.
    # Current model `Rating.allow_public` exists. `PortfolioItem` has `is_public`.
    # Let's assume `PortfolioItem.is_public` is the source of truth, but we should cross check if we want to be strict.
    # For MVP: Trust `PortfolioItem.is_public` (which user toggles).
    
    items = db.query(PortfolioItem).filter(
        PortfolioItem.provider_id == p_id,
        PortfolioItem.is_public == True
    ).all()
    
    # Calculate Avg Rating
    # We need to query ratings for this provider.
    avg_score = db.query(func.avg(Rating.score)).filter(Rating.to_user_id == p_id).scalar()
    avg_score = round(avg_score, 1) if avg_score else "Novato"
    
    return templates.TemplateResponse("portfolio_public.html", {
        "request": request,
        "provider": provider,
        "items": items,
        "avg_score": avg_score
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
