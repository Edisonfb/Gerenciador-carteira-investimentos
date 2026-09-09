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

Representa usuarios que acessam o sistema.

Campos iniciais:

- `id`;
- `name`;
- `email`;
- `password_hash`;
- `created_at`;
- `updated_at`.

### investors

Representa investidores gerenciados pela aplicacao.

Campos iniciais:

- `id`;
- `user_id`;
- `name`;
- `document`;
- `email`;
- `created_at`;
- `updated_at`.

Relacionamento:

- um usuario pode cadastrar um ou mais investidores.

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
users 1:N investors
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

## 6. Decisoes pendentes

- Definir se os IDs serao inteiros ou UUID.
- Definir se investidores e usuarios serao sempre entidades separadas.
- Definir como sera calculada a posicao atual da carteira.
- Definir se cotacoes atuais serao cadastradas manualmente ou integradas futuramente.
- Definir politica para exclusao fisica ou desativacao logica de registros.
