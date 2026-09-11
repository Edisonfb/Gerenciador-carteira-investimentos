# Banco de Dados

Este documento registra o modelo inicial do banco de dados.

Banco oficial previsto: MySQL.

MySQL e um banco relacional SQL. Portanto, as informacoes principais devem ser organizadas em tabelas, relacionamentos, chaves primarias e chaves estrangeiras.

## 1. Objetivo do banco

O banco deve armazenar os dados necessarios para:

- usuarios do sistema;
- investidores;
- carteiras de investimento;
- ativos financeiros;
- transacoes realizadas;
- historico necessario para calculos e consultas.

## 2. Estrutura da pasta database

```text
database/
├── migrations/
├── seeds/
├── diagrams/
└── init/
```

Responsabilidades:

- `migrations/`: alteracoes oficiais na estrutura do banco.
- `seeds/`: dados iniciais ou exemplos para desenvolvimento.
- `diagrams/`: diagramas MER, DER ou imagens do modelo.
- `init/`: scripts usados para inicializar o banco local.

## 3. Entidades iniciais

As entidades abaixo representam uma primeira versao do modelo. Elas podem ser ajustadas conforme os requisitos forem refinados.

### users

Representa usuarios que acessam o sistema (analista ou cliente).

Campos:

- `id`;
- `name`;
- `email`;
- `password_hash`;
- `role` (`analyst` ou `client`);
- `must_change_password`;
- `created_at`;
- `updated_at`.

### investors

Representa clientes pre-cadastrados pelo analista.

Campos:

- `id`;
- `user_id` (analista responsavel);
- `account_user_id` (conta de login do cliente, opcional ate o acesso ser gerado);
- `first_name`;
- `last_name`;
- `name` (nome completo derivado);
- `rg`;
- `document` (CPF);
- `email`;
- `phone`;
- `address`;
- `is_active`;
- `created_at`;
- `updated_at`.

Relacionamentos:

- um analista (`users`) pode cadastrar um ou mais investidores;
- um investidor pode ter uma conta de login de cliente (`account_user_id`).

### portfolios

Representa carteiras de investimento.

Campos iniciais:

- `id`;
- `investor_id`;
- `name`;
- `description`;
- `created_at`;
- `updated_at`.

Relacionamento:

- um investidor pode possuir uma ou mais carteiras.

### assets

Representa ativos financeiros.

Campos iniciais:

- `id`;
- `symbol`;
- `name`;
- `asset_type`;
- `created_at`;
- `updated_at`.

Exemplos de `asset_type`:

- acao;
- fundo_imobiliario;
- renda_fixa;
- etf;
- cripto;
- outro.

### transactions

Representa movimentacoes realizadas em uma carteira.

Campos iniciais:

- `id`;
- `portfolio_id`;
- `asset_id`;
- `transaction_type`;
- `quantity`;
- `unit_price`;
- `transaction_date`;
- `fees`;
- `notes`;
- `created_at`;
- `updated_at`.

Exemplos de `transaction_type`:

- compra;
- venda;
- deposito;
- retirada;
- rendimento;
- taxa.

Relacionamentos:

- uma carteira pode ter muitas transacoes;
- uma transacao pode estar associada a um ativo financeiro;
- transacoes de deposito, retirada ou taxa podem nao depender de ativo, conforme regra futura.

## 4. Relacionamentos principais

```text
users 1:N investors (como analista, via user_id)
users 1:1 investors (como cliente, via account_user_id)
investors 1:N portfolios
portfolios 1:N transactions
assets 1:N transactions
```

## 5. Regras iniciais de modelagem

- Usar chaves primarias numericas ou UUID, conforme decisao do grupo.
- Usar chaves estrangeiras para representar relacionamentos.
- Evitar dados financeiros usando `float`; preferir tipos decimais.
- Registrar datas de criacao e atualizacao quando fizer sentido.
- Documentar qualquer alteracao estrutural no banco.
- A aplicacao deve acessar o banco atraves da camada `repository.py` do backend.

## 6. Decisoes

- IDs numericos autoincrementais.
- Investidor e conta de login do cliente sao entidades ligadas (`account_user_id`), mantendo o cadastro regulatorio separado do usuario.
- Analista e dono operacional do pre-cadastro (`user_id`).
- Exclusao de investidores, carteiras e ativos e logica (`is_active = false`).
- Migration `002_roles_and_client_access.sql` adiciona perfis e campos de cliente ao schema inicial.
