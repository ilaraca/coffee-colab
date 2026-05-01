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
    assert c.get("/business", follow_redirects=False).status_code == 401


@pytest.fixture(scope="module")
def business_admin_email():
    return f"business_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_1_register_business_admin(business_admin_email, db_session):
    response = client.post(
        "/register",
        data={
            "name": "Admin Business QA",
            "email": business_admin_email,
            "password": "BusinessPassword123!",
            "role": "BUSINESS_ADMIN",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Verifique seu e-mail" in response.text
    user = get_user_by_email(db_session, business_admin_email)
    assert user is not None
    assert user.role.value == "BUSINESS_ADMIN"
    assert user.business_id is None


def test_2_verify_and_login_business(business_admin_email, db_session):
    token = generate_verification_token(business_admin_email)
    r = client.get(f"/verify-email?token={token}", follow_redirects=True)
    assert r.status_code == 200
    assert "E-mail confirmado" in r.text

    db_session.expire_all()
    assert get_user_by_email(db_session, business_admin_email).email_verified is True

    r = client.post(
        "/login",
        data={"email": business_admin_email, "password": "BusinessPassword123!"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/business"


def test_3_register_business_profile(business_admin_email):
    """POST /business/register_profile cria negócio e associa ao admin."""
    r = client.post(
        "/business/register_profile",
        data={
            "name": "Negócio QA Smoke",
            "category": "Cafe",
            "website_url": "",
            "instagram_url": "",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/business"

    r2 = client.get("/business", follow_redirects=True)
    assert r2.status_code == 200
    assert "Negócio QA Smoke" in r2.text
