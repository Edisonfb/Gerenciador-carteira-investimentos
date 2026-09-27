from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.analysts.repository import AnalistaRepository
from app.modules.analysts.schemas import CadastroAnalistaEntrada, AnalistaSaida, AnalistaUpdate
from app.modules.analysts.service import AnalistaService

router = APIRouter(prefix="/analysts", tags=["analysts"])

@router.post("", response_model=AnalistaSaida, status_code=201)
def cadastrar_analista(
    dados: CadastroAnalistaEntrada,
    db: Session = Depends(get_db),
):
    repository = AnalistaRepository(db)
    service = AnalistaService(repository)

    analista, erro = service.cadastrar_analista(dados)

    if erro is not None or analista is None:
        raise HTTPException(
            status_code=400,
            detail=erro or "Não foi possível cadastrar o analista.",
        )

    return {
        "id_analista": analista.id_analista,
        "id_usuario": analista.id_usuario,
        "nome": analista.nome,
        "email": analista.email,
        "ativo": analista.ativo,
    }

@router.get("/analistas", response_model=list[AnalistaSaida])
def listar_analistas(db: Session = Depends(get_db)):
    return AnalistaService(AnalistaRepository(db)).listar_analistas()

@router.get("/analistas/{id_analista}", response_model=AnalistaSaida)
def get_analista_por_id(id_analista: int, db: Session = Depends(get_db)):
    repository = AnalistaRepository(db)
    service = AnalistaService(repository)

    analista = service.get_analista_por_id(id_analista)
    if not analista:
        raise HTTPException(status_code=404, detail="Analista não encontrado")
    return analista

@router.patch("/analistas/{id_analista}", response_model=AnalistaUpdate)
def atualizar_analista(
    id_analista: int,
    dados: AnalistaUpdate,
    db: Session = Depends(get_db),
):
    repository = AnalistaRepository(db)
    service = AnalistaService(repository)

    analista = service.atualizar_analista(id_analista, dados)
    if not analista:
        raise HTTPException(status_code=404, detail="Analista não encontrado")
    return analista