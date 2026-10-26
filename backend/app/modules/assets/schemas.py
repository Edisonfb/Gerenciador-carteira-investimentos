"""Schemas de entrada e saida do modulo de ativos financeiros."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AtivoCadastroEntrada(BaseModel):
    """Dados necessarios para cadastrar um ativo"""
    model_config = ConfigDict(extra="forbid")

    codigo: str
    setor: str

class AtivoAtualizacaoEntrada(BaseModel):
    """Dados permitidos para atualizar um ativo"""

    model_config = ConfigDict(extra="forbid")

    codigo: str | None = None
    setor: str | None = None
    ativo: bool | None = None

class AtivoSaida(BaseModel):
    """Dados retornados pela API para um ativo financeiro"""

    id_ativo: int
    codigo: str
    setor: str
    ativo: bool
    data_criacao: datetime