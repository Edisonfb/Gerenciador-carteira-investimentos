"""Schemas de entrada e saida do modulo de carteiras."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PortfolioCreate(BaseModel):
    """Dados para criacao de carteira."""

    investor_id: int
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class PortfolioUpdate(BaseModel):
    """Dados para atualizacao de carteira."""

    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    is_active: bool | None = None


class PortfolioResponse(BaseModel):
    """Representacao de carteira na API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    investor_id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PortfolioPositionItem(BaseModel):
    """Posicao consolidada de um ativo na carteira."""

    asset_id: int
    symbol: str
    name: str
    quantity: Decimal
    average_price: Decimal
    total_invested: Decimal


class PortfolioSummaryResponse(BaseModel):
    """Resumo consolidado da carteira."""

    portfolio_id: int
    portfolio_name: str
    total_invested: Decimal
    total_fees: Decimal
    cash_flow: Decimal
    positions: list[PortfolioPositionItem]
    transactions_count: int
