# Pipeline do Sistema (v1)

Documento de referencia para **pessoas** e **outras IAs** entenderem o fluxo completo do projeto **antes** de ler ou alterar codigo.

Leia este arquivo primeiro. Depois use `architecture.md`, `api-contract.md`, `database.md`, `requirements.md` e `ai-guide.md` conforme a tarefa.

---

## 1. Objetivo deste documento

Explicar, de ponta a ponta:

- como uma acao do usuario percorre frontend, API, regras de negocio e banco;
- quais pastas e arquivos participam de cada etapa;
- quais regras nao podem ser quebradas ao evoluir o sistema;
- qual ordem de leitura e de alteracao outras IAs devem seguir.

Este documento descreve o **pipeline implementado na branch `v1`**, nao apenas a intencao inicial do repositorio.

---

## 2. Visao geral do pipeline

O sistema e um **monolito modular** em um unico repositorio, com quatro eixos principais:

```text
[Usuario]
   |
   v
[Frontend React]  --HTTP/JSON + JWT-->  [Backend FastAPI]
                                              |
                                              v
                                    [Service / regras]
                                              |
                                              v
                                    [Repository / SQLAlchemy]
                                              |
                                              v
                                    [MySQL via Docker Compose]
```

Separacao fixa de responsabilidades:

| Camada | O que faz | O que nao faz |
|--------|-----------|---------------|
| Frontend | UI, navegacao, estado de auth, chamadas HTTP | Regras de negocio de investimento |
| Router (backend) | HTTP, auth dependency, status code | Logica de negocio complexa |
| Service | Validacoes e regras de dominio | SQL direto |
| Repository | Consultas e persistencia | Decidir regras de negocio |
| Database | Persistencia e constraints | Conhecer UI ou endpoints |

Fluxo canonico de uma requisicao autenticada:

```text
Page/Component
  -> frontend/src/services/*
  -> apiRequest (Bearer JWT)
  -> backend router
  -> get_current_user (deps)
  -> service
  -> repository
  -> MySQL
  -> response JSON
  -> atualizacao da tela
```

---

## 3. Ordem de leitura recomendada

### Para humanos (primeiro contato)

1. `README.md` — como subir o ambiente
2. **`docs/pipeline.md`** (este arquivo) — como o sistema funciona
3. `docs/requirements.md` — o que o sistema deve fazer
4. `docs/architecture.md` — organizacao das pastas
5. `docs/api-contract.md` — endpoints
6. `docs/database.md` — modelo de dados

### Para IAs (antes de alterar arquivos)

1. `AGENTS.md`
2. **`docs/pipeline.md`**
3. `docs/architecture.md`
4. `docs/ai-guide.md`
5. Documento da area afetada (`api-contract`, `database`, `requirements`)
6. Codigo existente da camada alvo (nao reinventar estrutura)

Skill de implementacao: `.agents/skills/implement-task/SKILL.md`  
Skill de review: `.agents/skills/code-review/SKILL.md`

---

## 4. Pipeline de ambiente local (runtime)

Ordem obrigatoria para o sistema funcionar:

```text
1. .env (a partir de .env.example)
2. Docker Compose (MySQL + scripts em database/init/)
3. Backend (uvicorn em :8000)
4. Frontend (Vite em :5173)
```

### 4.1 Variaveis de ambiente

Arquivo raiz: `.env` (nao versionado). Modelo: `.env.example`.

Pontos criticos:

- `DATABASE_URL` — conexao SQLAlchemy/PyMySQL com o MySQL do Compose
- `SECRET_KEY` / `ACCESS_TOKEN_EXPIRE_MINUTES` / `JWT_ALGORITHM` — emissao e validacao JWT
- `CORS_ORIGINS` — origem do frontend (`http://localhost:5173`)

No frontend, a base da API e:

```text
VITE_API_BASE_URL ?? http://localhost:8000
```

definida em `frontend/src/services/api.ts`.

### 4.2 Banco (Docker)

Arquivo: `docker-compose.yml`

- Sobe MySQL 8 na porta `3306`
- Monta `database/init/` em `/docker-entrypoint-initdb.d`
- Scripts de init criam o schema **completo** na primeira subida do volume
- Migrations oficiais ficam em `database/migrations/` (historico versionado)

Backend e frontend **nao** rodam dentro do Docker na v1: so o MySQL.

Se o volume MySQL **ja existir** (banco antigo), o `init/` **nao** roda de novo. Aplique a migration manualmente no PowerShell:

```powershell
Get-Content database\migrations\002_roles_and_client_access.sql | docker exec -i investment_portfolio_mysql mysql -u portfolio_user -pportfolio_password investment_portfolio_manager
```

(Alternativa sem dados: `docker compose down -v` e depois `docker compose up -d`.)

### 4.3 Backend

```text
cd backend
python -m venv .venv
ativar venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Pontos de entrada:

- API: `http://localhost:8000`
- Health: `http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`

A raiz `/` **nao** tem rota; `{"detail":"Not Found"}` nela e esperado.

### 4.4 Frontend

```text
cd frontend
npm install
npm run dev
```

UI: `http://localhost:5173`

---

## 5. Pipeline do backend (detalhado)

### 5.1 Bootstrap da aplicacao

Arquivo central: `backend/app/main.py`

Responsabilidades:

1. cria `FastAPI`
2. configura CORS
3. registra routers dos modulos
4. registra handler de `ProjectException`
5. expoe `GET /health`
6. importa models para registrar metadata do SQLAlchemy

Modulos registrados:

| Modulo | Prefixo | Pasta |
|--------|---------|-------|
| auth | `/auth` | `backend/app/modules/auth/` |
| investors | `/investors` | `backend/app/modules/investors/` |
| portfolios | `/portfolios` | `backend/app/modules/portfolios/` |
| assets | `/assets` | `backend/app/modules/assets/` |
| transactions | `/transactions` | `backend/app/modules/transactions/` |

### 5.2 Anatomia de cada modulo

Cada modulo segue o mesmo pipeline interno:

```text
router.py
  -> instancia Service(db)
  -> service metodo de negocio
  -> repository consulta/grava
  -> model ORM
  -> MySQL
```

Arquivos obrigatorios por modulo:

| Arquivo | Papel no pipeline |
|---------|-------------------|
| `router.py` | Endpoints HTTP, Depends, status codes |
| `schemas.py` | Contrato Pydantic de entrada/saida |
| `service.py` | Regras, ownership, validacoes de dominio |
| `repository.py` | SQLAlchemy queries e persistencia |
| `models.py` | Tabelas / entidades ORM |

Infra compartilhada:

| Arquivo | Papel |
|---------|-------|
| `backend/app/core/config.py` | Settings a partir do `.env` |
| `backend/app/core/security.py` | Hash de senha e JWT |
| `backend/app/core/deps.py` | `get_db`, `get_current_user`, `get_current_analyst` |
| `backend/app/core/exceptions.py` | Excecoes de negocio (`ProjectException` e derivadas) |
| `backend/app/db/session.py` | Engine e `SessionLocal` |
| `backend/app/shared/validators.py` | Validadores reutilizaveis (ex.: tipos de transacao) |
| `backend/app/shared/roles.py` | Constantes de perfil (`analyst` / `client`) |
| `backend/app/shared/access.py` | Ownership compartilhado (analista dono ou cliente vinculado) |

### 5.3 Pipeline de uma requisicao protegida

Exemplo: `POST /transactions` com usuario logado.

```text
1. Cliente envia JSON + header Authorization: Bearer <token>
2. FastAPI resolve Depends(get_current_user)
3. oauth2_scheme le o Bearer token
4. decode_access_token extrai user_id
5. AuthRepository busca User no banco
6. Router recebe current_user + payload (schema)
7. Router cria TransactionService(db)
8. Service valida tipo, valores, ownership da carteira, ativo etc.
9. Service chama TransactionRepository.create(...)
10. Repository persiste Transaction
11. Router devolve TransactionResponse (201)
```

Se a regra de negocio falhar, o service lanca `ProjectException` (ou subtipo).  
O handler em `main.py` converte para JSON:

```json
{ "detail": "mensagem" }
```

com o status HTTP adequado.

### 5.4 Pipeline de autenticacao (backend)

Endpoints publicos de auth:

- `POST /auth/register` (cria analista)
- `POST /auth/login`
- `POST /auth/login/form` (OAuth2 form, usado pelo Swagger; fora do schema publico)

Endpoints protegidos:

- `GET /auth/me`
- `POST /auth/change-password`

Fluxo de login:

```text
email/senha
  -> AuthService valida credenciais
  -> compara password_hash
  -> security cria JWT com subject = user_id
  -> retorna { access_token, token_type: "bearer" }
```

Fluxo de registro (analista):

```text
name/email/password
  -> valida email unico
  -> gera password_hash
  -> cria User com role=analyst
  -> retorna UserResponse (sem senha)
```

Fluxo de pre-cadastro de cliente:

```text
analista autenticado
  -> POST /investors com dados regulatorios
  -> cria User role=client + senha temporaria (must_change_password=true)
  -> cria Investor ligado ao analista e a conta do cliente
  -> retorna InvestorAccessResponse com temporary_password (uma vez)
```

Dependencias:

- `Depends(get_current_user)` para qualquer autenticado
- `Depends(get_current_analyst)` para operacoes exclusivas do analista

### 5.5 Ownership e isolamento de dados

Regra transversal:

- investidores do analista: `investor.user_id == analyst.id`
- investidor do cliente: `investor.account_user_id == client.id`
- carteiras/transacoes: acesso se o usuario pode acessar o investidor dono
- services verificam ownership antes de ler/alterar (`shared/access.py`)

Exemplo tipico no service:

1. carregar recurso pelo id
2. se nao existir → `NotFoundError`
3. se nao pertencer ao usuario → `ForbiddenError`
4. se inativo (quando aplicavel) → erro de negocio/forbidden

Exclusoes:

- investidores, carteiras e ativos: exclusao **logica** (`is_active = false`)
- transacoes: exclusao **fisica** (`204 No Content`)

### 5.6 Pipeline de regras de transacao

Concentrado em `TransactionService` + `shared/validators.py`.

Tipos previstos (dominio): compra, venda, deposito, retirada, rendimento, taxa.

Validacoes tipicas no pipeline:

- tipo valido
- quantidade/preco/taxas nao negativos
- compra/venda exigem `asset_id` e valores positivos coerentes
- carteira deve existir, estar ativa e pertencer ao usuario
- ativo referenciado deve existir (quando obrigatorio)

O frontend **nao** deve duplicar essas regras; pode apenas melhorar UX com validacao de formulario basica.

---

## 6. Pipeline do frontend (detalhado)

### 6.1 Bootstrap

```text
main.tsx
  -> App.tsx
      -> BrowserRouter
      -> AuthProvider
      -> AppRoutes
```

Arquivos-chave:

- `frontend/src/main.tsx` — mount React
- `frontend/src/App.tsx` — providers
- `frontend/src/routes/AppRoutes.tsx` — rotas publicas/protegidas
- `frontend/src/styles/app.css` — estilos

### 6.2 Pipeline de autenticacao (frontend)

```text
LoginPage / RegisterPage (analista)
  -> authService.loginUser / registerUser
  -> apiRequest('/auth/login' | '/auth/register')
  -> setAccessToken no localStorage
  -> getCurrentUser (/auth/me)
  -> AuthProvider.setUser
  -> se must_change_password: ChangePasswordPage
  -> ProtectedRoute libera AppLayout + paginas por perfil
```

Componentes/hooks:

| Arquivo | Papel |
|---------|-------|
| `hooks/AuthProvider.tsx` | Estado global de usuario, login, register, changePassword, logout |
| `hooks/authContext.ts` | Contexto React |
| `hooks/useAuth.ts` | Hook de consumo |
| `components/ProtectedRoute.tsx` | Bloqueia rotas sem usuario / exige troca de senha |
| `components/AnalystRoute.tsx` | Bloqueia rotas exclusivas do analista |
| `components/AppLayout.tsx` | Shell/navegacao por perfil |
| `services/api.ts` | Cliente HTTP + token |
| `services/authService.ts` | Chamadas de auth |

Token:

- chave: `access_token` no `localStorage`
- enviado automaticamente por `apiRequest` quando `auth: true` (padrao)

### 6.3 Rotas da UI

Publicas:

- `/login`
- `/register` (analista)

Protegidas:

- `/change-password` (obrigatoria se `must_change_password`)
- `/` — home
- `/investors` — apenas analista
- `/portfolios`
- `/portfolios/:portfolioId/summary`
- `/assets`
- `/transactions`

Qualquer rota desconhecida redireciona para `/`.

### 6.4 Pipeline de uma tela de CRUD

Padrao usado nas pages (investors, portfolios, assets, transactions):

```text
1. Page monta e chama service de listagem
2. service usa apiRequest com JWT
3. API responde lista JSON
4. Page renderiza tabela/formulario
5. Submit chama create/update/delete no service
6. Em erro, exibe mensagem (ErrorBanner / feedback local)
7. Em sucesso, recarrega lista ou navega
```

Organizacao:

| Pasta | Conteudo |
|-------|----------|
| `pages/` | Telas e orquestracao de UI |
| `components/` | Layout, protecao de rota, banner de erro |
| `services/` | Um service por dominio da API |
| `types/api.ts` | Tipos TypeScript alinhados ao contrato |

Regra: **nao** colocar `fetch` direto nas pages; passar por `services/`.

---

## 7. Pipeline de dados (banco)

### 7.1 Modelo conceitual

```text
users (role: analyst | client)
  ├── investors via user_id          (analista pre-cadastra o cliente)
  └── investors via account_user_id  (conta de login do cliente)
        └── portfolios (investor_id)
              └── transactions (portfolio_id, asset_id opcional)

assets (cadastro global de ativos financeiros)
```

Campos relevantes de acesso:

- `users.role`, `users.must_change_password`
- `investors.account_user_id`, dados regulatorios (nome/sobrenome, RG, CPF, email, celular, endereco)

Detalhes: `docs/database.md` e scripts SQL.

### 7.2 Scripts

| Caminho | Uso |
|---------|-----|
| `database/init/` | Inicializacao automatica no primeiro `docker compose up` (schema atual) |
| `database/migrations/001_create_initial_tables.sql` | Schema inicial |
| `database/migrations/002_roles_and_client_access.sql` | Perfis + acesso do cliente |
| `database/seeds/` | Dados de exemplo (quando houver) |
| `database/diagrams/` | MER/DER |

### 7.3 Pipeline de mudanca de schema

Quando for necessario alterar o banco:

```text
1. Atualizar/criar migration em database/migrations/
2. Atualizar init se o ambiente local novo precisar nascer correto
3. Atualizar models.py dos modulos afetados
4. Atualizar docs/database.md
5. Atualizar docs/api-contract.md se o contrato mudar
6. Ajustar services/repositories/testes
```

Nunca espalhar SQL de schema em routers ou pages.

---

## 8. Pipeline de testes

Estrutura:

```text
tests/
├── backend/
│   ├── unit/          # regras isoladas (services, validators)
│   └── integration/   # API / repositories com app + DB de teste
├── e2e/               # fluxos amplos da API
├── frontend/          # testes do frontend
└── conftest.py        # fixtures compartilhadas
```

### 8.1 Como os testes de backend se conectam ao pipeline

`tests/conftest.py`:

1. sobe engine SQLite em memoria
2. cria metadata das models
3. sobrescreve `get_db` da app FastAPI
4. expoe fixtures `db` e `client` (`TestClient`)

Assim, testes exercitam o **mesmo pipeline** Router → Service → Repository, sem depender do MySQL Docker.

### 8.2 Comandos

```powershell
# na raiz do repo (Python)
pytest

# frontend
cd frontend
npm test
npm run lint
npm run build
```

Config Python: `pytest.ini` na raiz.

---

## 9. Pipeline de desenvolvimento em equipe / Git

Fluxo usado na v1:

```text
main (estavel do grupo)
  └── v1 (implementacao funcional)
        └── PR #1 (v1 -> main)
```

Boas praticas:

1. trabalhar em branch de feature/versao (`v1`, `v2`, etc.)
2. nao commitar `.env`
3. atualizar contrato/docs quando endpoint ou schema mudar
4. abrir PR para `main` apos smoke test local
5. IAs e humanos devem respeitar escopo da task (frontend **ou** backend **ou** banco **ou** testes **ou** docs), salvo pedido explicito multi-camada

---

## 10. Mapa mental: de uma acao do usuario ate o banco

### Exemplo A — Login (analista ou cliente)

```text
Usuario preenche email/senha
  -> LoginPage
  -> authService.loginUser
  -> POST /auth/login
  -> AuthService autentica
  -> JWT gerado
  -> token salvo no localStorage
  -> GET /auth/me (role + must_change_password)
  -> AuthProvider.user preenchido
  -> se must_change_password: ChangePasswordPage
  -> senao: area autenticada (menu conforme o perfil)
```

### Exemplo B — Pre-cadastro de cliente (analista)

```text
InvestorsPage submit
  -> investorService.createInvestor(...)
  -> POST /investors + Bearer
  -> get_current_analyst
  -> InvestorService.create_investor
  -> cria User role=client + senha temporaria
  -> InvestorRepository.create (user_id=analista, account_user_id=cliente)
  -> InvestorAccessResponse com temporary_password
  -> UI exibe senha uma vez e atualiza lista
```

### Exemplo C — Registrar compra

```text
TransactionsPage submit (tipo compra)
  -> transactionService.create(...)
  -> POST /transactions + Bearer
  -> TransactionService valida carteira/ativo/valores
  -> TransactionRepository.create(...)
  -> INSERT transactions
  -> response 201
  -> UI lista historico / permite abrir summary da carteira
```

### Exemplo D — Resumo da carteira

```text
PortfolioSummaryPage
  -> portfolioService.getSummary(portfolioId)
  -> GET /portfolios/{id}/summary
  -> service agrega posicoes/movimentacoes
  -> JSON consolidado
  -> UI exibe resumo
```

---

## 11. Contratos que outras IAs devem respeitar

Antes de gerar codigo, a IA deve assumir como verdade:

1. **Frontend nao redefine regra de negocio** — apenas consome API.
2. **Router nao concentra regra complexa** — delega ao service.
3. **Service nao escreve SQL** — usa repository.
4. **Repository nao decide politica de negocio** — persiste/consulta.
5. **Endpoints novos/alterados** exigem atualizacao de `docs/api-contract.md`.
6. **Schema novo/alterado** exige migration + `docs/database.md`.
7. **Escopo da task** e sagrado: nao “aproveitar” para refatorar outra camada.
8. **Nao inventar endpoints** que nao estejam no contrato ou no codigo.
9. **Nao commitar segredos** (`.env`, chaves reais).
10. Em duvida arquitetural, perguntar; nao improvisar um segundo padrao paralelo.

Checklist minimo para uma IA implementar uma feature:

```text
[ ] Li pipeline.md + architecture.md + ai-guide.md
[ ] Identifiquei a(s) camada(s) afetada(s)
[ ] Inspecionei modulo/pasta existente semelhante
[ ] Vou alterar apenas o necessario
[ ] Vou atualizar contrato/docs se a interface mudar
[ ] Vou criar/ajustar testes da mudanca
[ ] Vou informar escopo, arquivos e pendencias ao final
```

---

## 12. O que ja esta no pipeline da v1

Implementado de forma integrada:

- autenticacao JWT com perfis (`analyst` / `client`): register (analista), login, me, change-password
- pre-cadastro de clientes com senha temporaria e reemissao de acesso
- menus/rotas por perfil no frontend (`AnalystRoute`, troca obrigatoria de senha)
- CRUD de investidores/clientes, carteiras e ativos (com exclusao logica onde aplicavel)
- registro/consulta/edicao/exclusao de transacoes
- resumo de carteira
- frontend com rotas protegidas e services por dominio
- MySQL via Docker Compose + init/migrations (`002_roles_and_client_access`)
- base de testes unitarios, integracao e e2e da API

Ainda incremental / sujeito a evolucao:

- seeds ricos de demonstracao
- refinamentos de UX
- regras do estudo de caso ainda pendentes (objetivo %, cotacao, distancia, recomendacao de aporte, ticker B3)
- endurecimento de CI e qualidade

Consulte `docs/requirements.md` para o mapa de RFs.

---

## 13. Glossario rapido

| Termo | Significado neste projeto |
|-------|----------------------------|
| Pipeline | Caminho completo de uma acao ate a persistencia/resposta |
| Modulo | Pasta de negocio em `backend/app/modules/*` |
| Contrato | Acordo de endpoints/payloads em `api-contract.md` |
| Analista | Usuario `role=analyst`; pre-cadastra clientes |
| Cliente | Usuario `role=client`; acesso gerado pelo analista |
| Ownership | Garantia de que o recurso pertence ao analista dono ou ao cliente vinculado |
| Exclusao logica | Marcar `is_active=false` sem apagar a linha |
| Smoke test | Percorrer manualmente login → CRUD → resumo no browser |

---

## 14. Resumo em uma frase

**O pipeline da v1 leva toda acao do usuario do React (services + JWT) ate o FastAPI (router → service → repository) e ao MySQL no Docker, com documentacao e testes espelhando as mesmas fronteiras de responsabilidade.**
