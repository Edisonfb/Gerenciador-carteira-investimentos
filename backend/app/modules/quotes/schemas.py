"""Schemas de entrada e saida do modulo de cotacoes."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CotacaoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    preco: Decimal
    data_atualizacao: datetime
