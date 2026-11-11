"""Rotas HTTP do modulo de transacoes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import exigir_investidor
from app.db.session import get_db
from app.modules.assets.repository import AtivoRepository
from app.modules.auth.models import Usuario
from app.modules.investors.repository import InvestidorRepository
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.quotes.repository import CotacaoRepository
from app.modules.quotes.service import CotacaoService
from app.modules.transactions.repository import TransacaoRepository
from app.modules.transactions.schemas import TipoTransacao, TransacaoEntrada, TransacaoSaida
from app.modules.transactions.service import ErroTransacao, TransacaoService


router = APIRouter(prefix="/transactions", tags=["transactions"])


def obter_id_investidor(
    usuario: Usuario = Depends(exigir_investidor), db: Session = Depends(get_db),
) -> int:
    """Identifica o investidor pela sessao, sem aceitar ID enviado pelo cliente."""
    investidor = InvestidorRepository(db).buscar_por_usuario_id(usuario.id_usuario)
    if investidor is None:
        raise HTTPException(status_code=404, detail="Perfil de investidor não encontrado.")
    return investidor.id_investidor


def obter_servico(db: Session = Depends(get_db)) -> TransacaoService:
    """Monta o servico com os repositorios da mesma sessao."""
    return TransacaoService(
        TransacaoRepository(db), CarteiraRepository(db), AtivoRepository(db),
        CotacaoService(CotacaoRepository(db), AtivoRepository(db)),
    )


@router.post("", response_model=TransacaoSaida, status_code=status.HTTP_201_CREATED)
def registrar_transacao(
    dados: TransacaoEntrada,
    id_investidor: int = Depends(obter_id_investidor),
    service: TransacaoService = Depends(obter_servico),
):
    """Registra uma compra ou venda e atualiza a quantidade do ativo na carteira."""
    try:
        return service.registrar_transacao(dados, id_investidor)
    except ErroTransacao as erro:
        raise HTTPException(status_code=erro.status_code, detail=str(erro)) from erro


@router.get("", response_model=list[TransacaoSaida])
def listar_transacoes(
    id_carteira: int | None = None,
    ticker: str | None = None,
    tipo: TipoTransacao | None = None,
    id_investidor: int = Depends(obter_id_investidor),
    service: TransacaoService = Depends(obter_servico),
):
    """Consulta o historico de transacoes do investidor logado, com filtros opcionais."""
    return service.listar_transacoes(id_investidor, id_carteira, ticker, tipo)
