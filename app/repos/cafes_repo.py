from sqlalchemy.orm import Session
from app.models.cafe import Cafe
from uuid import uuid4

def create_cafe(db: Session, name: str, website_url: str = None, instagram_url: str = None) -> Cafe:
    # Generate a simple slug from the name
    slug = name.lower().replace(" ", "-") + "-" + str(uuid4())[:8]
    
    new_cafe = Cafe(
        name=name,
        slug=slug,
        website_url=website_url,
        instagram_url=instagram_url,
        is_verified=False
    )
    db.add(new_cafe)
    db.commit()
    db.refresh(new_cafe)
    return new_cafe

def get_cafe_by_id(db: Session, cafe_id) -> Cafe:
    return db.query(Cafe).filter(Cafe.id == cafe_id).first()
