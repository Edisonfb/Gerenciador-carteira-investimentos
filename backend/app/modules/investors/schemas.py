"""Schemas de entrada e saida do modulo de investidores."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InvestorCreate(BaseModel):
    """Dados para pre-cadastro de cliente pelo analista."""

    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    rg: str = Field(min_length=5, max_length=32)
    document: str = Field(min_length=5, max_length=32, description="CPF")
    email: EmailStr
    phone: str = Field(min_length=8, max_length=32)
    address: str = Field(min_length=5, max_length=255)


class InvestorUpdate(BaseModel):
    """Dados para atualizacao de investidor."""

    first_name: str | None = Field(default=None, min_length=2, max_length=80)
    last_name: str | None = Field(default=None, min_length=2, max_length=80)
    rg: str | None = Field(default=None, min_length=5, max_length=32)
    document: str | None = Field(default=None, min_length=5, max_length=32)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=8, max_length=32)
    address: str | None = Field(default=None, min_length=5, max_length=255)
    is_active: bool | None = None


class InvestorResponse(BaseModel):
    """Representacao de investidor na API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    account_user_id: int | None
    first_name: str
    last_name: str
    name: str
    rg: str
    document: str
    email: str
    phone: str
    address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class InvestorAccessResponse(InvestorResponse):
    """Investidor com senha temporaria gerada no pre-cadastro ou reemissao."""

    temporary_password: str
