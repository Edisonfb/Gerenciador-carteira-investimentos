from app.modules.auth.repository import AuthRepository
from app.core.security import criar_token_acesso, verificar_senha
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import UsuarioUpdate

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def realizar_login(self, email: str, senha: str):
        usuario = self.repository.buscar_por_email(email)

        if usuario is None:
            return None

        if not usuario.ativo:
            return False

        senha_correta = verificar_senha(senha, usuario.senha_hash)

        if not senha_correta:
            return None


        return {
            "access_token": criar_token_acesso(usuario.id_usuario),
            "token_type": "bearer"
        }

    def listar_usuarios(self) -> list[Usuario]:
        return self.repository.listar_todos()

    def get_usuario_por_id(self, id_usuario: int) -> Usuario | None:
        return self.repository.buscar_por_id(id_usuario)

    def atualizar_usuario(self, id_usuario: int, dados: UsuarioUpdate) -> Usuario | None:
        usuario = self.repository.buscar_por_id(id_usuario)

        if usuario is None:
            return None

        dados_dict = dados.model_dump(exclude_unset=True)

        for campo, valor in dados_dict.items():
            setattr(usuario, campo, valor)

        self.repository.salvar(usuario)
        return usuario
