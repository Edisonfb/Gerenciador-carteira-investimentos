"""Schemas de entrada e saida do modulo de investidores."""

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

class CadastroInvestidorEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str


class InvestidorSaida(BaseModel):
    email_acesso_enviado: bool = False
    id_investidor: int
    id_usuario: int
    email: str
    nome_usuario: str | None
    primeiro_acesso_concluido: bool


class PrimeiroAcessoInvestidorEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome_usuario: str
    email_recuperacao: str
    nova_senha: str
    email_comunicacao: str | None = None


class MeuPerfilInvestidorSaida(BaseModel):
    id_investidor: int
    id_usuario: int
    id_analista_responsavel: int
    email: str
    nome_usuario: str | None
    email_recuperacao: str | None
    tipo_usuario: str
    ativo: bool
    primeiro_acesso_concluido: bool
    nome: str | None
    sobrenome: str | None
    cpf: str | None
    telefone: str | None
    cep: str | None
    uf: str | None
    cidade: str | None
    bairro: str | None
    logradouro: str | None
    numero: str | None


class MeuPerfilInvestidorAtualizacao(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome_usuario: str | None = Field(default=None, max_length=50)
    email_recuperacao: str | None = Field(default=None, max_length=255)
    senha_atual: str | None = Field(default=None, max_length=72, repr=False)
    nova_senha: str | None = Field(default=None, max_length=72, repr=False)
    email: str | None = None
    nome: str | None = None
    sobrenome: str | None = None
    telefone: str | None = None
    cep: str | None = None
    uf: str | None = None
    cidade: str | None = None
    bairro: str | None = None
    logradouro: str | None = None
    numero: str | None = None


class CadastroPrimeiroAcessoEntrada(BaseModel):
    """Conclui o convite usando apenas a autorizacao temporaria validada."""
    model_config = ConfigDict(extra="forbid")

    token_definicao: str = Field(min_length=1, max_length=2048)
    nome_usuario: str = Field(min_length=1, max_length=50)
    email_comunicacao: str = Field(min_length=1, max_length=255)
    email_recuperacao: str = Field(min_length=1, max_length=255)
    nova_senha: str = Field(min_length=8, max_length=72)

    @field_validator("email_comunicacao", "email_recuperacao")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        email = valor.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Informe um e-mail válido.")
        return email

    @field_validator("nova_senha")
    @classmethod
    def validar_tamanho_senha(cls, valor: str) -> str:
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no máximo 72 bytes.")
        return valor
