"""Schemas de entrada e saida do modulo de ativos financeiros."""

from pydantic import BaseModel, ConfigDict

class CadastroAtivoEntrada(BaseModel):
    ticker: str
    nome: str
    setor: str
    subsetor: str
    segmento: str

class AtivoSaida(BaseModel):
    ticker: str
    nome: str
    setor: str
    subsetor: str
    segmento: str


class CadastroAtivoCarteiraEntrada(BaseModel):
    ticker: str
    id_carteira: int
    quantidade: int

class AtivoCarteiraSaida(BaseModel):
    ticker: str
    quantidade: int

class AtivoCarteiraUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quantidade: bool | None = None
