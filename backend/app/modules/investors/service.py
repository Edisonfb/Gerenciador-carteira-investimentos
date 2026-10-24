"""Regras de negocio do modulo de investidores."""
import secrets
import logging
import smtplib

from app.core.config import settings

from app.core.security import hash_senha
from app.db.enums import Tipo_Usuario
from app.shared import email_service
from app.modules.investors.models import Investidor
from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import CadastroInvestidorEntrada



class InvestidorService:
    def __init__(self, repository: InvestidorRepository):
        self.repository = repository
        self.email_acesso_enviado = False

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
            senha_hash=hash_senha(token_inicial),
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

        if settings.servidor_smtp and settings.email_remetente:
            try:
                email_service.enviar_token_acesso(dados.email, dados.nome, token_inicial)
                self.email_acesso_enviado = True
            except (smtplib.SMTPException, OSError, ValueError) as erro:
                logging.getLogger(__name__).warning(
                    "Investidor cadastrado, mas o envio do e-mail de acesso falhou. Tipo: %s; código SMTP: %s.",
                    type(erro).__name__,
                    getattr(erro, "smtp_code", "indisponível"),
                )

        return investidor_salvo, None