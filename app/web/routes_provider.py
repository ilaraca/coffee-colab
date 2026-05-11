from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.web.deps import get_provider
from app.repos import missions_repo
from typing import Optional

router = APIRouter(prefix="/provider")
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def provider_dashboard(
    request: Request,
    tab: str = "open",
    user = Depends(get_provider),
    db: Session = Depends(get_db)
):
    missions_open = []
    missions_my = []

    if tab == "open":
        missions_open = missions_repo.get_open_missions(db)
    elif tab == "my":
        missions_my = missions_repo.get_missions_for_provider(db, user.id)
    elif tab == "portfolio":
        from app.repos import portfolio_repo
        missions_portfolio = portfolio_repo.get_items_for_provider(db, user.id)
        return templates.TemplateResponse(request, "provider_dashboard.html", {
            "user": user,
            "tab": tab,
            "missions_open": missions_open,
            "missions_my": missions_my,
            "items": missions_portfolio,
        })
    elif tab == "wallet":
        from app.repos import wallet_repo

        grouped_wallets = wallet_repo.build_provider_grouped_wallets(db, user.id)

        return templates.TemplateResponse(request, "provider_dashboard.html", {
            "user": user,
            "tab": tab,
            "missions_open": missions_open,
            "missions_my": missions_my,
            "grouped_wallets": grouped_wallets,
        })

    return templates.TemplateResponse(request, "provider_dashboard.html", {
        "user": user,
        "tab": tab,
        "missions_open": missions_open,
        "missions_my": missions_my,
    })

@router.post("/missions/{mission_id}/accept")
async def accept_mission(
    mission_id: str,
    user = Depends(get_provider),
    db: Session = Depends(get_db)
):
    import uuid
    from app.models.mission import MissionStatus

    mission = missions_repo.get_mission_by_id(db, uuid.UUID(mission_id))
    if not mission or mission.status != MissionStatus.OPEN:
        raise HTTPException(400, "Mission not available")

    missions_repo.update_mission_status(db, mission, MissionStatus.ACCEPTED, user.id)
    return RedirectResponse(url="/provider?tab=my", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/missions/{mission_id}/done")
async def mark_done(
    mission_id: str,
    proof_of_work: Optional[str] = Form(None),
    user = Depends(get_provider),
    db: Session = Depends(get_db)
):
    import uuid
    from app.models.mission import MissionStatus

    mission = missions_repo.get_mission_by_id(db, uuid.UUID(mission_id))
    if not mission:
        raise HTTPException(404)

    if mission.provider_id != user.id:
        raise HTTPException(403, "Not your mission")

    if mission.status != MissionStatus.ACCEPTED:
        raise HTTPException(400, "Cannot mark done")

    missions_repo.update_mission_status(db, mission, MissionStatus.DONE, proof_of_work=proof_of_work)
    return RedirectResponse(url="/provider?tab=my", status_code=status.HTTP_303_SEE_OTHER)
