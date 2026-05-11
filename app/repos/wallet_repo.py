from sqlalchemy.orm import Session
import uuid
from typing import List, Optional
from app.models.transaction import Transaction, TransactionType, TransactionStatus

def create_transaction(
    db: Session,
    business_id: uuid.UUID,
    to_user_id: uuid.UUID,
    amount: int,
    type: TransactionType,
    mission_id: Optional[uuid.UUID] = None,
    from_user_id: Optional[uuid.UUID] = None,
    from_business_id: Optional[uuid.UUID] = None,
) -> Transaction:
    tx = Transaction(
        business_id=business_id,
        to_user_id=to_user_id,
        from_user_id=from_user_id,
        from_business_id=from_business_id,
        amount=amount,
        type=type,
        status=TransactionStatus.CONFIRMED, # Auto-confirm for now
        mission_id=mission_id
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def get_balance(db: Session, user_id: uuid.UUID, business_id: uuid.UUID) -> int:
    # Balance = SUM(EARN) - SUM(SPEND) for this provider at this business
    # Note: user_id is the provider (to_user_id in EARN, but in SPEND is it to or from?)
    # In my model note: "EARN: to_user_id = provider", "SPEND: to_user_id = provider" (because it tracks THEIR wallet balance decrement).
    # Let's verify Transaction model notes I wrote:
    # "EARN: to_user_id = provider (+ amount)"
    # "SPEND: to_user_id = provider (- amount)"
    # So we query all transactions where to_user_id == user_id and business_id == business_id.
    
    txs = db.query(Transaction).filter(
        Transaction.to_user_id == user_id,
        Transaction.business_id == business_id,
        Transaction.status == TransactionStatus.CONFIRMED
    ).all()
    
    balance = 0
    for tx in txs:
        if tx.type == TransactionType.EARN:
            balance += tx.amount
        elif tx.type == TransactionType.SPEND:
            balance -= tx.amount
        elif tx.type == TransactionType.ADJUST:
             # Adjust can be pos or neg? Assume simple additive for now or handle signs manually? 
             # Prompt said "Adjust manual outside MVP". Ignore or treat as additive.
             balance += tx.amount
             
    return balance

def get_transactions(db: Session, user_id: uuid.UUID) -> List[Transaction]:
     return db.query(Transaction).filter(
        Transaction.to_user_id == user_id
    ).order_by(Transaction.created_at.desc()).all()


def build_provider_grouped_wallets(db: Session, user_id: uuid.UUID) -> List[dict]:
    """Transações do provider agrupadas por negócio (para templates wallet / dashboard)."""
    from app.repos import businesses_repo

    transactions = get_transactions(db, user_id)
    business_ids = {tx.business_id for tx in transactions}
    businesses = businesses_repo.get_businesses_by_ids(db, business_ids)
    business_map = {b.id: b for b in businesses}

    grouped: List[dict] = []
    for b_id, b_obj in business_map.items():
        b_txs = [tx for tx in transactions if tx.business_id == b_id]
        b_balance = 0
        for tx in b_txs:
            if tx.type.value == "EARN":
                b_balance += tx.amount
            elif tx.type.value == "SPEND":
                b_balance -= tx.amount
        if b_balance > 0 or b_txs:
            grouped.append(
                {"business": b_obj, "balance": b_balance, "transactions": b_txs}
            )
    return grouped
