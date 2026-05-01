from sqlalchemy.orm import Session
import uuid
from app.models.rating import Rating

def create_rating(
    db: Session,
    mission_id: uuid.UUID,
    from_user_id: uuid.UUID,
    to_user_id: uuid.UUID,
    score: int,
    recommendation_text: str,
    allow_public: bool
) -> Rating:
    rating = Rating(
        mission_id=mission_id,
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        score=score,
        recommendation_text=recommendation_text,
        allow_public=allow_public
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating

from sqlalchemy import func

def get_avg_score_for_provider(db: Session, provider_id: uuid.UUID) -> float:
    return db.query(func.avg(Rating.score)).filter(Rating.to_user_id == provider_id).scalar()

def get_total_ratings_for_provider(db: Session, provider_id: uuid.UUID) -> int:
    return db.query(func.count(Rating.id)).filter(Rating.to_user_id == provider_id).scalar() or 0

def get_ratings_for_provider(db: Session, provider_id: uuid.UUID) -> list[Rating]:
    return db.query(Rating).filter(Rating.to_user_id == provider_id).all()
