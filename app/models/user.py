import uuid
import enum
from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from app.models.base import TimestampMixin

class UserRole(str, enum.Enum):
    CAFE_ADMIN = "CAFE_ADMIN"
    PROVIDER = "PROVIDER"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cafe_id = Column(UUID(as_uuid=True), ForeignKey("cafes.id"), nullable=True) # Admin belongs to a cafe context usually, providers might not initially but for this MVP simplicity we might keep it loose or null for global providers? 
    # Requirement S4: "Multi-tenant: Each record belongs to a cafe (cafe_id)"
    # However, providers might work across cafes. The prompt says "Seeds will have 1 cafe... Role-based access... PROVIDER accepts mission".
    # Usually providers are global. Let's make cafe_id nullable for providers, or specific if they are tied to one.
    # The prompt says "Cafes have product... Providers want to consume".
    # Let's assume cafe_id here mainly for CAFE_ADMINs.
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
