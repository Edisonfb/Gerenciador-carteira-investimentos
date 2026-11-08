"""Rotas HTTP do modulo de investidores."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import (
    CadastroInvestidorEntrada,
    CadastroPrimeiroAcessoEntrada,
    InvestidorSaida,
    MeuPerfilInvestidorAtualizacao,
    MeuPerfilInvestidorSaida,
    PrimeiroAcessoInvestidorEntrada,
)
from app.modules.investors.service import InvestidorService
from app.modules.investors.primeiro_acesso_service import concluir_cadastro_com_token
from app.modules.auth.models import Usuario
from app.core.dependencies import exigir_investidor, exigir_analista
from app.modules.analysts.repository import AnalistaRepository


router = APIRouter(prefix="/investors", tags=["investors"])


def _perfil_para_resposta(investidor):
    return {
        "id_investidor": investidor.id_investidor,
        "id_usuario": investidor.id_usuario,
        "id_analista_responsavel": investidor.id_analista_responsavel,
        "email": investidor.email,
        "nome_usuario": investidor.nome_usuario,
        "email_recuperacao": investidor.email_recuperacao,
        "tipo_usuario": investidor.tipo_usuario.value,
        "ativo": investidor.ativo,
        "primeiro_acesso_concluido": investidor.primeiro_acesso_concluido,
        "nome": investidor.nome,
        "sobrenome": investidor.sobrenome,
        "cpf": investidor.cpf,
        "telefone": investidor.telefone,
        "cep": investidor.cep,
        "uf": investidor.uf,
        "cidade": investidor.cidade,
        "bairro": investidor.bairro,
        "logradouro": investidor.logradouro,
        "numero": investidor.numero,
    }


@router.get("/me", response_model=MeuPerfilInvestidorSaida)
def obter_meu_perfil(
    usuario: Usuario = Depends(exigir_investidor), db: Session = Depends(get_db)
):
    investidor = InvestidorRepository(db).buscar_por_usuario_id(usuario.id_usuario)
    if investidor is None:
        raise HTTPException(status_code=404, detail="Perfil de investidor não encontrado.")
    return _perfil_para_resposta(investidor)


@router.patch("/me", response_model=MeuPerfilInvestidorSaida)
def atualizar_meu_perfil(
    dados: MeuPerfilInvestidorAtualizacao,
    usuario: Usuario = Depends(exigir_investidor),
    db: Session = Depends(get_db),
):
    repository = InvestidorRepository(db)
    try:
        investidor = InvestidorService(repository).atualizar_minha_conta(usuario.id_usuario, dados)
    except LookupError as erro:
        repository.desfazer()
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ValueError as erro:
        repository.desfazer()
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except IntegrityError as erro:
        repository.desfazer()
        raise HTTPException(status_code=409, detail="Usuário ou e-mail já cadastrado. Confira os dados informados.") from erro
    return _perfil_para_resposta(investidor)


@router.post("/first-access", status_code=status.HTTP_200_OK)
def concluir_cadastro_por_convite(dados: CadastroPrimeiroAcessoEntrada, db: Session = Depends(get_db)):
    """Salva os dados do investidor mediante prova do convite, sem emitir login."""
    repository = InvestidorRepository(db)
    try:
        concluir_cadastro_com_token(repository, dados)
    except ValueError as erro:
        repository.desfazer()
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except IntegrityError as erro:
        repository.desfazer()
        raise HTTPException(status_code=409, detail="Usuário ou e-mail já cadastrado. Confira os dados informados.") from erro
    return {"message": "Cadastro concluído com sucesso. Entre com seu usuário e senha."}


@router.post("/me/first-access", response_model=MeuPerfilInvestidorSaida)
def concluir_primeiro_acesso(
    dados: PrimeiroAcessoInvestidorEntrada,
    usuario: Usuario = Depends(exigir_investidor),
    db: Session = Depends(get_db),
):
    """Conclui o primeiro acesso do investidor autenticado."""
    repository = InvestidorRepository(db)
    service = InvestidorService(repository)

    investidor, erro = service.concluir_primeiro_acesso(usuario.id_usuario, dados)

    if erro is not None or investidor is None:
        status_code = 404 if erro == "Perfil de investidor não encontrado." else 400
        raise HTTPException(
            status_code=status_code,
            detail=erro or "Não foi possível concluir o primeiro acesso.",
        )

    return _perfil_para_resposta(investidor)


@router.post("", response_model=InvestidorSaida, status_code=201)
def cadastrar_investidor(
    dados: CadastroInvestidorEntrada,
    usuario: Usuario = Depends(exigir_analista),
    db: Session = Depends(get_db),
):
    if usuario.tipo_usuario.value != "analista":
        raise HTTPException(status_code=403, detail="Apenas analistas podem cadastrar investidores.")
    repository = InvestidorRepository(db)
    analista = repository.buscar_analista_por_usuario(usuario.id_usuario)
    if analista is None:
        raise HTTPException(status_code=404, detail="Perfil de analista não encontrado.")
    dados = dados.model_copy(update={"id_analista_responsavel": analista.id_analista})
    service = InvestidorService(repository)

    analista = AnalistaRepository(db).buscar_por_usuario_id(usuario.id_usuario)

    if analista is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de analista não encontrado.",
        )

    investidor, erro = service.cadastrar_investidor(dados, analista.id_analista)

    if erro is not None or investidor is None:
        raise HTTPException(
            status_code = 400,
            detail = erro or "Não foi possível cadastrar o investidor.",
        )

    return {
        "email_acesso_enviado": service.email_acesso_enviado,
        "id_investidor": investidor.id_investidor,
        "id_usuario": investidor.id_usuario,
        "email": investidor.email,
        "nome_usuario": investidor.nome_usuario,
        "primeiro_acesso_concluido": investidor.primeiro_acesso_concluido,
    }

@router.delete("/{id_investidor}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_investidor( id_investidor:int, db: Session = Depends(get_db)):
    repository = InvestidorRepository(db)
    service = InvestidorService(repository)

    investidor_excluido = service.excluir_investidor(id_investidor)

    if not investidor_excluido:
        raise HTTPException(
            status_code=404,
            detail= "Investidor não encontrado."
        )
