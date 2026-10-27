# Contrato da API

Este documento registra o contrato inicial entre frontend e backend.

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

Regras gerais:

- endpoints devem usar substantivos no plural quando representarem recursos;
- respostas devem ser previsiveis para facilitar o consumo pelo frontend;
- erros devem retornar codigo HTTP adequado e mensagem clara;
- alteracoes em endpoints usados pelo frontend devem ser combinadas antes.

## 2. Endpoint de saude

```text
GET /health
```

Objetivo: verificar se a API esta disponivel.

Resposta esperada:

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

Endpoints planejados:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

Responsabilidade:

- cadastrar usuario;
- autenticar usuario;
- retornar dados do usuario logado.

Observacao: o formato final de autenticacao ainda sera definido no backend.

## 4. Investidores

Prefixo:

```text
/investors
```

Endpoints planejados:

```text
GET    /investors
GET    /investors/{investor_id}
POST   /investors
PUT    /investors/{investor_id}
DELETE /investors/{investor_id}
```

Responsabilidade:

- cadastrar investidores;
- listar investidores;
- consultar um investidor especifico;
- atualizar dados de investidor;
- remover ou desativar investidor.

## 5. Carteiras

Prefixo:

```text
/portfolios
```

Endpoints planejados:

```text
GET    /portfolios
GET    /portfolios/{portfolio_id}
POST   /portfolios
PUT    /portfolios/{portfolio_id}
DELETE /portfolios/{portfolio_id}
GET    /portfolios/{portfolio_id}/summary
```

Responsabilidade:

- criar carteiras;
- listar carteiras;
- consultar detalhes de uma carteira;
- atualizar uma carteira;
- remover ou desativar uma carteira;
- consultar resumo consolidado da carteira.

## 6. Ativos financeiros

Prefixo:

```text
/assets
```

Endpoints planejados:

```text
GET    /assets
GET    /assets/setor/{setor}
GET    /assets/{asset_id}
POST   /assets
PUT    /assets/{asset_id}
DELETE /assets/{asset_id}
```

Responsabilidade:

- cadastrar ativos financeiros;
- listar ativos;
- consultar ativo especifico;
- atualizar dados de ativo;
- remover ou desativar ativo.

Exemplos de ativos:

- acao;
- fundo imobiliario;
- renda fixa;
- criptoativo;
- ETF;
- outro.

### 6.1. Consulta de ativos por setor

Endpoint implementado:

```text
GET /assets/setor/{setor}
```

Objetivo: retornar os ativos cadastrados que pertencem ao setor informado.

- Autenticacao: enviar `Authorization: Bearer <token>` de um investidor ativo.
- Parametro de caminho: `setor`, texto obrigatorio com o nome completo do setor.
- O service remove espacos das pontas do parametro antes da consulta.
- O repository compara o campo `Ativo.setor` por igualdade; nao realiza busca parcial. A distincao entre maiusculas e minusculas depende da configuracao do banco.
- A consulta nao aplica filtro adicional pelo status `ativo`.

Exemplo de requisicao:

```text
GET /assets/setor/Energia
```

Resposta de sucesso: `200 OK`, com uma lista de objetos contendo os campos de `AtivoSaida`: `id_ativo`, `codigo`, `setor`, `ativo` e `data_criacao`.

Quando nao houver ativos no setor informado, retorna `200 OK` com uma lista vazia:

```json
[]
```

Erros de acesso:

- `401`: token ausente, invalido ou expirado, ou usuario inexistente ou inativo;
- `403`: usuario autenticado sem perfil do tipo investidor.

Esta consulta usa uma rota especifica por setor. O parametro `setor` nao e um filtro de query implementado em `GET /assets`.

## 7. Transacoes

Prefixo:

```text
/transactions
```

Endpoints planejados:

```text
GET    /transactions
GET    /transactions/{transaction_id}
POST   /transactions
PUT    /transactions/{transaction_id}
DELETE /transactions/{transaction_id}
```

Responsabilidade:

- registrar compras;
- registrar vendas;
- consultar historico de transacoes;
- corrigir ou remover registros, se permitido pela regra de negocio.

Tipos iniciais de transacao:

- compra;
- venda;
- deposito;
- retirada;
- rendimento;
- taxa.

## 8. Padrao inicial de erro

Formato sugerido:

```json
{
  "detail": "Mensagem explicando o erro."
}
```

Codigos comuns:

- `400`: dados invalidos ou regra de negocio violada;
- `401`: usuario nao autenticado;
- `403`: usuario sem permissao;
- `404`: recurso nao encontrado;
- `500`: erro inesperado no servidor.

## 9. Observacoes para o frontend

O frontend deve consumir endpoints definidos neste documento.

Se uma tela precisar de um campo ou endpoint que ainda nao existe, registrar a necessidade aqui antes de implementar alteracoes fora do escopo do frontend.
