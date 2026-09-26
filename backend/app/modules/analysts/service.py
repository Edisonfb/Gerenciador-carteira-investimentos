from app.db.enums import Tipo_Usuario
from app.modules.analysts.models import Analista
from app.modules.analysts.repository import AnalistaRepository
from app.modules.analysts.schemas import CadastroAnalistaEntrada
from app.core.security import hash_senha

class AnalistaService:
    def __init__(self, repository: AnalistaRepository):
        self.repository = repository

    def cadastrar_analista(self, dados: CadastroAnalistaEntrada) -> tuple[Analista | None, str | None]:
        usuario_existente = self.repository.buscar_por_email(dados.email)

        if usuario_existente is not None:
            return None, "Já existe um usuário com este e-mail."

        analista = Analista(
            email=dados.email,
            senha_hash=hash_senha(dados.senha),
            tipo_usuario=Tipo_Usuario.ANALISTA,
            nome=dados.nome,
        )

        analista_salvo = self.repository.salvar(analista)

        return analista_salvo, None