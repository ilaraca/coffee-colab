from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.repos import users_repo
from app.web.deps import get_provider

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
         
    from app.repos import portfolio_repo, ratings_repo, missions_repo

    # Get public items
    items = portfolio_repo.get_public_items_for_provider(db, p_id)
    
    # Calculate Avg Rating
    avg_score = ratings_repo.get_avg_score_for_provider(db, p_id)
    avg_score = round(avg_score, 1) if avg_score else None
    
    # Total completed missions (APPROVED)
    total_missions = missions_repo.get_completed_missions_count_for_provider(db, p_id)
    
    # Total ratings received
    total_ratings = ratings_repo.get_total_ratings_for_provider(db, p_id)
    
    # Build a dict of mission_id -> Rating for quick lookup in template
    ratings_map = {}
    ratings = ratings_repo.get_ratings_for_provider(db, p_id)
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
    from app.repos import portfolio_repo
    
    item = portfolio_repo.get_item_by_id_and_provider(db, uuid.UUID(item_id), user.id)
    
    if not item:
        raise HTTPException(404)
        
    portfolio_repo.toggle_item_visibility(db, item)
    
    return RedirectResponse(url="/provider?tab=portfolio", status_code=status.HTTP_303_SEE_OTHER)
