"""Testes unitarios dos validadores compartilhados."""

from decimal import Decimal

from app.shared.validators import (
    is_non_negative,
    is_positive_number,
    is_valid_asset_type,
    is_valid_transaction_type,
)


def test_is_non_negative_aceita_zero_e_positivos() -> None:
    assert is_non_negative(0) is True
    assert is_non_negative(Decimal("10.5")) is True


def test_is_non_negative_rejeita_negativos() -> None:
    assert is_non_negative(-1) is False


def test_is_positive_number() -> None:
    assert is_positive_number(1) is True
    assert is_positive_number(0) is False
    assert is_positive_number(-2) is False


def test_is_valid_asset_type() -> None:
    assert is_valid_asset_type("acao") is True
    assert is_valid_asset_type("invalido") is False


def test_is_valid_transaction_type() -> None:
    assert is_valid_transaction_type("compra") is True
    assert is_valid_transaction_type("bonus") is False
