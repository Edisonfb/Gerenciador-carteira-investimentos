"""Envio simples de e-mail."""
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def enviar_token_acesso(email: str, nome: str, token: str) -> None:
    mensagem = EmailMessage()

    mensagem["Subject"] = "Seu token de acesso"
    mensagem["From"] = settings.email_remetente
    mensagem["To"] = email

    mensagem.set_content(
        f"Olá, {nome}.\n\n"
        "Sua conta foi cadastrada com sucesso.\n\n"
        "Seu token de acesso é:\n\n"
        f"{token}\n\n"
        "Na tela de login, selecione Primeiro acesso e informe seu e-mail e este token.\n"
        "Depois, cadastre sua senha para entrar no sistema.\n"
        f"{settings.endereco_frontend.rstrip('/')}/primeiro-acesso\n"
        "Não compartilhe este token com outras pessoas."
    )

    with smtplib.SMTP(settings.servidor_smtp, settings.porta_smtp, timeout=15) as servidor:
        if settings.usar_tls:
            servidor.starttls()
        if settings.usuario_smtp:
            servidor.login(settings.usuario_smtp, settings.senha_smtp)
        servidor.send_message(mensagem)


def enviar_link_senha(email: str, link: str, primeiro_acesso: bool) -> None:
    mensagem = EmailMessage()
    mensagem["Subject"] = "Primeiro acesso" if primeiro_acesso else "Recuperação de senha"
    mensagem["From"] = settings.email_remetente
    mensagem["To"] = email
    mensagem.set_content(
        "Olá!\n\nUse o link abaixo para definir sua senha. "
        "Ele expira em 30 minutos e só pode ser usado uma vez.\n\n"
        f"{link}\n\nSe você não solicitou esta mensagem, ignore este e-mail."
    )
    with smtplib.SMTP(settings.servidor_smtp, settings.porta_smtp, timeout=15) as servidor:
        if settings.usar_tls:
            servidor.starttls()
        if settings.usuario_smtp:
            servidor.login(settings.usuario_smtp, settings.senha_smtp)
        servidor.send_message(mensagem)
