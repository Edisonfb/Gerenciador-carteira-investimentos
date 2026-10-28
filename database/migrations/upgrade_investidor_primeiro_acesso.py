"""Atualiza o schema de investidores sem excluir dados ou o token legado.

Executar na raiz: backend/.venv/Scripts/python.exe database/migrations/upgrade_investidor_primeiro_acesso.py
Pode ser executado novamente. ALTER TABLE no MySQL faz commit implícito.
"""
import sys
from pathlib import Path
from sqlalchemy import inspect, text

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
import app.db  # Registra os modelos antes da importação da sessão.
from app.db.session import engine


def atualizar():
    engine.echo = False
    campos = {
        "nome": 30, "sobrenome": 30, "cpf": 11, "telefone": 15,
        "cep": 8, "uf": 2, "cidade": 32, "bairro": 30,
        "logradouro": 50, "numero": 5,
    }
    with engine.connect() as conexao:
        colunas = {c["name"]: c for c in inspect(conexao).get_columns("investidor")}
        comandos = []
        for nome, tamanho in campos.items():
            if nome in colunas and not colunas[nome]["nullable"]:
                comandos.append(f"MODIFY COLUMN `{nome}` VARCHAR({tamanho}) NULL")
        if "email_recuperacao" not in colunas:
            comandos.append("ADD COLUMN email_recuperacao VARCHAR(255) NULL UNIQUE")
        if "primeiro_acesso_concluido" not in colunas:
            comandos.append("ADD COLUMN primeiro_acesso_concluido BOOLEAN NOT NULL DEFAULT FALSE")
        # Mantém tokens existentes; novas inclusões não precisam preencher o campo legado.
        if "token_acesso" in colunas and not colunas["token_acesso"]["nullable"]:
            tamanho = colunas["token_acesso"]["type"].length
            comandos.append(f"MODIFY COLUMN token_acesso VARCHAR({tamanho}) NULL")
        if comandos:
            conexao.execute(text("ALTER TABLE investidor " + ", ".join(comandos)))
            conexao.commit()
            print("Schema atualizado; cadastros e tokens legados preservados.")
        else:
            print("Schema já atualizado; nenhuma alteração necessária.")


if __name__ == "__main__":
    atualizar()
