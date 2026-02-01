import uuid
import enum
from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from app.models.base import TimestampMixin

class TransactionType(str, enum.Enum):
    EARN = "EARN"
    SPEND = "SPEND"
    ADJUST = "ADJUST"

class TransactionStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cafe_id = Column(UUID(as_uuid=True), ForeignKey("cafes.id"), nullable=False)
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # For SPEND (provider -> cafe) this might be implicit or explicit. Usually provider is the user whose balance is affecting.
    # In this logic: 
    # EARN: to_user_id = provider. (+ amount)
    # SPEND: to_user_id = provider. (- amount) or we handle signs?
    # Spec says: Saldo = SUM(EARN) - SUM(SPEND). So both are positive amounts, just diff types.
    # to_user_id should be the provider always for balance tracking.
    
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=True)
    
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.CONFIRMED, nullable=False)
    amount = Column(Integer, nullable=False) # Positive integer
