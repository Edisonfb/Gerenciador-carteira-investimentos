"""Schemas de entrada e saida do modulo de carteiras."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

class CarteiraCadastroEntrada(BaseModel):
    model_config = ConfigDict(extra = "forbid")

    nome: str

class CarteiraAtualizacaoEntrada(BaseModel):
    model_config = ConfigDict(extra = "forbid")

    nome: str | None = None
    ativa: bool | None = None

class CarteiraSaida(BaseModel):
    id_carteira: int
    id_investidor: int
    nome: str
    ativa: bool
    data_criacao: datetime
