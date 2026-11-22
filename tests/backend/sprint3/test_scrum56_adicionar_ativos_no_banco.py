"""SCRUM-56 - Adicionar ativos no banco de dados (importacao do acoes-b3.csv)."""

import sys
from pathlib import Path

import pydantic
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.modules.assets.models import Ativo
from app.modules.investors.models import Investidor

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "database" / "migrations"))
from ativos import ARQUIVO_ATIVOS, carregar_ativos, importar_ativos  # noqa: E402

CABECALHO = "ticker;nome;setor;subsetor;segmento\n"


@pytest.fixture
def engine():
    engine = create_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def csv_teste(tmp_path, *linhas):
    arquivo = tmp_path / "ativos.csv"
    arquivo.write_text(CABECALHO + "".join(l + "\n" for l in linhas), encoding="utf-8")
    return arquivo


def tickers_no_banco(engine):
    with engine.connect() as conexao:
        return sorted(linha[0] for linha in conexao.execute(Ativo.__table__.select()))


# ---------- arquivo acoes-b3.csv ----------

def test_csv_da_b3_e_valido_e_sem_tickers_repetidos():
    ativos = carregar_ativos()
    tickers = [a.ticker for a in ativos]
    linhas = ARQUIVO_ATIVOS.read_text(encoding="utf-8-sig").strip().splitlines()
    assert len(ativos) == len(linhas) - 1  # todas as linhas, menos o cabecalho
    assert len(tickers) == len(set(tickers))
    assert all(a.setor for a in ativos)


def test_csv_da_b3_tem_os_ativos_usados_nas_historias():
    tickers = {a.ticker for a in carregar_ativos()}
    # O CRFB3 das historias nao entra: saiu da bolsa em 2025 e nao tem mais cotacao.
    for ticker in ["ABEV3", "BBDC3", "BBDC4", "EGIE3", "ITUB3", "ITUB4", "AALR3", "PETR4"]:
        assert ticker in tickers


def test_csv_da_b3_nao_tem_ativos_do_mercado_fracionario():
    # So ha negociacao em lotes de 100; o ticker com "F" no final e o do fracionario.
    fracionarios = [a.ticker for a in carregar_ativos() if a.ticker.endswith("F")]
    assert fracionarios == []


# ---------- importacao no banco ----------

def test_importa_todos_os_ativos_do_csv(engine):
    total = importar_ativos(engine)
    assert total == len(carregar_ativos())
    assert len(tickers_no_banco(engine)) == total


def test_importar_de_novo_nao_duplica(engine):
    importar_ativos(engine)
    assert importar_ativos(engine) == 0
    assert len(tickers_no_banco(engine)) == len(carregar_ativos())


def test_ativo_ja_cadastrado_e_preservado(engine, tmp_path):
    with engine.begin() as conexao:
        conexao.execute(Ativo.__table__.insert().values(
            ticker="ITUB4", nome="NOME ANTIGO", setor="Financeiro", subsetor="", segmento="", ativo=True,
        ))
    arquivo = csv_teste(tmp_path, "ITUB4;ITAU UNIBANCO;Financeiro;Bancos;Bancos",
                        "ABEV3;AMBEV S.A.;Consumo não Cíclico;Bebidas;Cervejas")
    assert importar_ativos(engine, arquivo) == 1
    with engine.connect() as conexao:
        nome = conexao.execute(Ativo.__table__.select().where(Ativo.ticker == "ITUB4")).first().nome
    assert nome == "NOME ANTIGO"
    assert tickers_no_banco(engine) == ["ABEV3", "ITUB4"]


def test_ticker_e_salvo_em_maiusculas(engine, tmp_path):
    arquivo = csv_teste(tmp_path, " itub4 ;ITAU UNIBANCO;Financeiro;Bancos;Bancos")
    importar_ativos(engine, arquivo)
    assert tickers_no_banco(engine) == ["ITUB4"]


def test_csv_com_ticker_repetido_nao_grava_nada(engine, tmp_path):
    arquivo = csv_teste(tmp_path, "ITUB4;ITAU;Financeiro;Bancos;Bancos", "ITUB4;ITAU;Financeiro;Bancos;Bancos")
    with pytest.raises(ValueError, match="duplicados"):
        importar_ativos(engine, arquivo)
    assert tickers_no_banco(engine) == []


@pytest.mark.parametrize("linha_invalida", [
    "ITUB-4;ITAU;Financeiro;Bancos;Bancos",  # caractere especial
    "ITUB4;ITAU;;Bancos;Bancos",              # sem setor
])
def test_csv_com_linha_invalida_nao_grava_nada(engine, tmp_path, linha_invalida):
    arquivo = csv_teste(tmp_path, "ABEV3;AMBEV S.A.;Consumo não Cíclico;Bebidas;Cervejas", linha_invalida)
    with pytest.raises(pydantic.ValidationError):
        importar_ativos(engine, arquivo)
    assert tickers_no_banco(engine) == []


# ---------- ativos importados aparecem na API ----------

async def test_ativo_importado_pode_ser_consultado_e_incluido_na_carteira(
    cliente, banco, investidor_logado, criar_carteira,
):
    importar_ativos(banco.get_bind())
    resposta = await cliente.get("/assets/PETR4", headers=investidor_logado)
    assert resposta.status_code == 200
    assert resposta.json()["nome"] != ""

    carteira = criar_carteira(banco.query(Investidor).first().id_investidor, "Aposentadoria")
    resposta = await cliente.post("/assets/carteira", headers=investidor_logado, json={
        "ticker": "PETR4", "id_carteira": carteira.id_carteira, "quantidade": 0, "objetivo_percentual": "100",
    })
    assert resposta.status_code == 201
