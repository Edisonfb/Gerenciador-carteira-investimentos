# Backend

Backend do gerenciador de carteiras de investimento.

Tecnologia principal: Python com FastAPI.

## Como executar futuramente

Executar os comandos abaixo dentro da pasta `backend/`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Organização

O backend segue uma divisão por módulos de negócio dentro de `app/modules/`.

Cada módulo deve separar rotas, schemas, serviços, repositórios e modelos.
