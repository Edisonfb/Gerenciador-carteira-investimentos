"""Envio simples de e-mail."""
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def _enviar_mensagem(email: str, assunto: str, conteudo: str) -> None:
    """Envia uma mensagem textual usando a configuracao SMTP da aplicacao."""
    if not settings.servidor_smtp or not settings.email_remetente:
        raise RuntimeError("Envio de e-mail não configurado. Defina SMTP_HOST e SMTP_FROM.")

    mensagem = EmailMessage()

    mensagem["Subject"] = assunto
    mensagem["From"] = settings.email_remetente
    mensagem["To"] = email
    mensagem.set_content(conteudo)

    with smtplib.SMTP(settings.servidor_smtp, settings.porta_smtp, timeout=15) as servidor:
        if settings.usar_tls:
            servidor.starttls()
        if settings.usuario_smtp:
            servidor.login(settings.usuario_smtp, settings.senha_smtp)
        servidor.send_message(mensagem)


def enviar_token_acesso(email: str, token: str) -> None:
    """Mantem o envio do token inicial usado no convite de investidores."""
    _enviar_mensagem(
        email, "Seu token de acesso",
        "Olá.\n\n"
        "Sua conta foi cadastrada com sucesso.\n\n"
        "Seu token de acesso é:\n\n"
        f"{token}\n\n"
        "Na tela de login, selecione Primeiro acesso e informe seu e-mail e este token.\n"
        "Depois, cadastre seu usuário, e-mails de comunicação e recuperação e sua senha para entrar no sistema.\n"
        f"{settings.endereco_frontend.rstrip('/')}/primeiro-acesso\n"
        "Não compartilhe este token com outras pessoas."
    )


def enviar_link_senha(email: str, link: str, primeiro_acesso: bool = False) -> None:
    """Envia o link e aceita a opcao de primeiro acesso usada na integracao."""
    _enviar_mensagem(
        email, "Primeiro acesso" if primeiro_acesso else "Redefinição de senha",
        "Olá.\n\n"
        "Use o link abaixo para cadastrar uma nova senha:\n\n"
        f"{link}\n\n"
        "O link expira em 30 minutos e deixa de funcionar após a troca da senha.\n"
        "Se você não fez essa solicitação, ignore esta mensagem.",
    )
