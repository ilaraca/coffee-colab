import uuid
import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Boolean, Uuid
from app.core.db import Base
from app.models.base import TimestampMixin

class UserRole(str, enum.Enum):
    BUSINESS_ADMIN = "BUSINESS_ADMIN"
    PROVIDER = "PROVIDER"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(Uuid(as_uuid=True), ForeignKey("businesses.id"), nullable=True) # Admin belongs to a business context usually
    # Requirement S4: "Multi-tenant: Each record belongs to a business (business_id)"
    # However, providers might work across businesses. The prompt says "Seeds will have 1 business... Role-based access... PROVIDER accepts mission".
    # Usually providers are global. Let's make business_id nullable for providers, or specific if they are tied to one.
    # The prompt says "Businesses have product... Providers want to consume".
    # Let's assume business_id here mainly for BUSINESS_ADMINs.
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

