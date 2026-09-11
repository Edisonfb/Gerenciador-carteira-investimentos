# Contrato da API

Este documento registra o contrato entre frontend e backend.

Ele deve ser atualizado sempre que um endpoint for criado, removido ou alterado.

## 1. Padroes gerais

Base local prevista:

```text
http://localhost:8000
```

Formato padrao de dados:

```text
JSON
```

Autenticacao:

- tipo: JWT Bearer;
- apos o login, o frontend deve enviar o header `Authorization: Bearer <access_token>`;
- endpoints protegidos exigem token valido;
- endpoints publicos: `GET /health`, `POST /auth/register`, `POST /auth/login`.

Regras gerais:

- endpoints usam substantivos no plural;
- erros retornam codigo HTTP adequado e mensagem em `detail`;
- exclusao de investidores, carteiras e ativos e logica (`is_active = false`);
- exclusao de transacoes e fisica (`204 No Content`);
- alteracoes em endpoints usados pelo frontend devem ser combinadas antes.

## 2. Endpoint de saude

```text
GET /health
```

Publico. Verifica se a API esta disponivel.

```json
{
  "status": "ok",
  "app": "Gerenciador de Carteiras de Investimento"
}
```

## 3. Autenticacao

Prefixo:

```text
/auth
```

### POST /auth/register

Publico. Cadastra usuario.

Request:

```json
{
  "name": "Maria Silva",
  "email": "maria@example.com",
  "password": "senha123"
}
```

Response `201`:

```json
{
  "id": 1,
  "name": "Maria Silva",
  "email": "maria@example.com",
  "created_at": "2026-01-10T10:00:00",
  "updated_at": "2026-01-10T10:00:00"
}
```

Erros comuns: `409` email ja cadastrado; `422` dados invalidos.

### POST /auth/login

Publico. Autentica com email e senha (JSON).

Request:

```json
{
  "email": "maria@example.com",
  "password": "senha123"
}
```

Response `200`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Erros comuns: `401` email ou senha invalidos.

### GET /auth/me

Protegido. Retorna o usuario autenticado.

Response `200`: mesmo formato de usuario do register.

## 4. Investidores

Prefixo protegido:

```text
/investors
```

```text
GET    /investors
GET    /investors/{investor_id}
POST   /investors
PUT    /investors/{investor_id}
DELETE /investors/{investor_id}
```

### POST /investors

```json
{
  "name": "Investidor Exemplo",
  "document": "12345678901",
  "email": "investidor@example.com"
}
```

`email` e opcional.

### Response de investidor

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Investidor Exemplo",
  "document": "12345678901",
  "email": "investidor@example.com",
  "is_active": true,
  "created_at": "2026-01-10T10:00:00",
  "updated_at": "2026-01-10T10:00:00"
}
```

`DELETE` desativa o investidor (`is_active = false`) e devolve o registro atualizado.

## 5. Carteiras

Prefixo protegido:

```text
/portfolios
```

```text
GET    /portfolios
GET    /portfolios/{portfolio_id}
POST   /portfolios
PUT    /portfolios/{portfolio_id}
DELETE /portfolios/{portfolio_id}
GET    /portfolios/{portfolio_id}/summary
```

### POST /portfolios

```json
{
  "investor_id": 1,
  "name": "Carteira Principal",
  "description": "Longo prazo"
}
```

### Response de carteira

```json
{
  "id": 1,
  "investor_id": 1,
  "name": "Carteira Principal",
  "description": "Longo prazo",
  "is_active": true,
  "created_at": "2026-01-10T10:00:00",
  "updated_at": "2026-01-10T10:00:00"
}
```

### GET /portfolios/{portfolio_id}/summary

```json
{
  "portfolio_id": 1,
  "portfolio_name": "Carteira Principal",
  "total_invested": "305.00000000",
  "total_fees": "0.00000000",
  "cash_flow": "-305.00000000",
  "positions": [
    {
      "asset_id": 1,
      "symbol": "PETR4",
      "name": "Petrobras",
      "quantity": "10.00000000",
      "average_price": "30.50000000",
      "total_invested": "305.00000000"
    }
  ],
  "transactions_count": 1
}
```

Valores monetarios/quantidade podem ser serializados como string decimal.

## 6. Ativos financeiros

Prefixo protegido:

```text
/assets
```

```text
GET    /assets
GET    /assets/{asset_id}
POST   /assets
PUT    /assets/{asset_id}
DELETE /assets/{asset_id}
```

### POST /assets

```json
{
  "symbol": "PETR4",
  "name": "Petrobras",
  "asset_type": "acao"
}
```

Tipos aceitos de `asset_type`:

- `acao`
- `fundo_imobiliario`
- `renda_fixa`
- `etf`
- `cripto`
- `outro`

`DELETE` desativa o ativo (`is_active = false`).

## 7. Transacoes

Prefixo protegido:

```text
/transactions
```

```text
GET    /transactions
GET    /transactions/{transaction_id}
POST   /transactions
PUT    /transactions/{transaction_id}
DELETE /transactions/{transaction_id}
```

### POST /transactions

```json
{
  "portfolio_id": 1,
  "asset_id": 1,
  "transaction_type": "compra",
  "quantity": "10",
  "unit_price": "30.5",
  "transaction_date": "2026-01-10T10:00:00",
  "fees": "0",
  "notes": "compra inicial"
}
```

Tipos aceitos de `transaction_type`:

- `compra`
- `venda`
- `deposito`
- `retirada`
- `rendimento`
- `taxa`

Regras relevantes:

- `compra`, `venda` e `rendimento` exigem `asset_id`;
- valores negativos de quantidade, preco ou taxas nao sao permitidos;
- `venda` nao pode superar a quantidade disponivel na carteira;
- `DELETE` remove a transacao e retorna `204`.

## 8. Padrao de erro

```json
{
  "detail": "Mensagem explicando o erro."
}
```

Codigos comuns:

- `400`: dados invalidos ou regra de negocio violada;
- `401`: usuario nao autenticado ou credenciais invalidas;
- `403`: usuario sem permissao;
- `404`: recurso nao encontrado;
- `409`: conflito (ex.: email ou documento duplicado);
- `422`: validacao de schema;
- `500`: erro inesperado no servidor.

## 9. Observacoes para o frontend

- consumir apenas endpoints deste documento;
- guardar o `access_token` apos o login e envia-lo nas requisicoes protegidas;
- se uma tela precisar de campo ou endpoint inexistente, registrar a necessidade aqui antes de alterar o backend.
