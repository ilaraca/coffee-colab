import uuid
import enum
from sqlalchemy import Column, Integer, Enum, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from app.models.base import TimestampMixin

class TokenStatus(str, enum.Enum):
    ISSUED = "ISSUED"
    REDEEMED = "REDEEMED"
    EXPIRED = "EXPIRED"

class RedeemToken(Base, TimestampMixin):
    __tablename__ = "redeem_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cafe_id = Column(UUID(as_uuid=True), ForeignKey("cafes.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    token_hash = Column(String, nullable=False) # sha256
    amount = Column(Integer, nullable=False)
    status = Column(Enum(TokenStatus), default=TokenStatus.ISSUED, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
