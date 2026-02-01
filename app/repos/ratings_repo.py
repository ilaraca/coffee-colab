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
