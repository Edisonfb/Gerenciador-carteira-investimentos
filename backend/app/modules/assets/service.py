from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.assets.repository import AtivoRepository, AtivoCarteiraRepository
from app.modules.assets.schemas import CadastroAtivoEntrada, AtivoSaida, CadastroAtivoCarteiraEntrada, AtivoCarteiraSaida

class AtivoService:
    def __init__(self, repository: AtivoRepository):
        self.repository = repository

    def listar_ativos(self) -> list[Ativo]:
        return self.repository.listar_ativos()


class AtivoCarteiraService:
    def __init__(self, repository: AtivoCarteiraRepository):
        self.repository = repository

    def cadastrar_ativo_carteira(self, dados: CadastroAtivoCarteiraEntrada) -> AtivoCarteira | None:
        ativo_carteira = AtivoCarteira(
            ticker=dados.ticker,
            id_carteira=dados.id_carteira,
            quantidade=dados.quantidade,
        )

        ativo_carteira_salvo = self.repository.salvar(ativo_carteira)

        return ativo_carteira_salvo

    def listar_ativos_carteira(self, id_carteira: int) -> list[AtivoCarteira]:
        return self.repository.listar_por_carteira(id_carteira)
