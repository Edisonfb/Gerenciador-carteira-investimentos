"""Regras de negocio do modulo de ativos financeiros."""
from app.modules.assets.models import Ativo
from app.modules.assets.repository import AtivoRepository
from app.modules.assets.schemas import (
    AtivoAtualizacaoEntrada,
    AtivoCadastroEntrada
)

class AtivoService:
    """Concentra as validações e operações de negócios do ativo"""

    def __init__(self, repository: AtivoRepository):
        self.repository = repository

    def criar_ativo(
            self, dados: AtivoCadastroEntrada,
    ) -> tuple[Ativo | None, str | None]:
        """Valida os dados e cadastra um ativo com código único"""
        codigo = dados.codigo.strip().upper()
        setor = dados.setor.strip()

        if not codigo:
            return None, "O código do ativo é obrigatório"

        if len(codigo) > 10:
            return None, "O código do ativo deve ter no máximo 10 caracteres"

        if not setor:
            return None, "O setor do ativo é obrigatório"

        if len(setor) > 80:
            return None, "O setor do ativo deve ter no máximo 80 caracteres"

        ativo_existente = self.repository.buscar_por_codigo(codigo)

        if ativo_existente is not None:
            return None, "Já existe um ativo com esse código"

        ativo = Ativo(codigo = codigo, setor = setor)

        ativo_salvo = self.repository.adicionar(ativo)

        return ativo_salvo, None

    def listar_ativos(self, codigo: str | None = None) -> list[Ativo]:
        """Retorna todos os ativos cadastrados"""
        if codigo is None:
            return self.repository.listar_todos()

        codigo = codigo.strip().upper()
        ativo = self.repository.buscar_por_codigo(codigo)

        if ativo is None:
            return []

        return [ativo]

    def buscar_ativos(self, id_ativo: int) -> Ativo | None:
        """Busca um ativo pelo identificados"""
        return self.repository.buscar_por_id(id_ativo)

    def atualizar_ativo(self,
        id_ativo: int,
        dados: AtivoAtualizacaoEntrada
        )-> tuple[Ativo | None, str | None]:
        """Valida os campos enviados e atualiza um ativo existente."""
        ativo = self.repository.buscar_por_id(id_ativo)

        if ativo is None:
            return None, "Ativo não encontrado"

        atualizacoes = dados.model_dump(exclude_unset = True)

        if "codigo" in atualizacoes:
            if atualizacoes["codigo"] is None:
                return None, "O código do ativo é obrigatório"

            codigo = atualizacoes["codigo"].strip().upper()

            if not codigo:
                return None, "O código do ativo é obrigatório"

            if len(codigo) > 10:
                return None, "O código do ativo deve ter no máximo 10 caracteres"

            ativo_existente = self.repository.buscar_por_codigo(codigo)

            if(ativo_existente is not None and ativo_existente.id_ativo != ativo.id_ativo):
                return None, "Já existe um ativo com esse código."

            atualizacoes["codigo"] = codigo

        if "setor" in atualizacoes:
            if atualizacoes["setor"] is None:
                return None, "O setor do ativo é obrigatório."

            setor = atualizacoes["setor"].strip()

            if not setor:
                return None, "O setor do ativo é obrigatório."

            if len(setor) > 80:
                return None, "O setor do ativo deve ter no máximo 80 caracteres."

            atualizacoes["setor"] = setor

        if "ativo" in atualizacoes:
            if atualizacoes["ativo"] is None:
                return None, "O status do ativo é obrigatório."

        if not atualizacoes:
            return ativo, None

        for campo, valor in atualizacoes.items():
            setattr(ativo, campo, valor)

        ativo_atualizado = self.repository.atualizar(ativo)

        return ativo_atualizado, None


    def excluir_ativo(self, id_ativo: int) -> bool:
        """Exclui um ativo existente e informa se ele foi encontrado."""
        ativo = self.repository.buscar_por_id(id_ativo)

        if ativo is None:
            return False

        self.repository.excluir(ativo)

        return True