"""Atualiza bancos MySQL existentes. Por padrao, apenas mostra o plano.

Uso na raiz:
  backend/.venv/Scripts/python.exe database/migrations/atualizar_estrutura_atual.py
  backend/.venv/Scripts/python.exe database/migrations/atualizar_estrutura_atual.py --aplicar

DDL no MySQL faz commit implicito: faca backup. Percentuais nunca sao inventados.
"""
import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from sqlalchemy import inspect, text


@dataclass
class Plano:
    comandos: list[str] = field(default_factory=list)
    pendencias: list[str] = field(default_factory=list)


def planejar(conexao, primeiro_acesso_legado: str | None = None) -> Plano:
    """Inspeciona antes de gerar DDL; nao executa nenhuma alteracao."""
    inspector = inspect(conexao)
    tabelas = set(inspector.get_table_names())
    if not {"usuario", "investidor", "ativo_carteira"}.issubset(tabelas):
        raise ValueError("Faltam tabelas base. Execute create_tables.py antes desta migracao.")
    colunas = {t: {c["name"]: c for c in inspector.get_columns(t)} for t in ("usuario", "investidor", "ativo_carteira")}
    if "ticker" not in colunas["ativo_carteira"]:
        raise ValueError("Modelo legado de ativos: revise integrar_ativos.py antes desta migracao.")
    plano = Plano()

    def unico(tabela, campo, nome_indice):
        # Indices compostos nao garantem unicidade individual do campo.
        indices = inspector.get_indexes(tabela) + inspector.get_unique_constraints(tabela)
        if any(i.get("column_names") == [campo] and (i.get("unique") or "unique" not in i) for i in indices):
            return
        if campo in colunas[tabela]:
            repetidos = conexao.execute(text(f"SELECT `{campo}` FROM `{tabela}` WHERE `{campo}` IS NOT NULL GROUP BY `{campo}` HAVING COUNT(*) > 1 LIMIT 1")).first()
            if repetidos:
                raise ValueError(f"Ha valores duplicados em {tabela}.{campo}. Corrija-os antes de aplicar.")
        plano.comandos.append(f"ALTER TABLE `{tabela}` ADD UNIQUE INDEX `{nome_indice}` (`{campo}`)")

    for tabela, campo, tamanho in [("usuario", "nome_usuario", 50), ("investidor", "email_recuperacao", 255)]:
        atual = colunas[tabela].get(campo)
        if atual is None:
            plano.comandos.append(f"ALTER TABLE `{tabela}` ADD COLUMN `{campo}` VARCHAR({tamanho}) NULL")
        elif getattr(atual["type"], "length", None) != tamanho or not atual["nullable"]:
            valores = conexao.execute(text(f"SELECT `{campo}` FROM `{tabela}` WHERE `{campo}` IS NOT NULL")).scalars()
            if any(len(valor) > tamanho for valor in valores):
                raise ValueError(f"Ha valores longos em {tabela}.{campo}. Nenhum dado sera truncado automaticamente.")
            plano.comandos.append(f"ALTER TABLE `{tabela}` MODIFY COLUMN `{campo}` VARCHAR({tamanho}) NULL")
        unico(tabela, campo, f"uq_{tabela}_{campo}")

    pessoais = {"nome": 30, "sobrenome": 30, "cpf": 11, "telefone": 15, "cep": 8, "uf": 2, "cidade": 32, "bairro": 30, "logradouro": 50, "numero": 5}
    for campo, tamanho in pessoais.items():
        atual = colunas["investidor"].get(campo)
        if atual and not atual["nullable"]:
            # Preserva o tamanho real das colunas ja existentes.
            tamanho_real = getattr(atual["type"], "length", None)
            if tamanho_real is None:
                raise ValueError(f"Tipo legado inesperado em investidor.{campo}; revise manualmente.")
            plano.comandos.append(f"ALTER TABLE `investidor` MODIFY COLUMN `{campo}` VARCHAR({tamanho_real}) NULL")
    token = colunas["investidor"].get("token_acesso")
    if token and not token["nullable"]:
        tamanho = getattr(token["type"], "length", None)
        if tamanho is None:
            raise ValueError("Tipo inesperado no token legado. Revise manualmente.")
        plano.comandos.append(f"ALTER TABLE `investidor` MODIFY COLUMN `token_acesso` VARCHAR({tamanho}) NULL")

    flag = colunas["investidor"].get("primeiro_acesso_concluido")
    if flag is None:
        total = conexao.execute(text("SELECT COUNT(*) FROM investidor")).scalar_one()
        if total and primeiro_acesso_legado not in {"pendente", "concluido"}:
            raise ValueError("Existem investidores sem controle de primeiro acesso. Informe --primeiro-acesso-legado pendente ou concluido conforme a situacao dessas contas. A migracao nao adivinha esse estado.")
        if primeiro_acesso_legado == "concluido" and total:
            plano.comandos.extend([
                "ALTER TABLE `investidor` ADD COLUMN `primeiro_acesso_concluido` BOOLEAN NOT NULL DEFAULT TRUE",
                "ALTER TABLE `investidor` ALTER COLUMN `primeiro_acesso_concluido` DROP DEFAULT",
            ])
        else:
            plano.comandos.extend([
                "ALTER TABLE `investidor` ADD COLUMN `primeiro_acesso_concluido` BOOLEAN NOT NULL DEFAULT FALSE",
                "ALTER TABLE `investidor` ALTER COLUMN `primeiro_acesso_concluido` DROP DEFAULT",
            ])
    elif flag["nullable"]:
        nulos = conexao.execute(text("SELECT COUNT(*) FROM investidor WHERE primeiro_acesso_concluido IS NULL")).scalar_one()
        if nulos:
            raise ValueError("Existem estados de primeiro acesso nulos. Defina os estados reais antes de continuar.")
        plano.comandos.append("ALTER TABLE `investidor` MODIFY COLUMN `primeiro_acesso_concluido` BOOLEAN NOT NULL")

    invalidos = conexao.execute(text("SELECT COUNT(*) FROM ativo_carteira WHERE quantidade IS NULL OR quantidade < 0 OR quantidade > 2147483647 OR quantidade != ROUND(quantidade, 0)")).scalar_one()
    if invalidos:
        raise ValueError("Existem quantidades nulas, negativas, fracionadas ou fora do limite INT. Corrija-as antes de aplicar.")
    quantidade = colunas["ativo_carteira"]["quantidade"]
    if quantidade["nullable"] or str(quantidade["type"]).upper() != "INTEGER":
        plano.comandos.append("ALTER TABLE `ativo_carteira` MODIFY COLUMN `quantidade` INT NOT NULL")

    checks = inspector.get_check_constraints("ativo_carteira")
    remover = []
    correta = False
    for check in checks:
        if "quantidade" not in check["sqltext"].lower():
            continue
        normalizado = re.sub(r"[`()\s]", "", check["sqltext"].lower())
        if normalizado not in {"quantidade>0", "quantidade>=0"}:
            raise ValueError("Restricao de quantidade nao reconhecida. Revise-a antes de migrar.")
        if normalizado == "quantidade>=0" and check["name"] == "ck_ativo_carteira_quantidade_nao_negativa":
            correta = True
        else:
            remover.append(check["name"])
    partes = ["DROP CHECK " + conexao.dialect.identifier_preparer.quote(nome) for nome in remover]
    if not correta:
        partes.append("ADD CONSTRAINT ck_ativo_carteira_quantidade_nao_negativa CHECK (quantidade >= 0)")
    if partes:
        plano.comandos.append("ALTER TABLE `ativo_carteira` " + ", ".join(partes))

    objetivo = colunas["ativo_carteira"].get("objetivo_percentual")
    if objetivo is None:
        total = conexao.execute(text("SELECT COUNT(*) FROM ativo_carteira")).scalar_one()
        if total:
            plano.comandos.append("ALTER TABLE `ativo_carteira` ADD COLUMN `objetivo_percentual` DECIMAL(5,2) NULL")
            plano.pendencias.append(f"{total} vinculo(s) antigo(s) precisam de objetivos reais. Preencha objetivo_percentual para cada ticker/id_carteira e execute novamente --aplicar para definir NOT NULL. A aplicacao requer essa conclusao para consultar as carteiras.")
        else:
            plano.comandos.append("ALTER TABLE `ativo_carteira` ADD COLUMN `objetivo_percentual` DECIMAL(5,2) NOT NULL")
    else:
        invalidos = conexao.execute(text("SELECT COUNT(*) FROM ativo_carteira WHERE objetivo_percentual IS NOT NULL AND (objetivo_percentual <= 0 OR objetivo_percentual > 100 OR objetivo_percentual != ROUND(objetivo_percentual, 2))")).scalar_one()
        if invalidos:
            raise ValueError("Existem objetivos fora de (0,100] ou com mais de duas casas. Nenhum percentual sera corrigido automaticamente.")
        nulos = conexao.execute(text("SELECT COUNT(*) FROM ativo_carteira WHERE objetivo_percentual IS NULL")).scalar_one()
        if nulos:
            plano.pendencias.append(f"{nulos} objetivo(s) ainda nulo(s). Preencha os percentuais reais e execute novamente --aplicar.")
        tipo = objetivo["type"]
        if getattr(tipo, "precision", None) != 5 or getattr(tipo, "scale", None) != 2 or (objetivo["nullable"] and not nulos):
            plano.comandos.append("ALTER TABLE `ativo_carteira` MODIFY COLUMN `objetivo_percentual` DECIMAL(5,2) " + ("NULL" if nulos else "NOT NULL"))
    return plano


def atualizar(engine, aplicar=False, primeiro_acesso_legado=None):
    if engine.dialect.name != "mysql":
        raise ValueError("A execucao desta migracao e exclusiva para MySQL 8.0.16 ou superior.")
    with engine.connect() as conexao:
        versao = conexao.dialect.server_version_info
        if versao and versao < (8, 0, 16):
            raise ValueError("MySQL 8.0.16 ou superior e necessario para CHECK efetivo.")
        plano = planejar(conexao, primeiro_acesso_legado)
        print("APLICANDO MIGRACAO" if aplicar else "SOMENTE VERIFICACAO: nenhuma alteracao sera aplicada")
        for comando in plano.comandos:
            print(comando + ";")
            if aplicar:
                conexao.execute(text(comando))
                conexao.commit()
        for pendencia in plano.pendencias:
            print("PENDENCIA:", pendencia)
        if not plano.comandos and not plano.pendencias:
            print("Estrutura ja atualizada. Nenhuma alteracao necessaria.")
        elif aplicar and not plano.pendencias:
            print("Migracao concluida. Dados existentes preservados.")
        return plano


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aplicar", action="store_true", help="Executa o plano; sem esta opcao apenas verifica.")
    parser.add_argument("--primeiro-acesso-legado", choices=["pendente", "concluido"], help="Estado dos investidores antigos quando a coluna ainda nao existe.")
    args = parser.parse_args()
    from app.db.session import engine
    engine.echo = False
    try:
        resultado = atualizar(engine, args.aplicar, args.primeiro_acesso_legado)
        sys.exit(2 if resultado.pendencias else 0)
    except ValueError as erro:
        print("MIGRACAO NAO INICIADA:", erro, file=sys.stderr)
        sys.exit(1)
