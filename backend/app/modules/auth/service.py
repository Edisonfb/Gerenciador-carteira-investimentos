from app.modules.auth.repository import AuthRepository
from app.core.security import verificar_senha

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def realizar_login(self, email: str, senha: str):
        usuario = self.repository.buscar_por_email(email)

        if usuario is None:
            return None

        senha_correta = verificar_senha(senha, usuario.senha_hash)

        if not senha_correta:
            return None

        return {
            "access_token": str(usuario.id_usuario),
            "token_type": "bearer"
        }