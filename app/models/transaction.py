import uuid
import enum
from sqlalchemy import Column, Integer, Enum, ForeignKey, Uuid
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

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    # Origem humana (ex.: ajuste manual por admin). Créditos vindos do negócio usam from_business_id.
    from_user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Negócio que originou EARN (missão aprovada) ou SPEND (resgate no estabelecimento).
    from_business_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Carteira do provider: sempre em to_user_id; saldo = SUM(EARN) - SUM(SPEND) (+ ADJUST).
    to_user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    mission_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("missions.id", ondelete="SET NULL"),
        nullable=True,
    )

    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.CONFIRMED, nullable=False)
    amount = Column(Integer, nullable=False)  # inteiro positivo
