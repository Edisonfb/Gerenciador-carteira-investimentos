"""Schemas de entrada e saida do modulo de autenticacao."""

from pydantic import BaseModel, ConfigDict, Field


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


class LogoutSaida(BaseModel):
    mensagem: str


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str | None = None
    ativo: bool | None = None


class SolicitarSenhaEntrada(BaseModel):
    email: str


class RedefinirSenhaEntrada(BaseModel):
    token: str
    senha: str


class PrimeiroAcessoEntrada(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    token: str = Field(min_length=1, max_length=255)


class PrimeiroAcessoSaida(BaseModel):
    token_definicao: str
