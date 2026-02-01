from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import uuid
from app.models.mission import Mission, MissionStatus

def create_mission(db: Session, cafe_id: uuid.UUID, title: str, description: str, credit_value: int) -> Mission:
    mission = Mission(
        cafe_id=cafe_id,
        title=title,
        description=description,
        credit_value=credit_value,
        status=MissionStatus.OPEN
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission

def get_missions_by_cafe(db: Session, cafe_id: uuid.UUID) -> List[Mission]:
    return db.query(Mission).filter(Mission.cafe_id == cafe_id).order_by(desc(Mission.created_at)).all()

def get_open_missions(db: Session, cafe_id: Optional[uuid.UUID] = None) -> List[Mission]:
    query = db.query(Mission).filter(Mission.status == MissionStatus.OPEN)
    if cafe_id:
        query = query.filter(Mission.cafe_id == cafe_id)
    return query.order_by(desc(Mission.created_at)).all()

def get_missions_for_provider(db: Session, provider_id: uuid.UUID) -> List[Mission]:
    return db.query(Mission).filter(Mission.provider_id == provider_id).order_by(desc(Mission.updated_at)).all()

def get_mission_by_id(db: Session, mission_id: uuid.UUID) -> Optional[Mission]:
    return db.query(Mission).filter(Mission.id == mission_id).first()

def update_mission_status(db: Session, mission: Mission, status: MissionStatus, provider_id: Optional[uuid.UUID] = None, proof_of_work: Optional[str] = None) -> Mission:
    mission.status = status
    if provider_id:
        mission.provider_id = provider_id
    if proof_of_work:
        mission.proof_of_work = proof_of_work
    db.commit()
    db.refresh(mission)
    return mission
