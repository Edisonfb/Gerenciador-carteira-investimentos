"""Schemas de entrada e saida do modulo de autenticacao."""

from pydantic import BaseModel, ConfigDict


class LoginEntrada(BaseModel):
    email: str
    senha: str


class UsuarioSaida(BaseModel):
    id_usuario: int
    email: str
    tipo_usuario: str
    ativo: bool


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str | None = None
    ativo: bool | None = None
