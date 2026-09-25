"""Rotas HTTP do modulo de investidores."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import CadastroInvestidorEntrada, InvestidorSaida
from app.modules.investors.service import InvestidorService


router = APIRouter(prefix="/investors", tags=["investors"])


@router.post("", response_model= InvestidorSaida, status_code=201)
def cadastrar_investidor(
    dados: CadastroInvestidorEntrada,
    db: Session = Depends(get_db),
):
    repository = InvestidorRepository(db)
    service = InvestidorService(repository)

    investidor, erro = service.cadastrar_investidor(dados)

    if erro is not None or investidor is None:
        raise HTTPException(
            status_code = 400,
            detail = erro or "Não foi possível cadastrar o investidor.",
        )

    return {
        "id_investidor": investidor.id_investidor,
        "id_usuario": investidor.id_usuario,
        "nome": investidor.nome,
        "sobrenome": investidor.sobrenome,
        "email": investidor.email,
        "cpf": investidor.cpf,
        "telefone": investidor.telefone,
    }