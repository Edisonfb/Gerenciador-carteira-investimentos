"""Schemas de entrada e saida do modulo de investidores."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InvestorCreate(BaseModel):
    """Dados para cadastro de investidor."""

    name: str = Field(min_length=2, max_length=120)
    document: str = Field(min_length=5, max_length=32)
    email: EmailStr | None = None


class InvestorUpdate(BaseModel):
    """Dados para atualizacao de investidor."""

    name: str | None = Field(default=None, min_length=2, max_length=120)
    document: str | None = Field(default=None, min_length=5, max_length=32)
    email: EmailStr | None = None
    is_active: bool | None = None


class InvestorResponse(BaseModel):
    """Representacao de investidor na API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    document: str
    email: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
