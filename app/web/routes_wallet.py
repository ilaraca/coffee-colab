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
    # For MVP assume single cafe or list all?
    # Logic implies "wallet" is global but balance is per cafe?
    # Spec: "Saldo... por provider por cafe"
    # So wallet should show breakdown.
    # For MVP, let's pick the "Seed Cafe" or list all cafes with balance > 0.
    # We'll just hardcode fetching balance for 'Modo Cafe' (via slug logic or just query all txs and aggregate?)
    # Easier: Query all transactions, group by Cafe.
    # MVP shortcut: Fetch all transactions. Display list.
    # Compute total balance derived? Or per cafe.
    # Let's show specific Cafe balance if we can.
    # Or just list transactions and show "Total Balance" (assuming 1 cafe for now).
    # We will get transactions.
    
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
                "transactions": b_txs
            })
    
    return templates.TemplateResponse("wallet.html", {
        "request": request, 
        "user": user,
        "grouped_wallets": grouped_wallets
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
        
        # Grouping logic again for success response
        transactions = wallet_repo.get_transactions(db, user.id)
        from app.models.business import Business
        business_ids = {tx.business_id for tx in transactions}
        businesses = db.query(Business).filter(Business.id.in_(list(business_ids))).all()
        grouped_wallets = []
        for b in businesses:
            b_txs = [tx for tx in transactions if tx.business_id == b.id]
            bal = sum(t.amount for t in b_txs if t.type.value == 'EARN') - sum(t.amount for t in b_txs if t.type.value == 'SPEND')
            grouped_wallets.append({"business": b, "balance": bal, "transactions": b_txs})

        return templates.TemplateResponse("provider_dashboard.html", {
            "request": request, 
            "user": user,
            "tab": "wallet",
            "grouped_wallets": grouped_wallets,
            "new_qr": qr_url,
            "new_token_expiry": token_obj.expires_at,
            "redeem_link": f"{request.base_url}business/redeem/{raw_token}",
            "raw_token": raw_token
        })
        
    except HTTPException as e:
        transactions = wallet_repo.get_transactions(db, user.id)
        from app.models.business import Business
        business_ids = {tx.business_id for tx in transactions}
        businesses = db.query(Business).filter(Business.id.in_(list(business_ids))).all()
        grouped_wallets = []
        for b in businesses:
            b_txs = [tx for tx in transactions if tx.business_id == b.id]
            bal = sum(t.amount for t in b_txs if t.type.value == 'EARN') - sum(t.amount for t in b_txs if t.type.value == 'SPEND')
            grouped_wallets.append({"business": b, "balance": bal, "transactions": b_txs})

        return templates.TemplateResponse("provider_dashboard.html", {
            "request": request, 
            "user": user,
            "tab": "wallet",
            "grouped_wallets": grouped_wallets,
            "error": e.detail
        })
