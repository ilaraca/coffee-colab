"""Ambiente de teste: SQLite em memória compartilhada (StaticPool), sem PostgreSQL."""
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("MAIL_USERNAME", "")
os.environ.setdefault("MAIL_PASSWORD", "")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app.core import db as db_module  # noqa: E402

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

db_module.engine = test_engine
db_module.SessionLocal = TestSessionLocal

import app.models  # noqa: E402, F401 — registra tabelas no metadata
from app.core.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def _sqlite_schema():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
