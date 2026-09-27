"""Rota para o analista enviar o token de primeiro acesso."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.primeiro_acesso.repository import PrimeiroAcessoRepository
from app.modules.auth.primeiro_acesso.schemas import EnviarTokenEntrada, EnviarTokenSaida
from app.modules.auth.primeiro_acesso.service import PrimeiroAcessoService

router = APIRouter(prefix="/auth/primeiro-acesso", tags=["auth"])
exigir_token = HTTPBearer(auto_error=False)


def obter_analista_autenticado(
    credenciais: HTTPAuthorizationCredentials | None = Depends(exigir_token),
    db: Session = Depends(get_db),
):
    if credenciais is None or not credenciais.credentials.isdigit():
        raise HTTPException(status_code=401, detail="Analista não autenticado.")

    repository = PrimeiroAcessoRepository(db)
    analista = repository.buscar_analista_por_usuario(int(credenciais.credentials))

    if analista is None:
        raise HTTPException(status_code=401, detail="Analista não autenticado.")

    return analista


@router.post("/enviar", response_model=EnviarTokenSaida)
def enviar_token_primeiro_acesso(
    dados: EnviarTokenEntrada,
    db: Session = Depends(get_db),
    _analista=Depends(obter_analista_autenticado),
):
    repository = PrimeiroAcessoRepository(db)
    service = PrimeiroAcessoService(repository)
    mensagem, erro = service.enviar_token(dados.id_investidor)

    if erro == "Investidor não encontrado.":
        raise HTTPException(status_code=404, detail=erro)

    if erro is not None or mensagem is None:
        raise HTTPException(
            status_code=400,
            detail=erro or "Não foi possível enviar o token de acesso.",
        )

    return {"mensagem": mensagem}
