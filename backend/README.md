# Backend

Backend do gerenciador de carteiras de investimento.

Tecnologia principal: Python com FastAPI.

## Como executar

Executar os comandos abaixo dentro da pasta `backend/`.

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
docker compose up -d mysql
.\backend\.venv\Scripts\python.exe .\database\migrations\create_tables.py
cd backend
uvicorn app.main:app --reload

O backend le as configuracoes de banco a partir do arquivo `backend/.env`.
Use as variaveis `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e `DB_PASSWORD`
ou, se preferir, informe uma `DATABASE_URL` completa.

Quando o banco estiver vazio, execute o script `database/migrations/create_tables.py`
antes de usar as rotas que gravam ou consultam dados.


## Organização

O backend segue uma divisão por módulos de negócio dentro de `app/modules/`.

Cada módulo deve separar rotas, schemas, serviços, repositórios e modelos.
