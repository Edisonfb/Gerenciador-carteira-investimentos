"""Rotas autenticadas do catalogo e dos ativos de carteiras."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import exigir_investidor
from app.db.session import get_db
from app.modules.auth.models import Usuario
from app.modules.assets.repository import AtivoCarteiraRepository, AtivoRepository
from app.modules.assets.schemas import (
    AtivoCarteiraSaida, AtivoCarteiraUpdate, AtivoSaida,
    CadastroAtivoCarteiraEntrada, Ticker,
)
from app.modules.assets.service import AtivoCarteiraService, AtivoService, ErroAtivo
from app.modules.investors.repository import InvestidorRepository
from app.modules.portfolios.repository import CarteiraRepository

router = APIRouter(
    prefix="/assets", tags=["assets"], dependencies=[Depends(exigir_investidor)],
)


def obter_id_investidor(
    usuario: Usuario = Depends(exigir_investidor), db: Session = Depends(get_db),
) -> int:
    """Identifica o perfil usando a sessao, sem aceitar ID do cliente."""
    investidor = InvestidorRepository(db).buscar_por_usuario_id(usuario.id_usuario)
    if investidor is None:
        raise HTTPException(status_code=404, detail="Perfil de investidor não encontrado.")
    return investidor.id_investidor


def obter_servico_carteira(db: Session = Depends(get_db)) -> AtivoCarteiraService:
    """Monta o servico com os repositorios da mesma sessao."""
    return AtivoCarteiraService(
        AtivoCarteiraRepository(db), CarteiraRepository(db), AtivoRepository(db),
    )


@router.get("", response_model=list[AtivoSaida])
def listar_ativos(
    codigo: str | None = None, ticker: str | None = None,
    db: Session = Depends(get_db),
):
    """Lista o catalogo e aceita codigo como alias de consulta por ticker."""
    if codigo is not None and ticker is not None and codigo.strip().upper() != ticker.strip().upper():
        raise HTTPException(status_code=422, detail="Informe apenas um código de ativo.")
    return AtivoService(AtivoRepository(db)).listar_ativos(
        codigo=ticker if ticker is not None else codigo,
    )


@router.get("/setor/{setor}", response_model=list[AtivoSaida])
def buscar_ativos_por_setor(setor: str, db: Session = Depends(get_db)):
    """Recupera a consulta por setor implementada na branch backup."""
    return AtivoService(AtivoRepository(db)).buscar_por_setor(setor)


@router.post("/carteira", response_model=AtivoCarteiraSaida, status_code=status.HTTP_201_CREATED)
def cadastrar_ativo_carteira(
    dados: CadastroAtivoCarteiraEntrada,
    id_investidor: int = Depends(obter_id_investidor),
    service: AtivoCarteiraService = Depends(obter_servico_carteira),
):
    """Adiciona um ativo a uma carteira do investidor autenticado."""
    try:
        return service.cadastrar_ativo_carteira(dados, id_investidor)
    except ErroAtivo as erro:
        raise HTTPException(status_code=erro.status_code, detail=str(erro)) from erro


@router.get("/carteira/{id_carteira}", response_model=list[AtivoCarteiraSaida])
def listar_ativos_carteira(
    id_carteira: int, id_investidor: int = Depends(obter_id_investidor),
    service: AtivoCarteiraService = Depends(obter_servico_carteira),
):
    """Consulta apenas ativos de uma carteira do investidor autenticado."""
    try:
        return service.listar_ativos_carteira(id_carteira, id_investidor)
    except ErroAtivo as erro:
        raise HTTPException(status_code=erro.status_code, detail=str(erro)) from erro


@router.patch(
    "/carteira/{id_carteira}/{ticker}", response_model=AtivoCarteiraSaida,
    responses={204: {"description": "Ativo removido da carteira por quantidade zero."}},
)
def atualizar_quantidade_ativo(
    id_carteira: int, ticker: Ticker, dados: AtivoCarteiraUpdate,
    id_investidor: int = Depends(obter_id_investidor),
    service: AtivoCarteiraService = Depends(obter_servico_carteira),
):
    """Atualiza a quantidade na carteira propria ou remove o vinculo com zero."""
    try:
        vinculo = service.atualizar_quantidade(id_carteira, ticker, dados, id_investidor)
    except ErroAtivo as erro:
        raise HTTPException(status_code=erro.status_code, detail=str(erro)) from erro
    if vinculo is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return vinculo


@router.delete("/carteira/{id_carteira}/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def remover_ativo_carteira(
    id_carteira: int, ticker: Ticker,
    id_investidor: int = Depends(obter_id_investidor),
    service: AtivoCarteiraService = Depends(obter_servico_carteira),
):
    """Remove somente o ativo da carteira pertencente ao investidor logado."""
    try:
        service.remover_ativo_carteira(id_carteira, ticker, id_investidor)
    except ErroAtivo as erro:
        raise HTTPException(status_code=erro.status_code, detail=str(erro)) from erro
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{ticker}", response_model=AtivoSaida)
def buscar_ativo(ticker: str, db: Session = Depends(get_db)):
    """Consulta o ativo pelo ticker e retorna 404 quando ausente."""
    ativo = AtivoService(AtivoRepository(db)).buscar_ativos(ticker)
    if ativo is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado.")
    return ativo
