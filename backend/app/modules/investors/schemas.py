"""Schemas de entrada e saida do modulo de investidores."""

from pydantic import BaseModel, ConfigDict

class CadastroInvestidorEntrada(BaseModel):
    id_analista_responsavel: int
    nome: str
    sobrenome: str
    email: str
    rg: str | None = None
    cpf: str
    telefone: str
    cep: str
    uf: str
    cidade: str
    bairro: str
    logradouro: str
    numero: str

class InvestidorSaida(BaseModel):
    id_investidor: int
    id_usuario: int
    nome: str
    sobrenome: str
    email: str
    cpf: str
    telefone: str


class MeuPerfilInvestidorSaida(BaseModel):
    id_investidor: int
    id_usuario: int
    id_analista_responsavel: int
    email: str
    tipo_usuario: str
    ativo: bool
    nome: str
    sobrenome: str
    cpf: str
    telefone: str
    cep: str
    uf: str
    cidade: str
    bairro: str
    logradouro: str
    numero: str


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
