"""Testes unitarios de regras do TransactionService."""

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ProjectException
from app.modules.transactions.schemas import TransactionCreate
from app.modules.transactions.service import TransactionService


def _build_service() -> TransactionService:
    service = TransactionService(MagicMock())
    service.repository = MagicMock()
    service.portfolio_repository = MagicMock()
    service.investor_repository = MagicMock()
    service.asset_repository = MagicMock()
    return service


def test_create_transaction_bloqueia_venda_acima_do_saldo() -> None:
    service = _build_service()
    user = SimpleNamespace(id=1, role="analyst")
    service.portfolio_repository.get_by_id.return_value = SimpleNamespace(
        id=10,
        investor_id=2,
        is_active=True,
    )
    service.investor_repository.get_by_id.return_value = SimpleNamespace(
        id=2,
        user_id=1,
        account_user_id=None,
    )
    service.asset_repository.get_by_id.return_value = SimpleNamespace(
        id=5,
        is_active=True,
    )
    service.repository.get_asset_quantity.return_value = Decimal("1")

    payload = TransactionCreate(
        portfolio_id=10,
        asset_id=5,
        transaction_type="venda",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
        transaction_date=datetime(2026, 1, 1),
        fees=Decimal("0"),
    )

    with pytest.raises(ProjectException, match="disponivel"):
        service.create_transaction(user, payload)  # type: ignore[arg-type]


def test_create_transaction_exige_ativo_em_compra() -> None:
    service = _build_service()
    user = SimpleNamespace(id=1, role="analyst")
    service.portfolio_repository.get_by_id.return_value = SimpleNamespace(
        id=10,
        investor_id=2,
        is_active=True,
    )
    service.investor_repository.get_by_id.return_value = SimpleNamespace(
        id=2,
        user_id=1,
        account_user_id=None,
    )

    payload = TransactionCreate(
        portfolio_id=10,
        asset_id=None,
        transaction_type="compra",
        quantity=Decimal("1"),
        unit_price=Decimal("10"),
        transaction_date=datetime(2026, 1, 1),
        fees=Decimal("0"),
    )

    with pytest.raises(ProjectException, match="exige asset_id"):
        service.create_transaction(user, payload)  # type: ignore[arg-type]
