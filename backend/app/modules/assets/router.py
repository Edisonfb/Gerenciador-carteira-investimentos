"""Rotas de consulta dos ativos financeiros."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.assets.repository import AtivoRepository, AtivoCarteiraRepository
from app.modules.assets.schemas import CadastroAtivoEntrada, AtivoSaida, CadastroAtivoCarteiraEntrada, AtivoCarteiraSaida
from app.modules.assets.service import AtivoService, AtivoCarteiraService

router = APIRouter(prefix="/assets", tags=["assets"])

@router.get("/assets", response_model=list[AtivoSaida])
def listar_ativos(db: Session = Depends(get_db)):
    return AtivoService(AtivoRepository(db)).listar_ativos()

@router.post("/assets/carteira", response_model=AtivoCarteiraSaida)
def cadastrar_ativo_carteira(dados: CadastroAtivoCarteiraEntrada, db: Session = Depends(get_db)):
    ativo_carteira_salvo = AtivoCarteiraService(AtivoCarteiraRepository(db)).cadastrar_ativo_carteira(dados)

    if ativo_carteira_salvo is None:
        raise HTTPException(status_code=400, detail="Erro ao cadastrar o ativo na carteira.")

    return ativo_carteira_salvo

@router.get("/assets/carteira/{id_carteira}", response_model=list[AtivoCarteiraSaida])
def listar_ativos_carteira(id_carteira: int, db: Session = Depends(get_db)):
    return AtivoCarteiraService(AtivoCarteiraRepository(db)).listar_por_carteira(id_carteira)
