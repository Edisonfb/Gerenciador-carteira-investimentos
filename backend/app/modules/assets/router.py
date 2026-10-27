"""Rotas de consulta dos ativos financeiros."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import exigir_investidor
from app.db.session import get_db
from app.modules.assets.repository import AtivoRepository
from app.modules.assets.schemas import AtivoSaida
from app.modules.assets.service import AtivoService


router = APIRouter(
    prefix="/assets",
    tags=["assets"],
    dependencies=[Depends(exigir_investidor)],
)


@router.get("", response_model=list[AtivoSaida])
def listar_ativos(
    codigo: str | None = None,
    db: Session = Depends(get_db),
):
    """Lista os ativos cadastrados para consulta pelo investidor."""
    service = AtivoService(AtivoRepository(db))

    return service.listar_ativos(codigo=codigo)


@router.get("/{id_ativo}", response_model=AtivoSaida)
def buscar_ativo(
    id_ativo: int,
    db: Session = Depends(get_db),
):
    """Consulta um ativo pelo identificador e retorna 404 se não existir."""
    service = AtivoService(AtivoRepository(db))
    ativo = service.buscar_ativos(id_ativo)

    if ativo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ativo não encontrado.",
        )

    return ativo