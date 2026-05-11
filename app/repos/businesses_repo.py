from typing import Collection, List
import uuid

from sqlalchemy.orm import Session
from app.models.business import Business
from uuid import uuid4

def create_business(db: Session, name: str, category: str = None, website_url: str = None, instagram_url: str = None) -> Business:
    # Generate a simple slug from the name
    slug = name.lower().replace(" ", "-") + "-" + str(uuid4())[:8]
    
    new_business = Business(
        name=name,
        category=category,
        slug=slug,
        website_url=website_url,
        instagram_url=instagram_url,
        is_verified=False
    )
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    return new_business

def get_business_by_id(db: Session, business_id) -> Business:
    return db.query(Business).filter(Business.id == business_id).first()


def get_businesses_by_ids(
    db: Session, business_ids: Collection[uuid.UUID]
) -> List[Business]:
    if not business_ids:
        return []
    return db.query(Business).filter(Business.id.in_(list(business_ids))).all()

def get_first_business(db: Session) -> Business:
    return db.query(Business).first()
