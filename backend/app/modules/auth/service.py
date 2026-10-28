from app.modules.auth.repository import AuthRepository
from app.core.security import criar_token_acesso, verificar_senha
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import UsuarioUpdate
from app.shared.usernames import normalizar_nome_usuario

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def realizar_login(self, email: str | None, nome_usuario: str | None, senha: str):
        usuario = None

        if email is not None:
            email_normalizado = email.strip().lower()
            if email_normalizado:
                usuario = self.repository.buscar_por_email(email_normalizado)

        if usuario is None and nome_usuario is not None:
            nome_usuario_normalizado = normalizar_nome_usuario(nome_usuario)
            if nome_usuario_normalizado:
                usuario = self.repository.buscar_por_nome_usuario(nome_usuario_normalizado)

        if usuario is None:
            return None

        if not usuario.ativo:
            return False

        # O token de convite deve ser trocado por uma senha no primeiro acesso.
        inicial = getattr(usuario, "token_acesso", None)
        if inicial and verificar_senha(inicial, usuario.senha_hash):
            return None

        senha_correta = verificar_senha(senha, usuario.senha_hash)

        if not senha_correta:
            return None


        return {
            "access_token": criar_token_acesso(usuario.id_usuario),
            "token_type": "bearer"
        }

    def realizar_logout(self, usuario: Usuario) -> dict:
        # O token JWT não fica salvo no servidor; o cliente deve descartá-lo.
        return {"mensagem": f"Sessão de {usuario.email} encerrada com sucesso."}

    def listar_usuarios(self) -> list[Usuario]:
        return self.repository.listar_todos()

    def get_usuario_por_id(self, id_usuario: int) -> Usuario | None:
        return self.repository.buscar_por_id(id_usuario)

    def atualizar_usuario(self, id_usuario: int, dados: UsuarioUpdate) -> tuple[Usuario | None, str | None]:
        usuario = self.repository.buscar_por_id(id_usuario)

        if usuario is None:
            return None, "Usuário não encontrado."

        dados_dict = dados.model_dump(exclude_unset=True)

        if "nome_usuario" in dados_dict and dados_dict["nome_usuario"] is not None:
            nome_usuario = normalizar_nome_usuario(dados_dict["nome_usuario"])

            if not nome_usuario:
                return None, "O nome de usuário é obrigatório."

            usuario_com_nome = self.repository.buscar_por_nome_usuario(nome_usuario)
            if usuario_com_nome is not None and usuario_com_nome.id_usuario != id_usuario:
                return None, "Já existe um usuário com este nome de usuário."

            dados_dict["nome_usuario"] = nome_usuario

        for campo, valor in dados_dict.items():
            setattr(usuario, campo, valor)

        self.repository.salvar(usuario)
        return usuario, None
