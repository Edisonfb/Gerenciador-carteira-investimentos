"""Schemas de entrada e saida do modulo de autenticacao."""

from pydantic import BaseModel


class CadastroUsuarioEntrada(BaseModel):
    nome: str
    email: str
    senha: str


class LoginEntrada(BaseModel):
    email: str
    senha: str


class UsuarioSaida(BaseModel):
    id: int
    nome: str
    email: str


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
