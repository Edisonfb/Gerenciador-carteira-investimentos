"""Regras de negocio do modulo de investidores."""
import secrets
import re
import logging
import smtplib

from app.core.config import settings

from app.core.security import hash_senha, verificar_senha
from app.db.enums import Tipo_Usuario
from app.shared import email_service
from app.modules.investors.models import Investidor
from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import (
    CadastroInvestidorEntrada,
    MeuPerfilInvestidorAtualizacao,
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
            self.email_acesso_enviado = True

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
        email_comunicacao = (dados.email_comunicacao if dados.email_comunicacao is not None else investidor.email).strip().lower()

        if len(nome_usuario) > 50:
            return None, "O nome de usuário deve ter no máximo 50 caracteres."

        if not nome_usuario:
            return None, "O nome de usuário é obrigatório."

        usuario_com_nome = self.repository.buscar_usuario_por_nome_usuario(nome_usuario)
        if usuario_com_nome is not None and usuario_com_nome.id_usuario != investidor.id_usuario:
            return None, "Já existe um usuário com este nome de usuário."

        if not email_recuperacao:
            return None, "O e-mail de recuperação é obrigatório."

        if email_recuperacao == email_comunicacao:
            return None, "O e-mail de recuperação deve ser diferente do e-mail principal."

        if not dados.nova_senha.strip():
            return None, "A nova senha é obrigatória."

        if len(dados.nova_senha) < 8 or len(dados.nova_senha.encode("utf-8")) > 72:
            return None, "A senha deve ter no mínimo 8 caracteres e no máximo 72 bytes."
        usuario_comunicacao = self.repository.buscar_usuario_por_email(email_comunicacao)
        if usuario_comunicacao is not None and usuario_comunicacao.id_usuario != investidor.id_usuario:
            return None, "Já existe um usuário com este e-mail de comunicação."
        recuperacao_comunicacao = self.repository.buscar_por_email_recuperacao(email_comunicacao)
        if recuperacao_comunicacao is not None and recuperacao_comunicacao.id_usuario != investidor.id_usuario:
            return None, "O e-mail de comunicação já está em uso como e-mail de recuperação."

        usuario_com_email = self.repository.buscar_usuario_por_email(email_recuperacao)
        if usuario_com_email is not None and usuario_com_email.id_usuario != investidor.id_usuario:
            return None, "O e-mail de recuperação já está cadastrado como e-mail principal."

        investidor_com_email = self.repository.buscar_por_email_recuperacao(email_recuperacao)
        if investidor_com_email is not None and investidor_com_email.id_usuario != investidor.id_usuario:
            return None, "Este e-mail de recuperação já está em uso."

        investidor.email = email_comunicacao
        investidor.nome_usuario = nome_usuario
        investidor.email_recuperacao = email_recuperacao
        investidor.senha_hash = hash_senha(dados.nova_senha)
        investidor.primeiro_acesso_concluido = True

        return self.repository.atualizar(investidor), None

    def atualizar_minha_conta(self, id_usuario: int, dados: MeuPerfilInvestidorAtualizacao) -> Investidor:
        """Valida a conta inteira antes de persistir, preservando campos omitidos."""
        investidor = self.repository.buscar_por_usuario_id_para_atualizacao(id_usuario)
        if investidor is None:
            raise LookupError("Perfil de investidor não encontrado.")
        campos = dados.model_dump(exclude_unset=True)
        campos_conta = {"nome_usuario", "email", "email_recuperacao", "nova_senha"}
        altera_conta = bool(campos_conta.intersection(campos))
        senha_atual = campos.pop("senha_atual", None)
        nova_senha = campos.pop("nova_senha", None)
        novo_hash = None
        if altera_conta:
            if not senha_atual or len(senha_atual.encode("utf-8")) > 72 or not verificar_senha(senha_atual, investidor.senha_hash):
                raise ValueError("Senha atual inválida. Confira a senha para confirmar as alterações.")
            if any(campos[campo] is None for campo in campos_conta.intersection(campos)):
                raise ValueError("Os dados da conta não podem ser nulos.")
            nome = normalizar_nome_usuario(campos.get("nome_usuario", investidor.nome_usuario) or "")
            email = (campos.get("email", investidor.email) or "").strip().lower()
            recuperacao = (campos.get("email_recuperacao", investidor.email_recuperacao) or "").strip().lower()
            if not nome or len(nome) > 50:
                raise ValueError("Informe um usuário de até 50 caracteres.")
            if any(len(valor) > 255 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor) for valor in (email, recuperacao)):
                raise ValueError("Informe e-mails de comunicação e recuperação válidos.")
            if email == recuperacao:
                raise ValueError("O e-mail de recuperação deve ser diferente do e-mail de comunicação.")
            outro = self.repository.buscar_usuario_por_nome_usuario(nome)
            if outro is not None and outro.id_usuario != id_usuario:
                raise ValueError("Já existe um usuário com este nome de usuário.")
            for endereco in (email, recuperacao):
                usuario = self.repository.buscar_usuario_por_email(endereco)
                dono_recuperacao = self.repository.buscar_por_email_recuperacao(endereco)
                if ((usuario is not None and usuario.id_usuario != id_usuario)
                    or (dono_recuperacao is not None and dono_recuperacao.id_usuario != id_usuario)):
                    raise ValueError("Um dos e-mails informados já está em uso por outra conta.")
            if nova_senha:
                if not nova_senha.strip() or len(nova_senha) < 8 or len(nova_senha.encode("utf-8")) > 72:
                    raise ValueError("A nova senha deve ter no mínimo 8 caracteres e no máximo 72 bytes.")
                novo_hash = hash_senha(nova_senha)
            campos.update(nome_usuario=nome, email=email, email_recuperacao=recuperacao)
        for campo, valor in campos.items():
            if valor is not None:
                setattr(investidor, campo, valor)
        if novo_hash is not None:
            investidor.senha_hash = novo_hash
        return self.repository.atualizar(investidor)

    # Exclui um investidor do banco de dados utilizando o id
    # Primeiro verifica se existe alguém com esse id no banco e depois exclui
    # Retorna True caso tenha excluído e False caso o investidor não exista no banco
    def excluir_investidor(self, id_investidor: int) -> bool:
        investidor = self.repository.buscar_por_id(id_investidor)

        if investidor is None:
            return False

        self.repository.excluir(investidor)
        return True
