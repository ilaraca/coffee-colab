import uuid
from sqlalchemy import Column, String, Boolean, Uuid
from app.core.db import Base
from app.models.base import TimestampMixin

class Business(Base, TimestampMixin):
    __tablename__ = "businesses"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True) # Cafe, Restaurante, Padaria, etc.
    slug = Column(String, unique=True, index=True, nullable=False)
    website_url = Column(String, nullable=True)
    instagram_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
