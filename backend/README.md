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


## Recuperação de senha e primeiro acesso

A tela de login identifica o perfil pela API (`/auth/me`), sem seleção manual.
Analistas entram em `/dashboard`; investidores entram em `/minha-conta`.
As rotas protegidas validam a sessão na API antes de exibir cada área.

- `POST /auth/esqueci-senha`: recebe `email` e envia um link para uma conta ativa.
- `POST /auth/primeiro-acesso`: recebe `email` e envia um link para investidores
  que ainda possuem a senha inicial do cadastro.
- `POST /auth/redefinir-senha`: recebe `token` e `senha` e grava a nova senha.

O primeiro acesso usa uma conta previamente cadastrada pelo responsável.
Os links expiram em 30 minutos e são invalidados após a troca da senha.
Tokens de definição de senha não são aceitos como tokens de login.

Configure no `.env` da raiz (ou `backend/.env`): `SMTP_HOST`, `SMTP_PORT`,
`SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` e `FRONTEND_URL`.
Sem servidor e remetente SMTP configurados, as solicitações retornam uma
mensagem de indisponibilidade. O endereço do frontend deve apontar para a
aplicação, por exemplo `http://localhost:5173`.

Para executar os testes deste fluxo, na raiz do projeto:

```powershell
$env:PYTHONPATH = "backend"
.\backend\.venv\Scripts\python.exe -m pytest tests/backend/unit/services/test_password_service.py -q
```
