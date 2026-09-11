"""Schemas de entrada e saida do modulo de ativos financeiros."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssetCreate(BaseModel):
    """Dados para cadastro de ativo."""

    symbol: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=2, max_length=120)
    asset_type: str = Field(min_length=2, max_length=40)


class AssetUpdate(BaseModel):
    """Dados para atualizacao de ativo."""

    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=2, max_length=120)
    asset_type: str | None = Field(default=None, min_length=2, max_length=40)
    is_active: bool | None = None


class AssetResponse(BaseModel):
    """Representacao de ativo na API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    name: str
    asset_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
