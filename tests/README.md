# Testes

Testes das histórias de usuário, separados por sprint.

## Organizacao

- `backend/sprint1/`, `backend/sprint2/` e `backend/sprint3/`: pytest, httpx e pytest-asyncio (banco falso SQLite em memória; Yahoo Finance falso na Sprint 3).
- `frontend/sprint1/` e `frontend/sprint2/`: vitest (fetch e localStorage falsos).
- `rodar_testes.py`: roda tudo e gera `relatorios/relatorio_testes.txt`.

Detalhes e lista de histórias em `despejo_testes.txt`.
