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
    transactions = wallet_repo.get_transactions(db, user.id)

    from app.models.business import Business
    business_ids = {tx.business_id for tx in transactions}
    businesses = db.query(Business).filter(Business.id.in_(list(business_ids))).all()
    business_map = {b.id: b for b in businesses}

    grouped_wallets = []
    for b_id, b_obj in business_map.items():
        b_txs = [tx for tx in transactions if tx.business_id == b_id]
        b_balance = 0
        for tx in b_txs:
            if tx.type.value == 'EARN':
                b_balance += tx.amount
            elif tx.type.value == 'SPEND':
                b_balance -= tx.amount
        if b_balance > 0 or b_txs:
            grouped_wallets.append({
                "business": b_obj,
                "balance": b_balance,
                "transactions": b_txs,
            })

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

    def _build_grouped_wallets():
        txs = wallet_repo.get_transactions(db, user.id)
        from app.models.business import Business as Biz
        b_ids = {tx.business_id for tx in txs}
        biz_list = db.query(Biz).filter(Biz.id.in_(list(b_ids))).all()
        result = []
        for b in biz_list:
            b_txs = [tx for tx in txs if tx.business_id == b.id]
            bal = (
                sum(t.amount for t in b_txs if t.type.value == 'EARN')
                - sum(t.amount for t in b_txs if t.type.value == 'SPEND')
            )
            result.append({"business": b, "balance": bal, "transactions": b_txs})
        return result

    try:
        raw_token, token_obj = service.generate_token(user.id, business.id, amount)
        qr_url = service.generate_qr_image(f"{request.base_url}redeem/{raw_token}")

        return templates.TemplateResponse(request, "provider_dashboard.html", {
            "user": user,
            "tab": "wallet",
            "grouped_wallets": _build_grouped_wallets(),
            "new_qr": qr_url,
            "new_token_expiry": token_obj.expires_at,
            "redeem_link": f"{request.base_url}business/redeem/{raw_token}",
            "raw_token": raw_token,
        })

    except HTTPException as e:
        return templates.TemplateResponse(request, "provider_dashboard.html", {
            "user": user,
            "tab": "wallet",
            "grouped_wallets": _build_grouped_wallets(),
            "error": e.detail,
        })
