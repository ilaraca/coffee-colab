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
    hide_cafe_name: bool = True,
    is_public: bool = False # Provider decides later, or default private
) -> PortfolioItem:
    item = PortfolioItem(
        provider_id=provider_id,
        mission_id=mission_id,
        title=title,
        summary=summary,
        category=category,
        hide_cafe_name=hide_cafe_name,
        is_public=is_public
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
