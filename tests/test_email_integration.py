"""Teste integrado: envio de e-mail (SMTP real ou verificação de conteúdo)."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult

from app.core.config import settings
from app.services.email_service import (
    send_password_reset_email,
    send_verification_email,
)


class CapturingHandler:
    """Handler que captura mensagens recebidas."""

    def __init__(self):
        self.messages = []

    async def handle_DATA(self, server, session, envelope):
        content = envelope.content
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        self.messages.append(
            {
                "mail_from": envelope.mail_from,
                "rcpt_tos": envelope.rcpt_tos,
                "content": content,
            }
        )
        return "250 OK"


def _accept_all_auth(server, session, envelope, mechanism, auth_data):
    return AuthResult(success=True)


def _start_smtp_server():
    """Inicia servidor SMTP; retorna (handler, port) ou None se falhar (ex.: errno 49 no macOS)."""
    handler = CapturingHandler()
    controller = Controller(
        handler,
        hostname="127.0.0.1",
        port=0,
        authenticator=_accept_all_auth,
    )
    try:
        controller.start()
        return handler, controller.port, controller
    except OSError as e:
        if e.errno == 49:  # EADDRNOTAVAIL em alguns macOS
            pytest.skip(
                "SMTP local indisponível neste ambiente (errno 49). "
                "Execute com Mailtrap (MAIL_USERNAME/MAIL_PASSWORD no .env) para teste real."
            )
        raise


@pytest.fixture
def smtp_server():
    """Servidor SMTP fake em localhost. Faz skip se não for possível iniciar (ex.: errno 49)."""
    handler, port, controller = _start_smtp_server()
    yield handler, port
    controller.stop()


# ---- Testes com SMTP real (ou skip) ----
@pytest.mark.asyncio
async def test_send_verification_email_real_smtp(smtp_server):
    """Envio de verificação conecta ao SMTP e envia mensagem com link."""
    handler, port = smtp_server

    with patch.object(settings, "MAIL_SERVER", "127.0.0.1"), patch.object(
        settings, "MAIL_PORT", port
    ), patch.object(settings, "MAIL_USERNAME", "test"), patch.object(
        settings, "MAIL_PASSWORD", "test"
    ), patch.object(settings, "MAIL_STARTTLS", False):
        await send_verification_email("usuario@exemplo.com")

    assert len(handler.messages) == 1
    msg = handler.messages[0]
    assert msg["rcpt_tos"] == ["usuario@exemplo.com"]
    assert "/verify-email?token=" in msg["content"]
    assert "Verificar meu e-mail" in msg["content"]


@pytest.mark.asyncio
async def test_send_password_reset_email_real_smtp(smtp_server):
    """Envio de reset de senha conecta ao SMTP e envia link válido."""
    handler, port = smtp_server

    with patch.object(settings, "MAIL_SERVER", "127.0.0.1"), patch.object(
        settings, "MAIL_PORT", port
    ), patch.object(settings, "MAIL_USERNAME", "test"), patch.object(
        settings, "MAIL_PASSWORD", "test"
    ), patch.object(settings, "MAIL_STARTTLS", False):
        await send_password_reset_email("recuperar@exemplo.com")

    assert len(handler.messages) == 1
    msg = handler.messages[0]
    assert msg["rcpt_tos"] == ["recuperar@exemplo.com"]
    assert "/reset-password?token=" in msg["content"]
    assert "Redefinir minha senha" in msg["content"]


# ---- Testes de conteúdo (mock) — sempre funcionam ----
@pytest.mark.asyncio
async def test_send_verification_email_builds_correct_message():
    """Verifica que o serviço monta a mensagem com destinatário, link e conteúdo esperados."""
    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()

    with patch("fastapi_mail.FastMail", return_value=mock_fm), patch.object(
        settings, "MAIL_USERNAME", "x"
    ), patch.object(settings, "MAIL_PASSWORD", "x"):
        await send_verification_email("verificar@exemplo.com")

    mock_fm.send_message.assert_called_once()
    msg = mock_fm.send_message.call_args[0][0]
    assert msg.recipients == ["verificar@exemplo.com"]
    assert "/verify-email?token=" in msg.body
    assert "Verificar meu e-mail" in msg.body


@pytest.mark.asyncio
async def test_send_password_reset_email_builds_correct_message():
    """Verifica que o serviço monta a mensagem de reset corretamente."""
    mock_fm = MagicMock()
    mock_fm.send_message = AsyncMock()

    with patch("fastapi_mail.FastMail", return_value=mock_fm), patch.object(
        settings, "MAIL_USERNAME", "x"
    ), patch.object(settings, "MAIL_PASSWORD", "x"):
        await send_password_reset_email("reset@exemplo.com")

    mock_fm.send_message.assert_called_once()
    msg = mock_fm.send_message.call_args[0][0]
    assert msg.recipients == ["reset@exemplo.com"]
    assert "/reset-password?token=" in msg.body
    assert "Redefinir minha senha" in msg.body
    assert "reset@exemplo.com" in msg.body
