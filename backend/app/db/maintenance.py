"""Operacoes explicitas de manutencao da estrutura do banco."""
from sqlalchemy import MetaData
from sqlalchemy.engine import Connection, Engine

from app.db import Base, registrar_modelos


class GerenciadorBanco:
    """Cria ou recria as tabelas usando os modelos atuais da aplicacao."""

    def __init__(self, engine: Engine):
        """Recebe a conexao de destino, permitindo usar bancos isolados nos testes."""
        self.engine = engine

    @staticmethod
    def _exigir_confirmacao(confirmar: bool) -> None:
        """Impede apagar tabelas sem uma solicitacao explicita."""
        if confirmar is not True:
            raise ValueError(
                "Esta operação apaga todos os dados das tabelas do banco configurado. "
                "Informe --confirmar para executar."
            )

    def criar_tabelas(self) -> list[str]:
        """Cria apenas tabelas ausentes, sem atualizar nem apagar as existentes."""
        registrar_modelos()
        with self.engine.begin() as conexao:
            Base.metadata.create_all(bind=conexao)
        return sorted(Base.metadata.tables)

    @staticmethod
    def _apagar_tabelas(conexao: Connection) -> None:
        """Le a estrutura real e remove tabelas antigas na ordem das dependencias."""
        estrutura_atual = MetaData()
        estrutura_atual.reflect(bind=conexao)
        estrutura_atual.drop_all(bind=conexao)

    def apagar_tabelas(self, *, confirmar: bool = False) -> None:
        """Apaga as tabelas do banco configurado, incluindo estruturas legadas."""
        self._exigir_confirmacao(confirmar)
        with self.engine.begin() as conexao:
            self._apagar_tabelas(conexao)

    def resetar(self, *, confirmar: bool = False) -> list[str]:
        """Apaga as tabelas e as recria conforme os modelos registrados."""
        self._exigir_confirmacao(confirmar)
        registrar_modelos()
        with self.engine.begin() as conexao:
            self._apagar_tabelas(conexao)
            Base.metadata.create_all(bind=conexao)
        return sorted(Base.metadata.tables)
