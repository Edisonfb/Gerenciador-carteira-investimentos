# Arquitetura do Projeto

Este documento resume a arquitetura inicial do Gerenciador de Carteiras de Investimento.

O projeto sera desenvolvido como um monolito modular: uma unica aplicacao, mas com separacao clara entre frontend, backend, banco de dados, testes e documentacao.

## 1. Objetivo da arquitetura

A arquitetura deve permitir que o grupo trabalhe em paralelo sem misturar responsabilidades.

Principios principais:

- cada area deve ter uma responsabilidade clara;
- cada modulo deve concentrar uma parte do negocio;
- alteracoes devem ser pequenas e localizadas;
- o backend nao deve misturar rota, regra de negocio e acesso ao banco no mesmo arquivo;
- o frontend deve consumir a API sem redefinir regras do backend;
- o banco deve ser alterado por scripts, migrations e documentacao.

## 2. Estrutura geral

```text
investment-portfolio-manager/
├── frontend/
├── backend/
├── database/
├── tests/
└── docs/
```

Responsabilidades:

- `frontend/`: interface do usuario, telas, componentes e consumo da API.
- `backend/`: API, regras de negocio, validacoes, autenticacao e acesso ao banco.
- `database/`: scripts, migrations, seeds, diagramas e materiais do MySQL.
- `tests/`: testes unitarios, integracao e e2e.
- `docs/`: documentacao tecnica e guias do projeto.

## 3. Backend

Tecnologia oficial: Python com FastAPI.

Estrutura inicial:

```text
backend/
└── app/
    ├── main.py
    ├── core/
    ├── db/
    ├── modules/
    │   ├── auth/
    │   ├── investors/
    │   ├── portfolios/
    │   ├── assets/
    │   └── transactions/
    └── shared/
```

Responsabilidades:

- `main.py`: cria a aplicacao FastAPI e registra as rotas.
- `core/`: configuracoes, seguranca, excecoes e recursos centrais.
- `db/`: conexao, sessao e base dos modelos do banco.
- `modules/`: modulos de negocio da aplicacao.
- `shared/`: utilitarios reutilizaveis por mais de um modulo.

## 4. Padrao dos modulos do backend

Cada modulo dentro de `backend/app/modules/` deve seguir este padrao:

```text
modules/nome_do_modulo/
├── router.py
├── schemas.py
├── service.py
├── repository.py
└── models.py
```

Responsabilidades:

- `router.py`: endpoints HTTP do modulo.
- `schemas.py`: entradas e saidas da API usando Pydantic.
- `service.py`: regras de negocio.
- `repository.py`: acesso ao banco de dados.
- `models.py`: modelos persistidos no banco.

Fluxo recomendado:

```text
Frontend -> Router -> Service -> Repository -> Banco de dados
```

Regras:

- `router.py` nao deve conter regra de negocio complexa.
- `service.py` nao deve acessar diretamente o banco quando existir `repository.py`.
- `repository.py` nao deve decidir regra de negocio.
- `models.py` nao deve conter logica de API.
- `schemas.py` deve representar os contratos de entrada e saida.

## 5. Frontend

Tecnologia oficial: React com TypeScript.

Estrutura sugerida:

```text
frontend/
└── src/
    ├── components/
    ├── pages/
    ├── services/
    ├── hooks/
    ├── types/
    ├── routes/
    └── styles/
```

Responsabilidades:

- `components/`: partes reutilizaveis da interface.
- `pages/`: telas principais.
- `services/`: chamadas para a API.
- `hooks/`: hooks reutilizaveis.
- `types/`: tipos e interfaces TypeScript.
- `routes/`: configuracao de rotas do frontend.
- `styles/`: estilos globais ou compartilhados.

O frontend deve seguir o contrato definido em `docs/api-contract.md`.

## 6. Banco de dados

Tecnologia oficial: MySQL.

Estrutura sugerida:

```text
database/
├── migrations/
├── seeds/
├── diagrams/
└── init/
```

Responsabilidades:

- `migrations/`: alteracoes oficiais de estrutura do banco.
- `seeds/`: dados iniciais ou de exemplo.
- `diagrams/`: diagramas MER, DER e materiais visuais.
- `init/`: scripts para inicializacao local do banco.

A aplicacao deve acessar o banco por meio dos repositorios do backend.

## 7. Testes

Estrutura sugerida:

```text
tests/
├── backend/
│   ├── unit/
│   └── integration/
├── frontend/
└── e2e/
```

Tipos:

- testes unitarios: validam funcoes e regras isoladas;
- testes de integracao: validam interacao entre API, servicos, repositorios e banco;
- testes e2e: validam fluxos completos da aplicacao.

## 8. Decisoes iniciais

- O projeto sera mantido como monolito modular.
- MySQL sera usado como banco relacional.
- FastAPI sera usado para expor a API.
- React com TypeScript sera usado no frontend.
- A comunicacao entre front e back deve seguir o contrato da API.
- Documentos longos devem ser divididos em arquivos menores dentro de `docs/`.
