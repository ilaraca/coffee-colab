import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from app.models.base import TimestampMixin

class Cafe(Base, TimestampMixin):
    __tablename__ = "cafes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
