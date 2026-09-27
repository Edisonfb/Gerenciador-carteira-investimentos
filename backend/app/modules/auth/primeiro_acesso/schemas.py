"""Entrada e saida do envio do token de primeiro acesso."""

from pydantic import BaseModel


class EnviarTokenEntrada(BaseModel):
    id_investidor: int


class EnviarTokenSaida(BaseModel):
    mensagem: str
