"""Rotas HTTP do modulo de investidores."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_analyst, get_current_user, get_db
from app.modules.auth.models import User
from app.modules.investors.models import Investor
from app.modules.investors.schemas import (
    InvestorAccessResponse,
    InvestorCreate,
    InvestorResponse,
    InvestorUpdate,
)
from app.modules.investors.service import InvestorService

router = APIRouter(prefix="/investors", tags=["investors"])


def _with_access(investor: Investor, temporary_password: str) -> InvestorAccessResponse:
    """Monta resposta incluindo senha temporaria."""
    base = InvestorResponse.model_validate(investor)
    return InvestorAccessResponse(
        **base.model_dump(),
        temporary_password=temporary_password,
    )


@router.get("", response_model=list[InvestorResponse])
def list_investors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Investor]:
    """Lista clientes do analista ou o proprio perfil do cliente."""
    return InvestorService(db).list_investors(current_user)


@router.get("/{investor_id}", response_model=InvestorResponse)
def get_investor(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Investor:
    return InvestorService(db).get_investor(current_user, investor_id)


@router.post("", response_model=InvestorAccessResponse, status_code=201)
def create_investor(
    payload: InvestorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst),
) -> InvestorAccessResponse:
    """Pre-cadastra cliente e devolve senha temporaria (exibida uma vez)."""
    investor, temporary_password = InvestorService(db).create_investor(
        current_user,
        payload,
    )
    return _with_access(investor, temporary_password)


@router.post("/{investor_id}/regenerate-access", response_model=InvestorAccessResponse)
def regenerate_access(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst),
) -> InvestorAccessResponse:
    """Reemite senha temporaria do cliente."""
    investor, temporary_password = InvestorService(db).regenerate_access(
        current_user,
        investor_id,
    )
    return _with_access(investor, temporary_password)


@router.put("/{investor_id}", response_model=InvestorResponse)
def update_investor(
    investor_id: int,
    payload: InvestorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst),
) -> Investor:
    return InvestorService(db).update_investor(current_user, investor_id, payload)


@router.delete("/{investor_id}", response_model=InvestorResponse)
def delete_investor(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_analyst),
) -> Investor:
    return InvestorService(db).delete_investor(current_user, investor_id)
