"""Rotas HTTP do modulo de carteiras."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.modules.auth.models import User
from app.modules.portfolios.models import Portfolio
from app.modules.portfolios.schemas import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummaryResponse,
    PortfolioUpdate,
)
from app.modules.portfolios.service import PortfolioService

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("", response_model=list[PortfolioResponse])
def list_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Portfolio]:
    return PortfolioService(db).list_portfolios(current_user)


@router.get("/{portfolio_id}/summary", response_model=PortfolioSummaryResponse)
def get_portfolio_summary(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioSummaryResponse:
    return PortfolioService(db).get_summary(current_user, portfolio_id)


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Portfolio:
    return PortfolioService(db).get_portfolio(current_user, portfolio_id)


@router.post("", response_model=PortfolioResponse, status_code=201)
def create_portfolio(
    payload: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Portfolio:
    return PortfolioService(db).create_portfolio(current_user, payload)


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    payload: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Portfolio:
    return PortfolioService(db).update_portfolio(current_user, portfolio_id, payload)


@router.delete("/{portfolio_id}", response_model=PortfolioResponse)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Portfolio:
    return PortfolioService(db).delete_portfolio(current_user, portfolio_id)
