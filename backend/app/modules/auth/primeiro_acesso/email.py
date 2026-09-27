"""Envio do link de primeiro acesso para o e-mail do investidor."""

import os
import smtplib
from email.message import EmailMessage


class EmailNaoConfigurado(Exception):
    """O servidor de e-mail ainda não foi configurado."""


class FalhaEnvioEmail(Exception):
    """O servidor de e-mail recusou ou não concluiu o envio."""


def enviar_link_primeiro_acesso(destinatario: str, nome: str, link: str) -> None:
    host = os.getenv("SMTP_HOST", "").strip()
    if not host:
        raise EmailNaoConfigurado("Serviço de e-mail não configurado.")

    porta = int(os.getenv("SMTP_PORT", "587"))
    usuario = os.getenv("SMTP_USER", "").strip()
    senha = os.getenv("SMTP_PASSWORD", "")
    remetente = os.getenv("SMTP_FROM", "").strip() or usuario

    mensagem = EmailMessage()
    mensagem["Subject"] = "Primeiro acesso ao Gerenciador de Carteiras"
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem.set_content(
        f"Olá, {nome}.\n\n"
        "Um analista cadastrou sua conta no Gerenciador de Carteiras de Investimento.\n"
        "Use o link abaixo para validar sua conta e definir sua senha.\n"
        "Este link vale por 24 horas e só pode ser usado uma vez.\n\n"
        f"{link}\n"
    )

    try:
        with smtplib.SMTP(host, porta, timeout=20) as servidor:
            servidor.starttls()
            if usuario and senha:
                servidor.login(usuario, senha)
            servidor.send_message(mensagem)
    except (OSError, smtplib.SMTPException) as erro:
        raise FalhaEnvioEmail("Não foi possível enviar o e-mail.") from erro
