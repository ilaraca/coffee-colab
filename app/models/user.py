import uuid
import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Boolean, Uuid, CheckConstraint
from app.core.db import Base
from app.models.base import TimestampMixin


class UserRole(str, enum.Enum):
    BUSINESS_ADMIN = "BUSINESS_ADMIN"
    PROVIDER = "PROVIDER"


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        # PROVIDER não deve estar vinculado a um negócio (business_id só para BUSINESS_ADMIN após onboarding).
        CheckConstraint(
            "role != 'PROVIDER' OR business_id IS NULL",
            name="ck_user_provider_no_business",
        ),
    )

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

