"""Regras do token de primeiro acesso."""

import os
import secrets
from datetime import datetime, timedelta

from app.modules.auth.primeiro_acesso.email import (
    EmailNaoConfigurado,
    FalhaEnvioEmail,
    enviar_link_primeiro_acesso,
)
from app.modules.auth.primeiro_acesso.repository import PrimeiroAcessoRepository

VALIDADE_HORAS = 24


class PrimeiroAcessoService:
    def __init__(self, repository: PrimeiroAcessoRepository):
        self.repository = repository

    def enviar_token(self, id_investidor: int) -> tuple[str | None, str | None]:
        investidor = self.repository.buscar_investidor(id_investidor)

        if investidor is None:
            return None, "Investidor não encontrado."

        if not investidor.email or "@" not in investidor.email:
            return None, "Investidor não possui um e-mail válido."

        token = secrets.token_urlsafe(32)
        expira_em = datetime.utcnow() + timedelta(hours=VALIDADE_HORAS)
        link = self._montar_link(token)

        token_anterior = investidor.token_acesso
        expira_anterior = investidor.token_expira_em
        utilizado_anterior = investidor.token_utilizado

        investidor.token_acesso = token
        investidor.token_expira_em = expira_em
        investidor.token_utilizado = False
        self.repository.salvar(investidor)

        try:
            enviar_link_primeiro_acesso(investidor.email, investidor.nome, link)
        except (EmailNaoConfigurado, FalhaEnvioEmail):
            investidor.token_acesso = token_anterior
            investidor.token_expira_em = expira_anterior
            investidor.token_utilizado = utilizado_anterior
            self.repository.salvar(investidor)
            return None, "Não foi possível enviar o token para o e-mail do investidor."

        return "Token de primeiro acesso enviado para o e-mail do investidor.", None

    def _montar_link(self, token: str) -> str:
        base = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
        return f"{base}/primeiro-acesso?token={token}"
