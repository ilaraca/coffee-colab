"""Garantias de schema alinhadas a docs/db-schema-review (constraints e vínculos).

Não importar `tests.conftest` aqui: isso reexecuta o módulo, cria um segundo engine
SQLite sem `create_all` e sobrescreve `SessionLocal` (vide tests/conftest.py).
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.business import Business
from app.models.mission import Mission, MissionStatus
from app.models.rating import Rating
from app.models.redeem import RedeemToken, TokenStatus
from app.models.user import User, UserRole


@pytest.fixture
def db() -> Session:
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def _business_provider_admin(db: Session):
    business = Business(
        name="B",
        slug=f"b-{uuid.uuid4().hex[:10]}",
        category="Cafe",
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    admin = User(
        business_id=business.id,
        name="Admin",
        email=f"a{uuid.uuid4().hex[:10]}@example.com",
        password_hash="x",
        role=UserRole.BUSINESS_ADMIN,
        email_verified=True,
    )
    provider = User(
        business_id=None,
        name="Prov",
        email=f"p{uuid.uuid4().hex[:10]}@example.com",
        password_hash="x",
        role=UserRole.PROVIDER,
        email_verified=True,
    )
    db.add_all([admin, provider])
    db.commit()
    db.refresh(admin)
    db.refresh(provider)
    return business, admin, provider


def test_redeem_token_hash_must_be_unique(db: Session):
    business, _, provider = _business_provider_admin(db)
    exp = datetime.now(timezone.utc) + timedelta(minutes=5)
    h = "deadbeef" * 8  # 64 chars like hex sha256
    t1 = RedeemToken(
        business_id=business.id,
        provider_id=provider.id,
        token_hash=h,
        amount=10,
        status=TokenStatus.ISSUED,
        expires_at=exp,
    )
    db.add(t1)
    db.commit()

    t2 = RedeemToken(
        business_id=business.id,
        provider_id=provider.id,
        token_hash=h,
        amount=10,
        status=TokenStatus.ISSUED,
        expires_at=exp,
    )
    db.add(t2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_rating_score_must_be_between_1_and_5(db: Session):
    business, admin, provider = _business_provider_admin(db)
    mission = Mission(
        business_id=business.id,
        provider_id=provider.id,
        title="m",
        description="d",
        credit_value=50,
        status=MissionStatus.DONE,
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)

    bad = Rating(
        mission_id=mission.id,
        from_user_id=admin.id,
        to_user_id=provider.id,
        score=99,
        recommendation_text="n/a",
        allow_public=False,
    )
    db.add(bad)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_provider_cannot_have_business_id(db: Session):
    business = Business(
        name="X",
        slug=f"x-{uuid.uuid4().hex[:10]}",
        category="x",
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    user = User(
        business_id=business.id,
        name="Bad",
        email=f"bad{uuid.uuid4().hex[:10]}@example.com",
        password_hash="x",
        role=UserRole.PROVIDER,
        email_verified=True,
    )
    db.add(user)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
