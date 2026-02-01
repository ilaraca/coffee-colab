from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from typing import Optional
from app.models.redeem import RedeemToken, TokenStatus

def create_token(
    db: Session,
    cafe_id: uuid.UUID,
    provider_id: uuid.UUID,
    token_hash: str,
    amount: int,
    expires_at: datetime
) -> RedeemToken:
    token = RedeemToken(
        cafe_id=cafe_id,
        provider_id=provider_id,
        token_hash=token_hash,
        amount=amount,
        expires_at=expires_at,
        status=TokenStatus.ISSUED
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token

def get_token_by_hash(db: Session, token_hash: str) -> Optional[RedeemToken]:
    return db.query(RedeemToken).filter(RedeemToken.token_hash == token_hash).first()

def update_token_status(db: Session, token: RedeemToken, status: TokenStatus) -> RedeemToken:
    token.status = status
    db.commit()
    db.refresh(token)
    return token
