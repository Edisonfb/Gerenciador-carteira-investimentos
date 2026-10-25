"""Rotas HTTP do modulo de carteiras."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import exigir_investidor
from app.db.session import get_db
from app.modules.auth.models import Usuario
from app.modules.investors.repository import InvestidorRepository
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.portfolios.schemas import (
    CarteiraAtualizacaoEntrada,
    CarteiraCadastroEntrada,
    CarteiraSaida
)
from app.modules.portfolios.service import CarteiraService


router = APIRouter(prefix="/portfolios", tags=["portfolios"])

def obter_id_investidor_logado(usuario: Usuario, db: Session) -> int:
    """Busca o perfil de investidor relacionado ao usuario autenticado."""
    investidor = InvestidorRepository(db).buscar_por_usuario_id(usuario.id_usuario)

    if investidor is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Perfil de investidor não encontrado."
        )

    return investidor.id_investidor

@router.post("", response_model = CarteiraSaida, status_code = status.HTTP_201_CREATED)
def criar_carteira(dados: CarteiraCadastroEntrada, usuario: Usuario = Depends(exigir_investidor), 
                   db: Session = Depends(get_db)):
    id_investidor = obter_id_investidor_logado(usuario, db)

    service = CarteiraService(CarteiraRepository(db))
    carteira, erro = service.criar_carteira(dados, id_investidor)

    if erro is not None or carteira is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = erro or "Não foi possível criar a carteira."
        )
    return carteira

@router.get("", response_model = list[CarteiraSaida])
def listar_carteiras(
    usuario: Usuario = Depends(exigir_investidor),
    db:  Session = Depends(get_db)
):
    id_investidor = obter_id_investidor_logado(usuario, db)

    service = CarteiraService(CarteiraRepository(db))
    return service.listar_carteiras(id_investidor)

@router.get("/{id_carteira}", response_model = CarteiraSaida)
def buscar_carteira(
    id_carteira: int,
    usuario: Usuario = Depends(exigir_investidor),
    db: Session = Depends(get_db)
):
    id_investidor = obter_id_investidor_logado(usuario, db)
    service = CarteiraService(CarteiraRepository(db))
    carteira = service.buscar_carteira(id_carteira, id_investidor)

    if carteira is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Carteira não encontrada"
        )
    return carteira

@router.patch("/{id_carteira}", response_model = CarteiraSaida)
def atualizar_carteira(
    id_carteira: int,
    dados: CarteiraAtualizacaoEntrada,
    usuario: Usuario = Depends(exigir_investidor),
    db: Session = Depends(get_db)
):
    id_investidor = obter_id_investidor_logado(usuario, db)

    service = CarteiraService(CarteiraRepository(db))
    carteira, erro = service.atualizar_carteira(
        id_carteira,
        id_investidor,
        dados
    )
    if erro is not None or carteira is None:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if erro == "Carteira não encontrada"
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code = status_code,
            detail = erro or "Não foi possível atualizar a carteira."
        )

    return carteira

@router.delete("/{id_carteira}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_carteira(
    id_carteira: int,
    usuario: Usuario = Depends(exigir_investidor),
    db: Session = Depends(get_db),
):
    id_investidor = obter_id_investidor_logado(usuario, db)

    service = CarteiraService(CarteiraRepository(db))
    carteira_excluida = service.excluir_carteira(id_carteira, id_investidor)

    if not carteira_excluida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carteira não encontrada.",
        )