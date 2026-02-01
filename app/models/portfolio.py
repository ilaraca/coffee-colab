import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from app.models.base import TimestampMixin

class PortfolioItem(Base, TimestampMixin):
    __tablename__ = "portfolio_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), unique=True, nullable=False)
    
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True) # From rating recommendation usually? Or mission title? Spec says "base na missao + recomendacao"
    category = Column(String, nullable=True)
    
    is_public = Column(Boolean, default=False) # Provider toggle
    hide_cafe_name = Column(Boolean, default=True) # Privacy
