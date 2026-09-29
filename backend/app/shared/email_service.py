"""Envio simples de e-mail."""
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def enviar_token_acesso(email: str, nome: str, token: str) -> None:
    if not settings.servidor_smtp or not settings.email_remetente:
        raise RuntimeError("Envio de e-mail não configurado. Defina SMTP_HOST e SMTP_FROM.")
    
    mensagem = EmailMessage()
    
    mensagem["Subject"] = "Seu token de acesso"
    mensagem["From"] = settings.email_remetente
    mensagem["To"] = email

    mensagem.set_content(
        f"Olá, {nome}.\n\n"
        "Sua conta foi cadastrada com sucesso.\n\n"
        "Seu token de acesso é:\n\n"
        f"{token}\n\n"
        "Utilize este token para acessar o sistema.\n"
        "Não compartilhe este token com outras pessoas."
    )


    with smtplib.SMTP(settings.servidor_smtp, settings.porta_smtp) as servidor:
        if settings.usar_tls:
            servidor.starttls()
        if settings.usuario_smtp:
            servidor.login(settings.usuario_smtp, settings.senha_smtp)
        servidor.send_message(mensagem)
