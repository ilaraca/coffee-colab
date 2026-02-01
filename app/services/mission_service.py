from sqlalchemy.orm import Session
import uuid
from fastapi import HTTPException
from app.models.mission import MissionStatus
from app.models.transaction import TransactionType
from app.repos import missions_repo, ratings_repo, wallet_repo, portfolio_repo

class MissionService:
    def __init__(self, db: Session):
        self.db = db

    def approve_mission(
        self, 
        mission_id: uuid.UUID, 
        cafe_admin_id: uuid.UUID,
        score: int,
        recommendation_text: str,
        allow_public: bool
    ):
        mission = missions_repo.get_mission_by_id(self.db, mission_id)
        if not mission:
            raise HTTPException(404, "Mission not found")
            
        if mission.status != MissionStatus.DONE:
            raise HTTPException(400, "Mission must be DONE to approve")
            
        # 1. Update Mission Status
        missions_repo.update_mission_status(self.db, mission, MissionStatus.APPROVED)
        
        # 2. Create Rating
        ratings_repo.create_rating(
            self.db,
            mission_id=mission.id,
            from_user_id=cafe_admin_id,
            to_user_id=mission.provider_id,
            score=score,
            recommendation_text=recommendation_text,
            allow_public=allow_public
        )
        
        # 3. Create Transaction (EARN)
        wallet_repo.create_transaction(
            self.db,
            cafe_id=mission.cafe_id,
            to_user_id=mission.provider_id,
            amount=mission.credit_value,
            type=TransactionType.EARN,
            mission_id=mission.id
        )
        
        # 4. Create Portfolio Item
        # Default category logic could be improved, for now generic or derive from mission title?
        # Using recommendation as summary + mission title.
        portfolio_repo.create_portfolio_item(
            self.db,
            provider_id=mission.provider_id,
            mission_id=mission.id,
            title=mission.title,
            summary=recommendation_text, 
            category="Service", # Placeholder
            hide_cafe_name=True, # Default per spec
            is_public=allow_public # If cafe allows public, we initially set it? 
            # Spec: "provider pode marcar... item como publico/privado. allow_public da cafeteria controla se PODE aparecer publicamente"
            # So provider toggle controls visibility, but cafe allow_public controls eligibility.
            # Let's set is_public=False initially so provider manually publishes it? 
            # Or set to allow_public value? Prompt: "provider pode marcar o item como público/privado".
            # Let's set is_public=False default.
        )
        
        return mission
