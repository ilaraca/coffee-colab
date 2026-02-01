from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from typing import List, Optional
from app.models.transaction import Transaction, TransactionType, TransactionStatus

def create_transaction(
    db: Session, 
    cafe_id: uuid.UUID, 
    to_user_id: uuid.UUID, 
    amount: int, 
    type: TransactionType, 
    mission_id: Optional[uuid.UUID] = None,
    from_user_id: Optional[uuid.UUID] = None
) -> Transaction:
    tx = Transaction(
        cafe_id=cafe_id,
        to_user_id=to_user_id,
        from_user_id=from_user_id,
        amount=amount,
        type=type,
        status=TransactionStatus.CONFIRMED, # Auto-confirm for now
        mission_id=mission_id
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def get_balance(db: Session, user_id: uuid.UUID, cafe_id: uuid.UUID) -> int:
    # Balance = SUM(EARN) - SUM(SPEND) for this provider at this cafe
    # Note: user_id is the provider (to_user_id in EARN, but in SPEND is it to or from?)
    # In my model note: "EARN: to_user_id = provider", "SPEND: to_user_id = provider" (because it tracks THEIR wallet balance decrement).
    # Let's verify Transaction model notes I wrote:
    # "EARN: to_user_id = provider (+ amount)"
    # "SPEND: to_user_id = provider (- amount)"
    # So we query all transactions where to_user_id == user_id and cafe_id == cafe_id.
    
    txs = db.query(Transaction).filter(
        Transaction.to_user_id == user_id,
        Transaction.cafe_id == cafe_id,
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
