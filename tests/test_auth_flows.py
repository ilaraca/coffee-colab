"""Smoke: cadastro, verificação de e-mail, login, esqueci senha e redefinição."""
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import app
from app.repos.users_repo import get_user_by_email

client = TestClient(app)


@pytest.fixture(scope="module")
def test_user_email():
    return f"qa_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_1_registration(test_user_email, db_session):
    """Cadastro cria usuário não verificado e mostra página de verificação."""
    data = {
        "name": "QA Tester",
        "email": test_user_email,
        "password": "Password123!",
        "role": "PROVIDER",
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "Verifique seu e-mail" in response.text

    user = get_user_by_email(db_session, test_user_email)
    assert user is not None
    assert user.email_verified is False


def test_2_login_unverified(test_user_email):
    """Login bloqueado até verificar e-mail; opção de reenvio visível."""
    data = {
        "email": test_user_email,
        "password": "Password123!",
    }
    response = client.post("/login", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "verificar seu e-mail antes de entrar" in response.text
    assert "Reenviar e-mail" in response.text


def test_3_verify_email(test_user_email, db_session):
    """Link de verificação ativa a conta."""
    from app.core.tokens import generate_verification_token

    token = generate_verification_token(test_user_email)

    response = client.get(f"/verify-email?token={token}", follow_redirects=True)
    assert response.status_code == 200
    assert "E-mail confirmado" in response.text

    db_session.expire_all()
    user = get_user_by_email(db_session, test_user_email)
    assert user.email_verified is True


def test_4_login_verified(test_user_email):
    """Após verificar, login redireciona para o painel do prestador."""
    data = {
        "email": test_user_email,
        "password": "Password123!",
    }
    response = client.post("/login", data=data, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/provider"


def test_5_forgot_password(test_user_email):
    """Solicitação de reset sempre mostra mensagem neutra."""
    response = client.post(
        "/forgot-password", data={"email": test_user_email}, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Confira sua caixa de entrada" in response.text


def test_6_reset_password(test_user_email, db_session):
    """Token válido redefine senha e exibe sucesso no login."""
    from app.core.security import verify_password
    from app.core.tokens import generate_password_reset_token

    token = generate_password_reset_token(test_user_email)

    data = {
        "token": token,
        "password": "NewPassword456!",
    }
    response = client.post("/reset-password", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "Senha alterada com sucesso" in response.text

    db_session.expire_all()
    user = get_user_by_email(db_session, test_user_email)
    assert verify_password("NewPassword456!", user.password_hash) is True


def test_7_login_new_password(test_user_email):
    """Login com a nova senha após reset."""
    data = {
        "email": test_user_email,
        "password": "NewPassword456!",
    }
    response = client.post("/login", data=data, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/provider"
