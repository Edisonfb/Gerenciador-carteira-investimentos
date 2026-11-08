"""Migra os dois modelos de ativos sem apagar o catalogo nem os vinculos."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from sqlalchemy import inspect, text
from app.db import registrar_modelos
from app.modules.assets.models import Ativo, AtivoCarteira


def migrar_ativos(engine):
    """Atualiza colunas, preserva IDs legados e recusa dados inconsistentes."""
    registrar_modelos()
    if engine.dialect.name not in {"sqlite", "mysql"}:
        raise ValueError("Migracao disponivel para MySQL e SQLite.")
    with engine.begin() as conn:
        inspector = inspect(conn)
        tabelas = inspector.get_table_names()
        for tabela in tabelas:
            for fk in inspector.get_foreign_keys(tabela):
                if fk["referred_table"] == "ativo_carteira":
                    raise ValueError("Referencia externa a ativo_carteira requer migracao especifica.")
        if "ativo" not in tabelas:
            Ativo.__table__.create(conn)
        else:
            colunas = {c["name"]: c for c in inspector.get_columns("ativo")}
            chave = "ticker" if "ticker" in colunas else "codigo"
            if chave not in colunas:
                raise ValueError("Tabela ativo sem ticker ou codigo reconhecido.")
            # Valida antes de executar DDL (no MySQL, DDL pode confirmar transacoes).
            tickers = conn.execute(text(f"SELECT {chave} FROM ativo")).scalars().all()
            if any(not isinstance(t, str) or not re.fullmatch(r"[A-Z0-9]{1,10}", t) for t in tickers):
                raise ValueError("Existem tickers invalidos; revise-os antes da migracao.")
            if len(set(tickers)) != len(tickers):
                raise ValueError("Existem tickers duplicados; revise-os antes da migracao.")
            if "ativo_carteira" in tabelas:
                invalidos = conn.execute(text(
                    "SELECT COUNT(*) FROM ativo_carteira WHERE quantidade IS NULL OR quantidade <= 0"
                )).scalar_one()
                if invalidos:
                    raise ValueError("Existem quantidades invalidas; revise-as antes da migracao.")
            if chave == "codigo" and engine.dialect.name == "mysql":
                conn.execute(text("ALTER TABLE ativo CHANGE COLUMN codigo ticker VARCHAR(10) NOT NULL"))
            elif chave == "codigo":
                conn.execute(text("ALTER TABLE ativo RENAME COLUMN codigo TO ticker"))
            # O ID numerico legado e sua chave primaria permanecem intactos.
            if engine.dialect.name == "mysql":
                fks = []
                for tabela in tabelas:
                    for fk in inspector.get_foreign_keys(tabela):
                        if fk["referred_table"] == "ativo" and fk["referred_columns"] == ["ticker"]:
                            if tabela != "ativo_carteira" or fk["constrained_columns"] != ["ticker"]:
                                raise ValueError("Referencia externa a ticker requer migracao especifica.")
                            fks.append((tabela, fk))
                preparer = conn.dialect.identifier_preparer
                for tabela, fk in fks:
                    conn.execute(text(
                        f"ALTER TABLE {preparer.quote(tabela)} DROP FOREIGN KEY {preparer.quote(fk['name'])}"
                    ))
                if "ativo_carteira" in tabelas:
                    conn.execute(text("ALTER TABLE ativo_carteira MODIFY ticker VARCHAR(10) NOT NULL"))
                conn.execute(text("ALTER TABLE ativo MODIFY ticker VARCHAR(10) NOT NULL"))
                conn.execute(text("ALTER TABLE ativo MODIFY setor VARCHAR(255) NOT NULL"))
                for tabela, fk in fks:
                    nome = preparer.quote(fk["name"])
                    opcoes = fk.get("options", {})
                    sufixo = ""
                    for opcao, clausula in [("ondelete", " ON DELETE "), ("onupdate", " ON UPDATE ")]:
                        acao = opcoes.get(opcao)
                        if acao in {"CASCADE", "SET NULL", "RESTRICT", "NO ACTION"}:
                            sufixo += clausula + acao
                    conn.execute(text(
                        f"ALTER TABLE ativo_carteira ADD CONSTRAINT {nome} "
                        f"FOREIGN KEY (ticker) REFERENCES ativo(ticker){sufixo}"
                    ))
            adicoes = {
                "nome": "VARCHAR(50) NOT NULL DEFAULT ''",
                "subsetor": "VARCHAR(255) NOT NULL DEFAULT ''",
                "segmento": "VARCHAR(255) NOT NULL DEFAULT ''",
                "ativo": "BOOLEAN NOT NULL DEFAULT 1",
                "data_criacao": "DATETIME",
            }
            for nome, ddl in adicoes.items():
                if nome not in colunas:
                    conn.execute(text(f"ALTER TABLE ativo ADD COLUMN {nome} {ddl}"))
            conn.execute(text(
                "UPDATE ativo SET data_criacao = CURRENT_TIMESTAMP WHERE data_criacao IS NULL"
            ))
            # A FK do novo vinculo exige unicidade, mesmo no banco de IDs legados.
            inspector = inspect(conn)
            pk = inspector.get_pk_constraint("ativo").get("constrained_columns", [])
            unicos = [u["column_names"] for u in inspector.get_unique_constraints("ativo")]
            unicos += [i["column_names"] for i in inspector.get_indexes("ativo") if i["unique"]]
            if pk != ["ticker"] and ["ticker"] not in unicos:
                conn.execute(text("CREATE UNIQUE INDEX uq_ativo_ticker ON ativo (ticker)"))
        if "ativo_carteira" not in tabelas:
            AtivoCarteira.__table__.create(conn)
        else:
            checks = inspect(conn).get_check_constraints("ativo_carteira")
            nome_check = "ck_ativo_carteira_quantidade_positiva"
            if not any(c["name"] == nome_check for c in checks):
                if engine.dialect.name == "sqlite":
                    # SQLite nao permite adicionar CHECK via ALTER TABLE.
                    conn.execute(text(
                        "CREATE TABLE ativo_carteira_integracao ("
                        "ticker VARCHAR(10) NOT NULL REFERENCES ativo(ticker), "
                        "id_carteira INTEGER NOT NULL REFERENCES carteira(id_carteira), "
                        "quantidade INTEGER NOT NULL, PRIMARY KEY (ticker, id_carteira), "
                        "CONSTRAINT ck_ativo_carteira_quantidade_positiva CHECK (quantidade > 0))"
                    ))
                    conn.execute(text(
                        "INSERT INTO ativo_carteira_integracao SELECT ticker, id_carteira, quantidade "
                        "FROM ativo_carteira"
                    ))
                    conn.execute(text("DROP TABLE ativo_carteira"))
                    conn.execute(text("ALTER TABLE ativo_carteira_integracao RENAME TO ativo_carteira"))
                else:
                    conn.execute(text(
                        "ALTER TABLE ativo_carteira ADD CONSTRAINT "
                        "ck_ativo_carteira_quantidade_positiva CHECK (quantidade > 0)"
                    ))


if __name__ == "__main__":
    from app.db.session import engine
    migrar_ativos(engine)
    print("Estrutura de ativos integrada. Nenhum registro foi removido.")
