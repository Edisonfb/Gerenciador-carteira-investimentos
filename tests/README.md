# Testes

Pasta destinada aos testes do projeto.

## Organizacao

- `backend/unit/`: testes unitarios do backend.
- `backend/integration/`: testes de integracao do backend.
- `frontend/`: testes do frontend.
- `e2e/`: fluxos completos via API (cadastro, login, CRUD e regras).

## Como executar

Na raiz do projeto, com o ambiente virtual do backend ativo:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
cd ..
pytest
```

Os testes de backend/integracao/e2e usam SQLite em memoria e nao dependem do MySQL local.

Para o frontend:

```powershell
cd frontend
npm test
```
