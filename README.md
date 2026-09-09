# Gerenciador de Carteiras de Investimento

Projeto academico para gerenciamento de carteiras de investimento.

O sistema sera desenvolvido como um monolito modular: uma unica aplicacao, mas organizada por areas e responsabilidades para facilitar o trabalho em equipe.

## Objetivo

Criar uma aplicacao para cadastrar investidores, carteiras, ativos financeiros e transacoes, permitindo consultar informacoes consolidadas sobre os investimentos.

## Tecnologias

- Frontend: React com TypeScript.
- Backend: Python com FastAPI.
- Banco de dados: MySQL.
- Testes: Python com pytest.
- Documentacao: Markdown.

## Estrutura principal

```text
investment-portfolio-manager/
├── frontend/
├── backend/
├── database/
├── tests/
└── docs/
```

Responsabilidades:

- `frontend/`: interface da aplicacao.
- `backend/`: API, regras de negocio e acesso ao banco.
- `database/`: scripts, migrations, seeds e diagramas do banco.
- `tests/`: testes unitarios, integracao e e2e.
- `docs/`: documentacao tecnica do projeto.

## Documentos principais

Para entender ou retomar o projeto em outro chat, leia nesta ordem:

1. `docs/architecture.md`: arquitetura e separacao de responsabilidades.
2. `docs/requirements.md`: requisitos iniciais do sistema.
3. `docs/api-contract.md`: contrato inicial da API.
4. `docs/database.md`: modelo inicial do banco MySQL.
5. `docs/ai-guide.md`: regras para uso de IA no projeto, quando disponivel localmente.

## Uso de IA no projeto

Antes de pedir alteracoes para uma IA, informe o escopo da tarefa: backend, frontend, banco de dados, testes, documentacao ou configuracao.

A IA deve seguir a arquitetura definida em `docs/architecture.md` e respeitar o limite do pedido. Se o problema estiver fora do escopo, ela deve apenas registrar o problema e indicar a area responsavel.

O guia local para padronizacao do uso de IA fica em `docs/ai-guide.md`.

## Observacao

Os documentos deste projeto sao vivos. Eles comecam como uma base inicial e devem ser atualizados conforme o codigo, os testes e as decisoes do grupo evoluirem.
