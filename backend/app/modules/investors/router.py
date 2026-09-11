"""Rotas HTTP do modulo de investidores."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.modules.auth.models import User
from app.modules.investors.models import Investor
from app.modules.investors.schemas import (
    InvestorCreate,
    InvestorResponse,
    InvestorUpdate,
)
from app.modules.investors.service import InvestorService

router = APIRouter(prefix="/investors", tags=["investors"])


@router.get("", response_model=list[InvestorResponse])
def list_investors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Investor]:
    return InvestorService(db).list_investors(current_user)


@router.get("/{investor_id}", response_model=InvestorResponse)
def get_investor(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Investor:
    return InvestorService(db).get_investor(current_user, investor_id)


@router.post("", response_model=InvestorResponse, status_code=201)
def create_investor(
    payload: InvestorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Investor:
    return InvestorService(db).create_investor(current_user, payload)


@router.put("/{investor_id}", response_model=InvestorResponse)
def update_investor(
    investor_id: int,
    payload: InvestorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Investor:
    return InvestorService(db).update_investor(current_user, investor_id, payload)


@router.delete("/{investor_id}", response_model=InvestorResponse)
def delete_investor(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Investor:
    return InvestorService(db).delete_investor(current_user, investor_id)
