"""Schemas de entrada e saida do modulo de investidores."""

from pydantic import BaseModel

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