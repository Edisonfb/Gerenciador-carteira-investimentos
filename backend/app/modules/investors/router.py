"""Rotas HTTP do modulo de investidores."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import (
    CadastroInvestidorEntrada,
    InvestidorSaida,
    MeuPerfilInvestidorAtualizacao,
    MeuPerfilInvestidorSaida,
)
from app.modules.investors.service import InvestidorService
from app.core.dependencies import exigir_investidor
from app.modules.auth.models import Usuario


router = APIRouter(prefix="/investors", tags=["investors"])


def _perfil_para_resposta(investidor):
    return {
        "id_investidor": investidor.id_investidor,
        "id_usuario": investidor.id_usuario,
        "id_analista_responsavel": investidor.id_analista_responsavel,
        "email": investidor.email,
        "tipo_usuario": investidor.tipo_usuario.value,
        "ativo": investidor.ativo,
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
    investidor = repository.buscar_por_usuario_id(usuario.id_usuario)
    if investidor is None:
        raise HTTPException(status_code=404, detail="Perfil de investidor não encontrado.")

    atualizacoes = dados.model_dump(exclude_unset=True)
    email = atualizacoes.pop("email", None)
    if email is not None:
        usuario.email = email
    for campo, valor in atualizacoes.items():
        if valor is not None:
            setattr(investidor, campo, valor)
    repository.atualizar(investidor)
    return _perfil_para_resposta(investidor)


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