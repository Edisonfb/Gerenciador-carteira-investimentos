"""Regras de negocio e autorizacao dos ativos de carteiras."""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.assets.repository import AtivoCarteiraRepository, AtivoRepository
from app.modules.assets.schemas import (
    AtivoAtualizacaoEntrada, AtivoCarteiraUpdate,
    CadastroAtivoCarteiraEntrada, CadastroAtivoEntrada,
)
from app.modules.portfolios.repository import CarteiraRepository


class ErroAtivo(ValueError):
    """Representa uma falha prevista sem depender da camada HTTP."""

    def __init__(self, mensagem: str, status_code: int):
        """Carrega a mensagem e o codigo de resposta da falha."""
        super().__init__(mensagem)
        self.status_code = status_code


class AtivoService:
    """Consulta o catalogo e preserva a manutencao interna."""

    def __init__(self, repository: AtivoRepository):
        """Recebe o repositorio do catalogo."""
        self.repository = repository

    def listar_ativos(self, codigo: str | None = None) -> list[Ativo]:
        """Lista ou pesquisa um ticker exato normalizado."""
        if codigo is None:
            return self.repository.listar_ativos()
        ativo = self.repository.buscar_por_codigo(codigo.strip().upper())
        return [] if ativo is None else [ativo]

    def buscar_ativos(self, ticker: str) -> Ativo | None:
        """Consulta pelo identificador publico ticker."""
        return self.repository.buscar_por_codigo(ticker.strip().upper())

    def buscar_por_setor(self, setor: str) -> list[Ativo]:
        """Remove espacos e consulta o setor por igualdade."""
        return self.repository.buscar_por_setor(setor.strip())

    def criar_ativo(self, dados: CadastroAtivoEntrada) -> tuple[Ativo | None, str | None]:
        """Evita tickers duplicados e cadastra os campos validados."""
        if self.repository.buscar_por_codigo(dados.ticker) is not None:
            return None, "Já existe um ativo com esse código."
        try:
            return self.repository.salvar(Ativo(**dados.model_dump())), None
        except IntegrityError:
            return None, "Não foi possível cadastrar o ativo por conflito de dados."

    def atualizar_ativo(
        self, ticker: str, dados: AtivoAtualizacaoEntrada,
    ) -> tuple[Ativo | None, str | None]:
        """Atualiza os campos enviados sem modificar a chave dos vinculos."""
        ativo = self.buscar_ativos(ticker)
        if ativo is None:
            return None, "Ativo não encontrado."
        campos = dados.model_dump(exclude_unset=True)
        if any(valor is None for valor in campos.values()):
            return None, "Os campos enviados não podem ser nulos."
        for campo, valor in campos.items():
            setattr(ativo, campo, valor)
        return self.repository.atualizar(ativo), None

    def excluir_ativo(self, ticker: str) -> bool:
        """Preserva a exclusao interna apenas para ativos sem posicoes em carteiras."""
        ativo = self.buscar_ativos(ticker)
        if ativo is None or ativo.ativos_carteira:
            return False
        try:
            self.repository.excluir(ativo)
        except IntegrityError:
            return False
        return True


class AtivoCarteiraService:
    """Autoriza a carteira antes de consultar ou modificar seus ativos."""

    def __init__(
        self, repository: AtivoCarteiraRepository,
        carteiras: CarteiraRepository, ativos: AtivoRepository,
    ):
        """Recebe repositorios, mantendo consultas fora das regras de negocio."""
        self.repository = repository
        self.carteiras = carteiras
        self.ativos = ativos

    def _exigir_carteira(self, id_carteira: int, id_investidor: int):
        """Oculta carteiras inexistentes ou pertencentes a outro investidor."""
        carteira = self.carteiras.buscar_por_id_e_investidor(id_carteira, id_investidor)
        if carteira is None:
            raise ErroAtivo("Carteira não encontrada.", 404)
        return carteira

    def cadastrar_ativo_carteira(
        self, dados: CadastroAtivoCarteiraEntrada, id_investidor: int,
    ) -> AtivoCarteira:
        """Adiciona ativo existente apenas a uma carteira do investidor."""
        carteira = self._exigir_carteira(dados.id_carteira, id_investidor)
        if not carteira.ativa:
            raise ErroAtivo("A carteira está desativada.", 400)
        ativo = self.ativos.buscar_por_codigo(dados.ticker)
        if ativo is None:
            raise ErroAtivo("Ativo não encontrado.", 404)
        if not ativo.ativo:
            raise ErroAtivo("O ativo está desativado.", 400)
        if self.repository.buscar(dados.ticker, dados.id_carteira) is not None:
            raise ErroAtivo("O ativo já está cadastrado nesta carteira.", 409)
        try:
            return self.repository.salvar(AtivoCarteira(**dados.model_dump()))
        except IntegrityError as erro:
            # O repositorio ja executou rollback, inclusive em corridas de FK/duplicidade.
            raise ErroAtivo("Conflito ao cadastrar o ativo na carteira.", 409) from erro

    def listar_ativos_carteira(
        self, id_carteira: int, id_investidor: int,
    ) -> list[AtivoCarteira]:
        """Lista os vinculos somente depois de verificar o proprietario."""
        self._exigir_carteira(id_carteira, id_investidor)
        return self.repository.listar_por_carteira(id_carteira)

    def atualizar_quantidade(
        self, id_carteira: int, ticker: str,
        dados: AtivoCarteiraUpdate, id_investidor: int,
    ) -> AtivoCarteira:
        """Substitui a quantidade preservando o vinculo e seu objetivo, inclusive com zero."""
        carteira = self._exigir_carteira(id_carteira, id_investidor)
        vinculo = self.repository.buscar(ticker, id_carteira)
        if vinculo is None:
            raise ErroAtivo("Ativo não encontrado nesta carteira.", 404)
        if dados.quantidade > 0:
            if not carteira.ativa:
                raise ErroAtivo("A carteira está desativada.", 400)
            ativo = self.ativos.buscar_por_codigo(ticker)
            if ativo is None or not ativo.ativo:
                raise ErroAtivo("O ativo está desativado ou não existe.", 400)
        try:
            vinculo.quantidade = dados.quantidade
            return self.repository.salvar(vinculo)
        except (IntegrityError, StaleDataError) as erro:
            raise ErroAtivo("Conflito ao atualizar o ativo da carteira.", 409) from erro

    def remover_ativo_carteira(
        self, id_carteira: int, ticker: str, id_investidor: int,
    ) -> None:
        """Remove o vinculo proprio, mesmo com quantidade positiva ou recurso inativo."""
        self._exigir_carteira(id_carteira, id_investidor)
        vinculo = self.repository.buscar(ticker, id_carteira)
        if vinculo is None:
            raise ErroAtivo("Ativo não encontrado nesta carteira.", 404)
        try:
            self.repository.excluir(vinculo)
        except (IntegrityError, StaleDataError) as erro:
            raise ErroAtivo("Conflito ao remover o ativo da carteira.", 409) from erro
