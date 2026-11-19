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

### 3.1. Recuperacao de senha implementada

`POST /auth/esqueci-senha` recebe o email principal de identificacao da conta:

```json
{"email": "principal@exemplo.test"}
```

O email e normalizado para minusculas e sem espacos nas pontas. Para investidores ativos, o link e enviado exclusivamente ao campo `investidor.email_recuperacao`. Se o campo estiver ausente ou vazio, nao ha envio e nao existe alternativa automatica para o email principal. Para analistas ativos, que nao possuem esse campo no modelo atual, o envio permanece no email da conta.

A resposta e generica para contas existentes, inexistentes, inativas ou sem email de recuperacao, sem revelar o destinatario. SMTP ausente retorna `503`; falhas de transporte sao registradas sem expor se a conta existe. A funcao `enviar_link_senha(email, link)` cuida da mensagem de redefinicao; `enviar_token_acesso(email, token)` continua atendendo o convite inicial de investidores.

O link aponta para `/definir-senha?token=...` no frontend, expira em 30 minutos e e invalidado apos a mudanca da senha. `POST /auth/redefinir-senha` recebe `token` e `senha` (minimo de 8 caracteres e maximo de 72 bytes UTF-8), valida assinatura/finalidade/expiracao e altera a senha protegida no banco. O token de redefinicao nao serve como token de login. O email de recuperacao ja existe no modelo, sem necessidade de migracao para esta alteracao.

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
POST   /portfolios/{portfolio_id}/contribution-simulation
```

Responsabilidade:

- criar carteiras;
- listar carteiras;
- consultar detalhes de uma carteira;
- atualizar uma carteira;
- remover ou desativar uma carteira;
- consultar resumo consolidado da carteira.

### 5.1. Simulacao de aporte

`POST /portfolios/{portfolio_id}/contribution-simulation` exige investidor autenticado
e recebe `{"aporte": "1200.00"}`. O aporte deve ser positivo, em reais e com no
maximo duas casas decimais. A rota nao grava compras, vendas ou saldo financeiro.

Para cada ativo vinculado, o backend consulta a cotacao atual (ou a ultima salva,
conforme a regra de `GET /quotes/{ticker}`), multiplica pela quantidade atual e
calcula sua participacao no patrimonio. Com as metas percentuais da carteira,
sugere compras em lotes de **100 acoes**, sem ultrapassar o aporte. O custo de um
lote e `100 * cotacao`, nao R$ 100. A sugestao pode deixar saldo se outro lote
nao couber ou nao aproximar a carteira das metas.

As distancias sao calculadas em pontos percentuais como `participacao - objetivo`:
negativas abaixo da meta, positivas acima e zero quando a meta e atingida.
Essa convencao vale para `distancia_atual` e `distancia_projetada`.

Resposta `200` (valores ilustrativos):

```json
{
  "id_carteira": 1, "patrimonio_atual": "1000.00", "aporte": "1000.00",
  "valor_investido": "1000.00", "saldo_restante": "0.00",
  "patrimonio_projetado": "2000.00",
  "ativos": [
    {
      "ticker": "AAAA3", "cotacao": "10.00", "data_atualizacao": "2026-11-16T12:00:00",
      "objetivo_percentual": "50.00", "quantidade_atual": 100,
      "valor_atual": "1000.00", "participacao_atual": "100.00",
      "distancia_atual": "50.00", "quantidade_sugerida": 0,
      "custo_sugerido": "0.00", "quantidade_projetada": 100,
      "valor_projetado": "1000.00", "participacao_projetada": "50.00",
      "distancia_projetada": "0.00"
    },
    {
      "ticker": "BBBB4", "cotacao": "10.00", "data_atualizacao": "2026-11-16T12:00:00",
      "objetivo_percentual": "50.00", "quantidade_atual": 0,
      "valor_atual": "0.00", "participacao_atual": "0.00",
      "distancia_atual": "-50.00", "quantidade_sugerida": 100,
      "custo_sugerido": "1000.00", "quantidade_projetada": 100,
      "valor_projetado": "1000.00", "participacao_projetada": "50.00",
      "distancia_projetada": "0.00"
    }
  ]
}
```

`404` indica carteira inexistente ou de outro investidor. `400` indica carteira
desativada, vazia, ativo desativado ou metas que nao somam 100%. `422` indica
aporte invalido ou campos extras. `503` indica cotacao indisponivel. As cotacoes
e as sugestoes sao uma estimativa do momento da consulta; registrar a compra
continua exigindo que o investidor informe o preco efetivamente pago.

## 6. Ativos financeiros

As rotas abaixo estao implementadas e exigem `Authorization: Bearer <token>` de um investidor ativo.

```text
GET  /assets
GET  /assets/setor/{setor}
GET  /assets/{ticker}
POST /assets/carteira
GET  /assets/carteira/{id_carteira}
PATCH /assets/carteira/{id_carteira}/{ticker}
DELETE /assets/carteira/{id_carteira}/{ticker}
```

### 6.1. Catalogo e consulta por setor

`GET /assets` retorna o catalogo ordenado por ticker. Aceita `?ticker=PETR4` ou o alias anterior `?codigo=PETR4`, com busca exata apos remover espacos das pontas e converter para maiusculas. Se os dois parametros forem enviados com valores diferentes, retorna `422`.

`GET /assets/{ticker}` consulta um ativo pelo ticker e retorna `404` se nao existir. O identificador publico foi adaptado de ID numerico para ticker na integracao com a implementacao do colega. A resposta passou a usar os campos `ticker`, `nome`, `setor`, `subsetor`, `segmento`, `ativo` e `data_criacao`.

`GET /assets/setor/{setor}` recupera a funcionalidade da branch backup. Remove espacos das pontas e compara o setor completo por igualdade; a distincao entre maiusculas e minusculas depende da configuracao do banco. A consulta nao e um filtro de query de `GET /assets`.

As consultas retornam tambem ativos desativados, preservando o comportamento anterior do catalogo. Listas sem resultados retornam `200` com `[]`. A consulta individual retorna `200` com um objeto.

A API do investidor nao oferece cadastro, atualizacao ou exclusao do catalogo global: POST /assets, PUT /assets/{ticker} e DELETE /assets/{ticker} retornam `405`. A manutencao interna usa schemas validados; ticker e uma chave estavel e nao e alterado pela atualizacao descritiva.

### 6.2. Ativos de uma carteira

Exemplo de entrada em `POST /assets/carteira`:

```json
{"ticker": "PETR4", "id_carteira": 1, "quantidade": 10}
```

Ticker e normalizado para maiusculas, aceita letras e numeros e tem no maximo 10 caracteres. `quantidade` deve ser um inteiro entre 1 e 2147483647; booleanos, strings, fracionarios, zero e negativos sao rejeitados com `422`. Campos extras sao proibidos, inclusive identificadores de investidor enviados no corpo.

O investidor e identificado pela sessao. A carteira deve pertencer a ele e estar ativa; o ativo deve existir e estar ativo. Cadastro bem-sucedido retorna `201`:

```json
{"ticker": "PETR4", "id_carteira": 1, "quantidade": 10}
```

Um segundo cadastro do mesmo ticker na mesma carteira retorna `409`, sem somar nem substituir a quantidade. Conflitos de integridade concorrentes tambem retornam `409`, com rollback da transacao.

`GET /assets/carteira/{id_carteira}` retorna somente os vinculos da carteira do investidor, ordenados por ticker; carteira propria vazia retorna `200` com `[]`. Carteiras proprias desativadas continuam consultaveis, mas nao recebem novos ativos.

Erros previstos:

- `401`: token ausente, invalido ou expirado; usuario inexistente ou inativo.
- `403`: usuario autenticado sem perfil de investidor.
- `404`: perfil de investidor ausente; carteira inexistente ou alheia; ativo inexistente no cadastro.
- `400`: carteira ou ativo desativado no cadastro.
- `409`: vinculo duplicado ou conflito de integridade.
- `422`: corpo fora do contrato.

Carteira alheia e carteira inexistente retornam a mesma mensagem, `Carteira nao encontrada.` (com acentuacao na API), sem revelar o proprietario ou seus ativos.

### 6.3. Atualizacao e remocao de ativos da carteira

`PATCH /assets/carteira/{id_carteira}/{ticker}` substitui a quantidade atual, sem somar:

```json
{"quantidade": 7}
```

Quantidade inteira positiva retorna `200` com `ticker`, `id_carteira` e a nova `quantidade`. O ativo e a carteira devem estar ativos para essa atualizacao. A quantidade zero remove completamente o vinculo e retorna `204` sem corpo; zero nunca e salvo na tabela. O cadastro por POST continua exigindo quantidade positiva.

`DELETE /assets/carteira/{id_carteira}/{ticker}` remove diretamente o vinculo, independentemente da quantidade atual, e retorna `204` sem corpo. A remocao direta ou por zero tambem e permitida em carteira/ativo desativado. O ativo do catalogo e os vinculos de outras carteiras sao preservados.

Ambas as rotas exigem investidor autenticado e verificam a propriedade antes de acessar o vinculo. Carteira alheia/inexistente retorna `404`; vinculo ausente em carteira propria tambem retorna `404`. Ticker e normalizado. Quantidades negativas, booleanos, fracionarios, strings, nulos e campos extras sao rejeitados com `422`. Falhas de integridade concorrentes retornam `409`, com rollback. A estrutura do banco continua exigindo `quantidade > 0`, sem alteracao de tabela ou migration.

## 7. Cotacoes

```text
GET /quotes/{ticker}
```

Exige `Authorization: Bearer <token>` de um investidor ativo. Retorna o preco atual do ativo, consultado no Yahoo Finance (`{ticker}.SA`):

```json
{"ticker": "PETR4", "preco": "47.12", "data_atualizacao": "2026-11-05T01:36:47"}
```

A cotacao fica salva na tabela `cotacao`. Por 15 minutos o valor salvo e devolvido sem nova consulta ao Yahoo. Depois disso, o Yahoo e consultado de novo e o banco e atualizado. Se o Yahoo nao responder, a API devolve a ultima cotacao salva; `data_atualizacao` (UTC) indica a idade do valor.

Erros:

- `401`/`403`: sem login de investidor.
- `404`: ticker fora do catalogo de ativos (o Yahoo nao e consultado).
- `503`: Yahoo indisponivel e nenhuma cotacao salva para o ativo.

Para mostrar o valor total antes de confirmar uma compra ou venda, o frontend consulta esta rota e multiplica `preco` pela quantidade.

## 8. Transacoes

Prefixo:

```text
/transactions
```

Endpoints implementados (investidor autenticado):

```text
POST /transactions
GET  /transactions
```

Somente compra e venda. Nao ha edicao nem exclusao de transacoes.

### 8.1. Registro de transacao

Entrada de `POST /transactions`:

```json
{"id_carteira": 1, "ticker": "PETR4", "tipo": "compra", "quantidade": 200, "preco_unitario": "47.10"}
```

O investidor informa a quantidade e o preco unitario efetivamente pago; a cotacao atual nao substitui esse preco. Opcionalmente, pode informar `data_transacao` com fuso horario, desde que nao seja futura. Sem esse campo, a data e o momento do registro (UTC). Resposta `201`:

```json
{
  "id_transacao": 1, "id_carteira": 1, "nome_carteira": "Aposentadoria",
  "ticker": "PETR4", "tipo": "compra", "quantidade": 200,
  "preco_unitario": "47.10", "valor_total": "9420.00",
  "data_transacao": "2026-11-05T01:40:00"
}
```

Regras:

- `quantidade` em lotes de 100 acoes (100, 200, 300...). Outros valores retornam `400`.
- A carteira deve pertencer ao investidor e estar ativa.
- O ativo precisa ja estar na carteira (incluido com objetivo); a compra so altera a quantidade.
- Compra soma a quantidade em `ativo_carteira`; venda subtrai. Venda maior que a quantidade atual retorna `400`.
- A transacao e a nova quantidade sao gravadas juntas: se uma falhar, nenhuma e salva.

Erros:

- `400`: lote invalido, carteira desativada, ativo desativado (compra) ou quantidade insuficiente (venda).
- `401`/`403`: sem login de investidor.
- `404`: carteira inexistente ou alheia, ativo inexistente, ativo fora da carteira.
- `409`: conflito ao gravar.
- `422`: corpo fora do contrato (tipo diferente de compra/venda, quantidade nao inteira ou nao positiva, preco ausente ou invalido, campos extras).

### 8.2. Historico de transacoes

`GET /transactions` lista somente as transacoes do investidor logado, das mais recentes para as mais antigas. Filtros opcionais por query: `id_carteira`, `ticker` e `tipo` (`compra` ou `venda`). Lista vazia retorna `200` com `[]`.

Cada item tem o mesmo formato da resposta do registro. Se a carteira for excluida, as transacoes continuam no historico com `nome_carteira` preenchido e `id_carteira` nulo.

## 9. Padrao inicial de erro

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

## 10. Observacoes para o frontend

O frontend deve consumir endpoints definidos neste documento.

Se uma tela precisar de um campo ou endpoint que ainda nao existe, registrar a necessidade aqui antes de implementar alteracoes fora do escopo do frontend.
