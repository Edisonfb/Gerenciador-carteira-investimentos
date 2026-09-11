"""Validadores compartilhados entre os modulos da aplicacao."""

from decimal import Decimal


ASSET_TYPES = {
    "acao",
    "fundo_imobiliario",
    "renda_fixa",
    "etf",
    "cripto",
    "outro",
}

TRANSACTION_TYPES = {
    "compra",
    "venda",
    "deposito",
    "retirada",
    "rendimento",
    "taxa",
}

ASSET_REQUIRED_TYPES = {"compra", "venda", "rendimento"}


def is_non_negative(value: Decimal | float | int) -> bool:
    """Verifica se um numero e maior ou igual a zero."""
    return Decimal(str(value)) >= 0


def is_positive_number(value: Decimal | float | int) -> bool:
    """Verifica se um numero e maior que zero."""
    return Decimal(str(value)) > 0


def is_valid_asset_type(asset_type: str) -> bool:
    """Valida o tipo de ativo financeiro."""
    return asset_type in ASSET_TYPES


def is_valid_transaction_type(transaction_type: str) -> bool:
    """Valida o tipo de transacao."""
    return transaction_type in TRANSACTION_TYPES
