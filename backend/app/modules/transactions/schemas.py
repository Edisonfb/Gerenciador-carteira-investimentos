"""Schemas de entrada e saida do modulo de transacoes."""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.modules.assets.schemas import Ticker


TipoTransacao = Literal["compra", "venda"]


class TransacaoEntrada(BaseModel):
    """Recebe os dados reais da compra ou venda, inclusive preco pago."""
    model_config = ConfigDict(extra="forbid")

    id_carteira: Annotated[int, Field(strict=True, gt=0)]
    ticker: Ticker
    tipo: TipoTransacao
    quantidade: Annotated[int, Field(strict=True, gt=0, le=2147483647)]
    preco_unitario: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
    data_transacao: AwareDatetime | None = None


class TransacaoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_transacao: int
    id_carteira: int | None
    nome_carteira: str
    ticker: str
    tipo: str
    quantidade: int
    preco_unitario: Decimal
    valor_total: Decimal
    data_transacao: datetime
