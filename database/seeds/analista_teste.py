"""Conta fixa de desenvolvimento para acessar a interface apos um reset."""
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.db import registrar_modelos
from app.modules.analysts.models import Analista
from app.modules.analysts.repository import AnalistaRepository
from app.modules.analysts.schemas import CadastroAnalistaEntrada
from app.modules.analysts.service import AnalistaService

# Credenciais de teste solicitadas para a preparacao do banco local.
EMAIL_ANALISTA_TESTE = "analista@teste.local"
USUARIO_ANALISTA_TESTE = "analista"
SENHA_ANALISTA_TESTE = "12345"


def criar_analista_teste(engine: Engine) -> int:
    """Cria o analista padrao pelo fluxo de cadastro, sem duplicar a mesma conta."""
    registrar_modelos()
    with Session(engine) as sessao:
        repository = AnalistaRepository(sessao)
        por_email = repository.buscar_usuario_por_email(EMAIL_ANALISTA_TESTE)
        por_usuario = repository.buscar_usuario_por_nome_usuario(USUARIO_ANALISTA_TESTE)
        if por_email is not None or por_usuario is not None:
            if (
                isinstance(por_email, Analista)
                and por_usuario is not None
                and por_email.id_usuario == por_usuario.id_usuario
                and por_email.nome_usuario == USUARIO_ANALISTA_TESTE
            ):
                return por_email.id_analista
            raise ValueError("As credenciais do analista de teste pertencem a outra conta.")

        analista, erro = AnalistaService(repository).cadastrar_analista(
            CadastroAnalistaEntrada(
                nome="Analista de Teste",
                email=EMAIL_ANALISTA_TESTE,
                nome_usuario=USUARIO_ANALISTA_TESTE,
                senha=SENHA_ANALISTA_TESTE,
            ),
        )
        if erro is not None or analista is None:
            raise ValueError(erro or "Não foi possível criar o analista de teste.")
        return analista.id_analista
