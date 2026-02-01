from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
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
    
    # Calculate simple balance
    balance = 0
    for tx in transactions:
         if tx.type.value == 'EARN': 
             balance += tx.amount
         elif tx.type.value == 'SPEND': 
             balance -= tx.amount
    
    return templates.TemplateResponse("wallet.html", {
        "request": request, 
        "user": user,
        "transactions": transactions,
        "balance": balance
    })

@router.get("/token")
async def token_redirect():
    return RedirectResponse("/provider?tab=wallet")

@router.post("/token")
async def generate_token(
    request: Request,
    amount: int = Form(...),
    user = Depends(get_provider),
    db: Session = Depends(get_db)
):
    # Need cafe_id. How do we know which cafe?
    # MVP: Form should select Cafe?
    # Or we default to the only cafe "Modo Cafe".
    from app.models.cafe import Cafe
    cafe = db.query(Cafe).first() 
    if not cafe:
        raise HTTPException(500, "No cafe found")
        
    service = RedeemService(db)
    
    try:
        raw_token, token_obj = service.generate_token(user.id, cafe.id, amount)
        qr_url = service.generate_qr_image(f"{request.base_url}redeem/{raw_token}")
        
        # Show success page with QR INSIDE Validator Dashboard
        return templates.TemplateResponse("provider_dashboard.html", {
            "request": request, 
            "user": user,
            "tab": "wallet",
            "transactions": wallet_repo.get_transactions(db, user.id),
            "balance": wallet_repo.get_balance(db, user.id, cafe.id),
            "new_qr": qr_url,
            "new_token_expiry": token_obj.expires_at,
            "redeem_link": f"{request.base_url}redeem/{raw_token}"
        })
        
    except HTTPException as e:
        return templates.TemplateResponse("provider_dashboard.html", {
            "request": request, 
            "user": user,
            "tab": "wallet",
            "transactions": wallet_repo.get_transactions(db, user.id),
            "balance": 0, 
            "error": e.detail
        })
