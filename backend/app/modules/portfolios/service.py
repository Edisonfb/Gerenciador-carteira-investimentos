"""Regras de negocio do modulo de carteiras."""
from app.modules.portfolios.models import Carteira
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.portfolios.schemas import( CarteiraAtualizacaoEntrada, CarteiraCadastroEntrada)

class CarteiraService:
    """Concentra as regras de negocio das carteiras."""
    def __init__(self, repository: CarteiraRepository):
        self.repository = repository

    def criar_carteira(self, dados: CarteiraCadastroEntrada, id_investidor: int
                       ) -> tuple[Carteira | None, str | None]:
        nome = dados.nome.strip()

        if not nome:
            return None, "O nome da carteira é obrigatório."

        carteira = Carteira(id_investidor = id_investidor, nome = nome, descricao = dados.descricao)

        carteira_salva = self.repository.adicionar(carteira)

        return carteira_salva, None

    def listar_carteiras(self, id_investidor: int) -> list[Carteira]:
        return self.repository.listar_por_investidor(id_investidor)

    def buscar_carteira(self, id_carteira: int, id_investidor: int) -> Carteira | None:
        return self.repository.buscar_por_id_e_investidor(id_carteira, id_investidor)

    def atualizar_carteira(self, id_carteira: int, id_investidor: int, dados: CarteiraAtualizacaoEntrada
                            ) -> tuple[Carteira |None, str | None]:
        carteira = self.repository.buscar_por_id_e_investidor(id_carteira, id_investidor)

        if carteira is None:
            return None, "Carteira não encontrada"

        atualizacoes = dados.model_dump(exclude_unset= True)

        if "nome" in atualizacoes:
            if atualizacoes["nome"] is None:
                 return None, "O nome da carteira é obrigatório."

            nome = atualizacoes["nome"].strip()

            if not nome:
                return None, "O nome da carteira é obrigatório."

            carteira.nome = nome

        if "descricao" in atualizacoes:
            carteira.descricao = atualizacoes["descricao"]

        if "ativa" in atualizacoes:
            if atualizacoes["ativa"] is None:
                return None, "O status da carteira é obrigatório."
            carteira.ativa = atualizacoes["ativa"]

        carteira_atualizada = self.repository.atualizar(carteira)

        return carteira_atualizada, None

    def excluir_carteira(self, id_carteira: int, id_investidor: int) -> bool:
        carteira = self.repository.buscar_por_id_e_investidor( id_carteira, id_investidor)

        if carteira is None:
            return False

        self.repository.excluir(carteira)

        return True