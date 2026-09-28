"""Envio simples de e-mail."""
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def enviar_token_acesso(email: str, nome: str, token: str) -> None:
    """Envia o link de ativacao da conta para o e-mail do investidor."""
    link = f"{settings.endereco_frontend.rstrip('/')}/ativar-conta?token={token}"

    mensagem = EmailMessage()
    mensagem["Subject"] = "Ativação da conta"
    mensagem["From"] = settings.email_remetente
    mensagem["To"] = email
    mensagem.set_content(
        f"Olá, {nome}.\n\n"
        "Sua conta foi cadastrada. Acesse o link abaixo para ativá-la:\n"
        f"{link}\n"
    )

    with smtplib.SMTP(settings.servidor_smtp, settings.porta_smtp) as servidor:
        if settings.usar_tls:
            servidor.starttls()
        if settings.usuario_smtp:
            servidor.login(settings.usuario_smtp, settings.senha_smtp)
        servidor.send_message(mensagem)
