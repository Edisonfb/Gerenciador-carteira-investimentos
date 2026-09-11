"""Schemas de entrada e saida do modulo de autenticacao."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Dados para cadastro publico de analista."""

    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Dados para login."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class PasswordChange(BaseModel):
    """Troca de senha do usuario autenticado."""

    current_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    """Resposta de autenticacao com token JWT."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Dados publicos do usuario."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    must_change_password: bool
    created_at: datetime
    updated_at: datetime
