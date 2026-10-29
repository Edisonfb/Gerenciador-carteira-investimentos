"""Planejamento da migracao usa SQLite isolado; nenhum banco real e alterado."""
import importlib.util
from pathlib import Path
import sys

import pytest
from sqlalchemy import create_engine, text

arquivo = Path(__file__).resolve().parents[4] / "database/migrations/atualizar_estrutura_atual.py"
spec = importlib.util.spec_from_file_location("migracao_estrutura_atual", arquivo)
modulo = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = modulo
spec.loader.exec_module(modulo)


@pytest.fixture
def banco():
    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE usuario (id_usuario INTEGER PRIMARY KEY, nome_usuario VARCHAR(50) NULL)"))
        conn.execute(text("CREATE TABLE investidor (id_investidor INTEGER PRIMARY KEY, email_recuperacao VARCHAR(255) NULL, primeiro_acesso_concluido BOOLEAN NOT NULL)"))
        conn.execute(text("CREATE TABLE ativo_carteira (ticker VARCHAR(10), id_carteira INTEGER, quantidade INTEGER NOT NULL, CONSTRAINT ck_ativo_carteira_quantidade_positiva CHECK (quantidade > 0))"))
        conn.execute(text("CREATE UNIQUE INDEX uq_usuario_nome_usuario ON usuario(nome_usuario)"))
        conn.execute(text("CREATE UNIQUE INDEX uq_investidor_email_recuperacao ON investidor(email_recuperacao)"))
        yield conn
    engine.dispose()


def test_planeja_objetivo_obrigatorio_em_tabela_vazia_e_troca_check(banco):
    plano = modulo.planejar(banco)
    assert any("ADD COLUMN `objetivo_percentual` DECIMAL(5,2) NOT NULL" in c for c in plano.comandos)
    assert any("DROP CHECK ck_ativo_carteira_quantidade_positiva" in c and "quantidade >= 0" in c for c in plano.comandos)
    assert not plano.pendencias
    # Planejar nao modifica a estrutura.
    assert "objetivo_percentual" not in [r[1] for r in banco.execute(text("PRAGMA table_info(ativo_carteira)"))]


def test_vinculos_antigos_ficam_pendentes_sem_percentuais_inventados(banco):
    banco.execute(text("INSERT INTO ativo_carteira VALUES ('ITUB4', 1, 10)"))
    plano = modulo.planejar(banco)
    assert any(c.endswith("DECIMAL(5,2) NULL") for c in plano.comandos)
    assert plano.pendencias
    assert not any("UPDATE" in c for c in plano.comandos)
    assert banco.execute(text("SELECT quantidade FROM ativo_carteira")).scalar_one() == 10


def test_campos_de_conta_ausentes_sao_planejados(banco):
    banco.execute(text("DROP TABLE usuario"))
    banco.execute(text("CREATE TABLE usuario (id_usuario INTEGER PRIMARY KEY)"))
    banco.execute(text("DROP TABLE investidor"))
    banco.execute(text("CREATE TABLE investidor (id_investidor INTEGER PRIMARY KEY)"))
    comandos = "\n".join(modulo.planejar(banco).comandos)
    assert "ADD COLUMN `nome_usuario` VARCHAR(50) NULL" in comandos
    assert "ADD COLUMN `email_recuperacao` VARCHAR(255) NULL" in comandos
    assert "ADD COLUMN `primeiro_acesso_concluido` BOOLEAN NOT NULL DEFAULT FALSE" in comandos
    assert comandos.count("ADD UNIQUE INDEX") == 2


def test_nao_adivinha_estado_de_contas_antigas(banco):
    banco.execute(text("DROP TABLE investidor"))
    banco.execute(text("CREATE TABLE investidor (id_investidor INTEGER PRIMARY KEY, email_recuperacao VARCHAR(255) UNIQUE)"))
    banco.execute(text("INSERT INTO investidor(id_investidor) VALUES (1)"))
    with pytest.raises(ValueError, match="primeiro-acesso-legado"):
        modulo.planejar(banco)
    plano = modulo.planejar(banco, "concluido")
    assert any("DEFAULT TRUE" in c for c in plano.comandos)


def test_conclui_not_null_depois_do_preenchimento_real(banco):
    banco.execute(text("ALTER TABLE ativo_carteira ADD COLUMN objetivo_percentual DECIMAL(10,2) NULL"))
    banco.execute(text("INSERT INTO ativo_carteira VALUES ('ITUB4', 1, 10, NULL)"))
    assert modulo.planejar(banco).pendencias
    banco.execute(text("UPDATE ativo_carteira SET objetivo_percentual=100"))
    plano = modulo.planejar(banco)
    assert not plano.pendencias
    assert any("MODIFY COLUMN `objetivo_percentual` DECIMAL(5,2) NOT NULL" in c for c in plano.comandos)


@pytest.mark.parametrize("valor", [0, -1, 100.01, 10.123])
def test_rejeita_percentual_invalido_sem_ddl(banco, valor):
    banco.execute(text("ALTER TABLE ativo_carteira ADD COLUMN objetivo_percentual NUMERIC"))
    banco.execute(text("INSERT INTO ativo_carteira VALUES ('ITUB4', 1, 10, :valor)"), {"valor": valor})
    with pytest.raises(ValueError, match="objetivos fora"):
        modulo.planejar(banco)


def test_nao_cria_indice_unique_com_valores_duplicados(banco):
    banco.execute(text("DROP TABLE usuario"))
    banco.execute(text("CREATE TABLE usuario (nome_usuario VARCHAR(50))"))
    banco.execute(text("INSERT INTO usuario VALUES ('ana'),('ana')"))
    with pytest.raises(ValueError, match="duplicados"):
        modulo.planejar(banco)


def test_estrutura_atual_nao_exige_alteracoes(banco):
    banco.execute(text("DROP TABLE ativo_carteira"))
    banco.execute(text("CREATE TABLE ativo_carteira (ticker VARCHAR(10), id_carteira INTEGER, quantidade INTEGER NOT NULL, objetivo_percentual DECIMAL(5,2) NOT NULL, CONSTRAINT ck_ativo_carteira_quantidade_nao_negativa CHECK (quantidade >= 0))"))
    plano = modulo.planejar(banco)
    assert plano.comandos == []
    assert plano.pendencias == []
