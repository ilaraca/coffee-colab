from sqlalchemy.orm import Session
import uuid
from app.models.portfolio import PortfolioItem

def create_portfolio_item(
    db: Session,
    provider_id: uuid.UUID,
    mission_id: uuid.UUID,
    title: str,
    summary: str,
    category: str = "Geral",
    hide_business_name: bool = True,
    is_public: bool = False # Provider decides later, or default private
) -> PortfolioItem:
    item = PortfolioItem(
        provider_id=provider_id,
        mission_id=mission_id,
        title=title,
        summary=summary,
        category=category,
        hide_business_name=hide_business_name,
        is_public=is_public
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_items_for_provider(db: Session, provider_id: uuid.UUID) -> list[PortfolioItem]:
    return db.query(PortfolioItem).filter(PortfolioItem.provider_id == provider_id).all()

def get_public_items_for_provider(db: Session, provider_id: uuid.UUID) -> list[PortfolioItem]:
    return db.query(PortfolioItem).filter(
        PortfolioItem.provider_id == provider_id,
        PortfolioItem.is_public == True
    ).order_by(PortfolioItem.created_at.desc()).all()

def get_item_by_id_and_provider(db: Session, item_id: uuid.UUID, provider_id: uuid.UUID) -> PortfolioItem:
    return db.query(PortfolioItem).filter(
        PortfolioItem.id == item_id,
        PortfolioItem.provider_id == provider_id
    ).first()

def toggle_item_visibility(db: Session, item: PortfolioItem):
    item.is_public = not item.is_public
    db.commit()
