import logging
from app.core.config import settings
from app.core.tokens import generate_verification_token, generate_password_reset_token

logger = logging.getLogger(__name__)


async def send_verification_email(email: str) -> None:
    """
    Send a verification email to the given address.
    If SMTP credentials are not configured, logs the verification link to console.
    """
    token = generate_verification_token(email)
    verify_url = f"{settings.APP_BASE_URL}/verify-email?token={token}"

    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        # Dev mode: print link to console instead of sending e-mail
        logger.warning(
            "SMTP not configured. Verification link for %s:\n  %s",
            email,
            verify_url,
        )
        print(f"\n[DEV] Verification link for {email}:\n  {verify_url}\n")
        return

    # Build and send HTML email via fastapi-mail
    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    html_body = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #0f0e0d; color: #f5f0e8; margin: 0; padding: 0; }}
            .container {{ max-width: 520px; margin: 40px auto; background: #1a1815; border-radius: 12px; overflow: hidden; border: 1px solid #2d2925; }}
            .header {{ background: linear-gradient(135deg, #c8952a 0%, #e8b84b 100%); padding: 36px 40px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 1.8rem; color: #0f0e0d; font-weight: 700; letter-spacing: -0.5px; }}
            .header p {{ margin: 8px 0 0; color: #3d2b00; font-size: 0.9rem; }}
            .body {{ padding: 36px 40px; }}
            .body p {{ color: #b8a99a; line-height: 1.6; margin: 0 0 16px; }}
            .body strong {{ color: #f5f0e8; }}
            .btn {{ display: inline-block; background: linear-gradient(135deg, #c8952a, #e8b84b); color: #0f0e0d !important; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 700; font-size: 1rem; margin: 8px 0 24px; }}
            .link-fallback {{ font-size: 0.78rem; color: #6b5f55; word-break: break-all; }}
            .footer {{ padding: 20px 40px; border-top: 1px solid #2d2925; text-align: center; font-size: 0.75rem; color: #6b5f55; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>☕ Modo Café</h1>
                <p>Verificação de e-mail</p>
            </div>
            <div class="body">
                <p>Olá! Obrigado por se cadastrar no <strong>Coffee Co-lab</strong>.</p>
                <p>Clique no botão abaixo para confirmar seu e-mail e ativar sua conta. O link é válido por <strong>24 horas</strong>.</p>
                <a href="{verify_url}" class="btn">✔ Verificar meu e-mail</a>
                <p>Se o botão não funcionar, copie e cole esse link no navegador:</p>
                <p class="link-fallback">{verify_url}</p>
                <p style="margin-top: 24px;">Se você não criou uma conta, ignore este e-mail.</p>
            </div>
            <div class="footer">
                Coffee Co-lab &mdash; Seu Talento Vale Café
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="☕ Confirme seu e-mail — Coffee Co-lab",
        recipients=[email],
        body=html_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info("Verification email sent to %s", email)

async def send_password_reset_email(email: str) -> None:
    """
    Send a password reset email.
    """
    token = generate_password_reset_token(email)
    reset_url = f"{settings.APP_BASE_URL}/reset-password?token={token}"

    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        logger.warning(
            "SMTP not configured. Password reset link for %s:\n  %s",
            email,
            reset_url,
        )
        print(f"\n[DEV] Password reset link for {email}:\n  {reset_url}\n")
        return

    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    html_body = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #0f0e0d; color: #f5f0e8; margin: 0; padding: 0; }}
            .container {{ max-width: 520px; margin: 40px auto; background: #1a1815; border-radius: 12px; overflow: hidden; border: 1px solid #2d2925; }}
            .header {{ background: linear-gradient(135deg, #c8952a 0%, #e8b84b 100%); padding: 36px 40px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 1.8rem; color: #0f0e0d; font-weight: 700; letter-spacing: -0.5px; }}
            .header p {{ margin: 8px 0 0; color: #3d2b00; font-size: 0.9rem; }}
            .body {{ padding: 36px 40px; }}
            .body p {{ color: #b8a99a; line-height: 1.6; margin: 0 0 16px; }}
            .body strong {{ color: #f5f0e8; }}
            .btn {{ display: inline-block; background: linear-gradient(135deg, #c8952a, #e8b84b); color: #0f0e0d !important; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 700; font-size: 1rem; margin: 8px 0 24px; }}
            .link-fallback {{ font-size: 0.78rem; color: #6b5f55; word-break: break-all; }}
            .footer {{ padding: 20px 40px; border-top: 1px solid #2d2925; text-align: center; font-size: 0.75rem; color: #6b5f55; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>☕ Modo Café</h1>
                <p>Recuperação de Senha</p>
            </div>
            <div class="body">
                <p>Olá,</p>
                <p>Recebemos um pedido para redefinir a senha da conta vinculada a <strong>{email}</strong> no Coffee Co-lab.</p>
                <p>Clique no botão abaixo para criar uma nova senha. O link é válido por <strong>2 horas</strong>.</p>
                <a href="{reset_url}" class="btn">🔑 Redefinir minha senha</a>
                <p>Se você não solicitou isso, você pode ignorar esse e-mail com segurança. Sua senha permanecerá a mesma.</p>
                <p style="margin-top: 24px;">Se o botão não funcionar, copie e cole este link:</p>
                <p class="link-fallback">{reset_url}</p>
            </div>
            <div class="footer">
                Coffee Co-lab &mdash; Seu Talento Vale Café
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="🔑 Redefinição de Senha — Coffee Co-lab",
        recipients=[email],
        body=html_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info("Password reset email sent to %s", email)
