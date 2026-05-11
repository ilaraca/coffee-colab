import uuid
import enum
from sqlalchemy import Column, Integer, Enum, ForeignKey, String, DateTime, Uuid
from app.core.db import Base
from app.models.base import TimestampMixin


class TokenStatus(str, enum.Enum):
    ISSUED = "ISSUED"
    REDEEMED = "REDEEMED"
    EXPIRED = "EXPIRED"


class RedeemToken(Base, TimestampMixin):
    __tablename__ = "redeem_tokens"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    provider_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    token_hash = Column(String, unique=True, nullable=False)  # sha256
    amount = Column(Integer, nullable=False)
    status = Column(
        Enum(TokenStatus),
        default=TokenStatus.ISSUED,
        nullable=False,
        index=True,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    transaction_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True,
    )
    redeemed_at = Column(DateTime(timezone=True), nullable=True)
