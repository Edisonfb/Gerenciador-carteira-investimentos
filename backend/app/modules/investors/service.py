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
from app.modules.investors.schemas import (
    CadastroInvestidorEntrada,
    PrimeiroAcessoInvestidorEntrada,
)
from app.shared.usernames import normalizar_nome_usuario



class InvestidorService:
    def __init__(self, repository: InvestidorRepository):
        self.repository = repository
        self.email_acesso_enviado = False

    def cadastrar_investidor(
        self,
        dados: CadastroInvestidorEntrada,
        id_analista_responsavel: int,
    ) -> tuple[Investidor | None, str | None]:
        """Cadastra um investidor convidado usando apenas o e-mail."""
        email = dados.email.strip().lower()

        if not email:
            return None, "O e-mail do investidor é obrigatório."

        usuario_existente = self.repository.buscar_usuario_por_email(email)

        if usuario_existente is not None:
            return None, "Já existe um usuário com este e-mail."

        token_inicial = secrets.token_urlsafe(8)

        investidor = Investidor(
            email=email,
            senha_hash=hash_senha(token_inicial),
            tipo_usuario=Tipo_Usuario.INVESTIDOR,
            id_analista_responsavel=id_analista_responsavel,
            primeiro_acesso_concluido=False,
        )
        try:
            investidor_salvo = self.repository.adicionar(investidor)

            email_service.enviar_token_acesso(
                email,
                token_inicial,
            )
            self.repository.confirmar()

        except Exception:
            self.repository.desfazer()
            raise

        return investidor_salvo, None

    def concluir_primeiro_acesso(
        self,
        id_usuario: int,
        dados: PrimeiroAcessoInvestidorEntrada,
    ) -> tuple[Investidor | None, str | None]:
        """Troca o token inicial por senha definitiva e salva e-mail de recuperação."""
        investidor = self.repository.buscar_por_usuario_id(id_usuario)

        if investidor is None:
            return None, "Perfil de investidor não encontrado."

        if investidor.primeiro_acesso_concluido:
            return None, "O primeiro acesso deste investidor já foi concluído."

        nome_usuario = normalizar_nome_usuario(dados.nome_usuario)
        email_recuperacao = dados.email_recuperacao.strip().lower()

        if not nome_usuario:
            return None, "O nome de usuário é obrigatório."

        usuario_com_nome = self.repository.buscar_usuario_por_nome_usuario(nome_usuario)
        if usuario_com_nome is not None and usuario_com_nome.id_usuario != investidor.id_usuario:
            return None, "Já existe um usuário com este nome de usuário."

        if not email_recuperacao:
            return None, "O e-mail de recuperação é obrigatório."

        if email_recuperacao == investidor.email:
            return None, "O e-mail de recuperação deve ser diferente do e-mail principal."

        if not dados.nova_senha.strip():
            return None, "A nova senha é obrigatória."

        usuario_com_email = self.repository.buscar_usuario_por_email(email_recuperacao)
        if usuario_com_email is not None:
            return None, "O e-mail de recuperação já está cadastrado como e-mail principal."

        investidor_com_email = self.repository.buscar_por_email_recuperacao(email_recuperacao)
        if investidor_com_email is not None:
            return None, "Este e-mail de recuperação já está em uso."

        investidor.nome_usuario = nome_usuario
        investidor.email_recuperacao = email_recuperacao
        investidor.senha_hash = hash_senha(dados.nova_senha)
        investidor.primeiro_acesso_concluido = True

        return self.repository.atualizar(investidor), None

    # Exclui um investidor do banco de dados utilizando o id
    # Primeiro verifica se existe alguém com esse id no banco e depois exclui
    # Retorna True caso tenha excluído e False caso o investidor não exista no banco
    def excluir_investidor(self, id_investidor: int) -> bool:
        investidor = self.repository.buscar_por_id(id_investidor)

        if investidor is None:
            return False

        self.repository.excluir(investidor)
        return True
