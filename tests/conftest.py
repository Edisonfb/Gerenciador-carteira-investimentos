"""Configuracoes compartilhadas por todos os testes."""

import os

# Precisa vir antes de qualquer import do app: o config le o ambiente ao ser
# importado e o load_dotenv nao sobrescreve variaveis ja definidas.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "chave-de-teste-com-tamanho-suficiente-para-hs256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

import app.db  # noqa: E402,F401  registra todos os modelos no mapper
