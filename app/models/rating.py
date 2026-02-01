import uuid
from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import TimestampMixin

class Rating(Base, TimestampMixin):
    __tablename__ = "ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), unique=True, nullable=False)
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    score = Column(Integer, nullable=False) # 1..5
    recommendation_text = Column(Text, nullable=False)
    allow_public = Column(Boolean, default=False)

    mission = relationship("Mission", back_populates="rating")
