"""Schemas de entrada e saida do modulo de transacoes."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    """Dados para registro de transacao."""

    portfolio_id: int
    asset_id: int | None = None
    transaction_type: str = Field(min_length=2, max_length=40)
    quantity: Decimal = Field(default=Decimal("0"))
    unit_price: Decimal = Field(default=Decimal("0"))
    transaction_date: datetime
    fees: Decimal = Field(default=Decimal("0"))
    notes: str | None = None


class TransactionUpdate(BaseModel):
    """Dados para atualizacao de transacao."""

    asset_id: int | None = None
    transaction_type: str | None = Field(default=None, min_length=2, max_length=40)
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    transaction_date: datetime | None = None
    fees: Decimal | None = None
    notes: str | None = None


class TransactionResponse(BaseModel):
    """Representacao de transacao na API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    portfolio_id: int
    asset_id: int | None
    transaction_type: str
    quantity: Decimal
    unit_price: Decimal
    transaction_date: datetime
    fees: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
