"""Regras de negocio do modulo de investidores."""
import secrets

from app.db.enums import Tipo_Usuario
from app.modules.investors.models import Investidor
from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import CadastroInvestidorEntrada


class InvestidorService:
    def __init__(self, repository: InvestidorRepository):
        self.repository = repository

    def cadastrar_investidor(self, dados: CadastroInvestidorEntrada) -> tuple[Investidor | None, str | None]:
        usuario_existente = self.repository.buscar_usuario_por_email(dados.email)

        if usuario_existente is not None:
            return None, "Já existe um usuário com este e-mail."

        investidor_existente = self.repository.buscar_investidor_por_cpf(dados.cpf)

        if investidor_existente is not None:
            return None, "Já existe um investidor com este CPF."

        token_inicial = secrets.token_urlsafe(8)

        investidor = Investidor(
            email=dados.email,
            senha_hash=token_inicial,
            tipo_usuario=Tipo_Usuario.INVESTIDOR,
            id_analista_responsavel=dados.id_analista_responsavel,
            nome=dados.nome,
            sobrenome=dados.sobrenome,
            rg=dados.rg,
            cpf=dados.cpf,
            telefone=dados.telefone,
            cep=dados.cep,
            uf=dados.uf,
            cidade=dados.cidade,
            bairro=dados.bairro,
            logradouro=dados.logradouro,
            numero=dados.numero,
            token_acesso=token_inicial,
        )

        investidor_salvo = self.repository.salvar(investidor)

        return investidor_salvo, None