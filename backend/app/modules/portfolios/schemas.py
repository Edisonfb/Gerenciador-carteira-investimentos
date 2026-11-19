"""Schemas de entrada e saida do modulo de carteiras."""

from datetime import datetime
from decimal import Decimal

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

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


class PosicaoResumoSaida(BaseModel):
    """Apresenta valor e peso atual de um ativo na carteira."""

    ticker: str
    quantidade: int
    cotacao: Decimal | None
    data_atualizacao: datetime | None
    valor_atual: Decimal
    participacao_percentual: Decimal


class CarteiraResumoSaida(BaseModel):
    """Apresenta o patrimonio total e a composicao financeira da carteira."""

    id_carteira: int
    patrimonio_total: Decimal
    ativos: list[PosicaoResumoSaida]


class SimulacaoAporteEntrada(BaseModel):
    """Recebe o valor disponível para sugerir compras sem registrá-las."""
    model_config = ConfigDict(extra="forbid")

    aporte: Annotated[Decimal, Field(gt=0, max_digits=14, decimal_places=2)]


class AtivoSimulacaoAporteSaida(BaseModel):
    """Mostra a posição atual, a cotação usada e a compra sugerida."""

    ticker: str
    cotacao: Decimal
    data_atualizacao: datetime
    objetivo_percentual: Decimal
    quantidade_atual: int
    valor_atual: Decimal
    participacao_atual: Decimal
    distancia_atual: Decimal
    quantidade_sugerida: int
    custo_sugerido: Decimal
    quantidade_projetada: int
    valor_projetado: Decimal
    participacao_projetada: Decimal
    distancia_projetada: Decimal


class SimulacaoAporteSaida(BaseModel):
    """Apresenta a distribuição sugerida e o saldo não investido."""

    id_carteira: int
    patrimonio_atual: Decimal
    aporte: Decimal
    valor_investido: Decimal
    saldo_restante: Decimal
    patrimonio_projetado: Decimal
    ativos: list[AtivoSimulacaoAporteSaida]
