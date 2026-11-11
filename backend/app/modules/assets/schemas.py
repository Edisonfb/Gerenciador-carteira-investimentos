"""Contratos de entrada e saida de ativos e vinculos com carteiras."""
from datetime import datetime
from typing import Annotated
from decimal import Decimal


from pydantic import AliasChoices, BaseModel, ConfigDict, Field, StringConstraints

Ticker = Annotated[
    str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=1,
                           max_length=10, pattern=r"^[A-Za-z0-9]+$"),
]
QuantidadeInicial = Annotated[int, Field(strict=True, ge=0, le=0)]
TextoSetor = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class CadastroAtivoEntrada(BaseModel):
    """Valida os campos do catalogo e aceita o nome anterior codigo."""
    model_config = ConfigDict(extra="forbid")

    ticker: Ticker = Field(validation_alias=AliasChoices("ticker", "codigo"))
    nome: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)] = ""
    setor: TextoSetor
    subsetor: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] = ""
    segmento: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] = ""


AtivoCadastroEntrada = CadastroAtivoEntrada


class AtivoAtualizacaoEntrada(BaseModel):
    """Permite atualizar os dados descritivos e o status, mantendo a chave."""
    model_config = ConfigDict(extra="forbid")

    nome: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)] | None = None
    setor: TextoSetor | None = None
    subsetor: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] | None = None
    segmento: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] | None = None
    ativo: bool | None = None


class AtivoSaida(BaseModel):
    """Retorna os campos do catalogo integrado."""
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    nome: str
    setor: str
    subsetor: str
    segmento: str
    ativo: bool
    data_criacao: datetime


class CadastroAtivoCarteiraEntrada(BaseModel):
    """Inclui o ativo sem posicao; compras sao registradas por transacao."""
    model_config = ConfigDict(extra="forbid")

    ticker: Ticker
    id_carteira: Annotated[int, Field(strict=True, gt=0)]
    quantidade: QuantidadeInicial
    objetivo_percentual: Annotated[Decimal, Field(gt=0, le=100, max_digits=5, decimal_places=2)]


class AtivoCarteiraSaida(BaseModel):
    """Retorna o vinculo sem dados de outros investidores."""
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    id_carteira: int
    quantidade: int
    objetivo_percentual: Decimal


class AtivoCarteiraUpdate(BaseModel):
    """Permite alterar somente a meta, preservando a quantidade comprada."""
    model_config = ConfigDict(extra="forbid")

    objetivo_percentual: Annotated[Decimal, Field(gt=0, le=100, max_digits=5, decimal_places=2)] | None = None
