import uuid
import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import TimestampMixin

class MissionStatus(str, enum.Enum):
    OPEN = "OPEN"
    ACCEPTED = "ACCEPTED"
    DONE = "DONE"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"

class Mission(Base, TimestampMixin):
    __tablename__ = "missions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cafe_id = Column(UUID(as_uuid=True), ForeignKey("cafes.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    credit_value = Column(Integer, nullable=False)
    status = Column(Enum(MissionStatus), default=MissionStatus.OPEN, nullable=False)
    proof_of_work = Column(Text, nullable=True)

    # Relationships
    rating = relationship("Rating", uselist=False, back_populates="mission")
