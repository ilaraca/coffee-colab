"""Smoke: fluxo cafeteria — cadastro, verificação, login e cadastro do perfil da cafeteria."""
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.core.tokens import generate_verification_token
from app.main import app
from app.repos.users_repo import get_user_by_email

client = TestClient(app)


def test_0_protected_routes_require_login():
    """Rotas de painel exigem sessão (cliente sem cookies)."""
    c = TestClient(app)
    assert c.get("/provider", follow_redirects=False).status_code == 401
    assert c.get("/cafe", follow_redirects=False).status_code == 401


@pytest.fixture(scope="module")
def cafe_admin_email():
    return f"cafe_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_1_register_cafe_admin(cafe_admin_email, db_session):
    response = client.post(
        "/register",
        data={
            "name": "Admin Café QA",
            "email": cafe_admin_email,
            "password": "CafePassword123!",
            "role": "CAFE_ADMIN",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Verifique seu e-mail" in response.text
    user = get_user_by_email(db_session, cafe_admin_email)
    assert user is not None
    assert user.role.value == "CAFE_ADMIN"
    assert user.cafe_id is None


def test_2_verify_and_login_cafe(cafe_admin_email, db_session):
    token = generate_verification_token(cafe_admin_email)
    r = client.get(f"/verify-email?token={token}", follow_redirects=True)
    assert r.status_code == 200
    assert "E-mail confirmado" in r.text

    db_session.expire_all()
    assert get_user_by_email(db_session, cafe_admin_email).email_verified is True

    r = client.post(
        "/login",
        data={"email": cafe_admin_email, "password": "CafePassword123!"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/cafe"


def test_3_register_cafe_profile(cafe_admin_email):
    """POST /cafe/register_profile cria cafeteria e associa ao admin."""
    r = client.post(
        "/cafe/register_profile",
        data={
            "name": "Cafeteria QA Smoke",
            "website_url": "",
            "instagram_url": "",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/cafe"

    r2 = client.get("/cafe", follow_redirects=True)
    assert r2.status_code == 200
    assert "Cafeteria QA Smoke" in r2.text
