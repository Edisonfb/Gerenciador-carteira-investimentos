"""Schemas de entrada e saida do modulo de investidores."""

from pydantic import BaseModel, ConfigDict

class CadastroInvestidorEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str


class InvestidorSaida(BaseModel):
    email_acesso_enviado: bool = False
    id_investidor: int
    id_usuario: int
    email: str
    primeiro_acesso_concluido: bool


class PrimeiroAcessoInvestidorEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email_recuperacao: str
    nova_senha: str


class MeuPerfilInvestidorSaida(BaseModel):
    id_investidor: int
    id_usuario: int
    id_analista_responsavel: int
    email: str
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
