# Gerenciador de Carteiras de Investimento

Projeto academico para gerenciamento de carteiras de investimento, desenvolvido como parte do Projeto Final do IFRS.

O sistema tem como objetivo permitir o cadastro e acompanhamento de investidores, carteiras, ativos financeiros e transacoes, centralizando informacoes importantes para consulta e organizacao dos investimentos.

## Status do projeto

Em desenvolvimento.

A estrutura inicial do repositorio, a base do backend, a base do frontend e os documentos tecnicos principais ja foram criados. As funcionalidades do sistema ainda serao implementadas de forma incremental.

## Funcionalidades planejadas

- Cadastro e autenticacao de usuarios.
- Gerenciamento de investidores.
- Gerenciamento de carteiras de investimento.
- Gerenciamento de ativos financeiros.
- Registro de transacoes.
- Consulta do historico de transacoes.
- Consulta de resumo consolidado da carteira.
- Validacoes de regras de negocio relacionadas a investimentos.

## Tecnologias

- Frontend: React com TypeScript e Vite.
- Backend: Python com FastAPI.
- Banco de dados: MySQL.
- ORM / banco: SQLAlchemy e PyMySQL.
- Testes: pytest, httpx e pytest-asyncio.
- Ambiente local: Docker Compose para MySQL.

## Arquitetura

O projeto segue uma arquitetura de monolito modular. A aplicacao fica em um unico repositorio, mas separada por responsabilidades para facilitar manutencao, organizacao e trabalho em equipe.

Fluxo principal esperado:

```text
Frontend -> Router -> Service -> Repository -> Banco de dados
```

Principios importantes:

- o frontend consome a API e nao redefine regras de negocio;
- as rotas do backend recebem requisicoes HTTP e delegam regras para services;
- services concentram regras de negocio;
- repositories concentram acesso ao banco de dados;
- alteracoes no banco devem ser documentadas e organizadas em scripts ou migrations.

## Estrutura do repositorio

```text
Gerenciador-carteira-investimentos/
├── backend/
│   └── app/
│       ├── core/
│       ├── db/
│       ├── modules/
│       └── shared/
├── database/
│   ├── diagrams/
│   ├── init/
│   ├── migrations/
│   └── seeds/
├── docs/
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── routes/
│       ├── services/
│       ├── styles/
│       └── types/
└── tests/
    ├── backend/
    ├── e2e/
    └── frontend/
```

## Como executar localmente

### Pre-requisitos

- Git.
- Node.js.
- Python.
- Docker Desktop ou Docker Compose.

### 1. Clonar o repositorio

```powershell
git clone <url-do-repositorio>
cd Gerenciador-carteira-investimentos
```

### 2. Configurar variaveis de ambiente

Copie o arquivo de exemplo:

```powershell
copy .env.example .env
```

Depois ajuste os valores conforme o ambiente local, se necessario.

### 3. Subir o banco de dados

Na raiz do projeto:

```powershell
docker compose up -d
```

Esse comando inicia o MySQL usando as configuracoes do `docker-compose.yml`.

### 4. Executar o backend

Entre na pasta do backend:

```powershell
cd backend
```

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Inicie a API:

```powershell
uvicorn app.main:app --reload
```

Por padrao, a API ficara disponivel em:

```text
http://localhost:8000
```

A documentacao interativa do FastAPI pode ser acessada em:

```text
http://localhost:8000/docs
```

### 5. Executar o frontend

Em outro terminal, entre na pasta do frontend:

```powershell
cd frontend
```

Instale as dependencias:

```powershell
npm install
```

Inicie o servidor de desenvolvimento:

```powershell
npm run dev
```

Por padrao, o frontend ficara disponivel em:

```text
http://localhost:5173
```

## Testes

Os testes ficam na pasta `tests/`.

Quando os testes estiverem implementados, eles poderao ser executados a partir da configuracao definida para cada area do projeto.

Para testes Python:

```powershell
pytest
```

Para verificacao do frontend:

```powershell
cd frontend
npm run lint
npm run build
```
