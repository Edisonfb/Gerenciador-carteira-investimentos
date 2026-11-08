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

## 7. Integracao implementada de ativos e carteiras

O modelo implementado usa `ativo.ticker` (ate 10 caracteres) como identidade do catalogo. Preserva os campos descritivos `nome`, `setor`, `subsetor`, `segmento` do colega e acrescenta `ativo` e `data_criacao`. Nome, subsetor e segmento podem ser vazios para acomodar registros legados sem essas informacoes. O alias Python `codigo` aponta para o mesmo ticker, sem criar outra coluna.

`ativo_carteira` mantem a chave composta `(ticker, id_carteira)`, as chaves estrangeiras para ativo e carteira e quantidade inteira positiva. O banco novo inclui o CHECK `ck_ativo_carteira_quantidade_positiva`. A API limita a quantidade ao inteiro assinado de 32 bits e rejeita vinculos duplicados.

A atualizacao de quantidade aceita zero como pedido de exclusao do vinculo; nao grava zero na tabela. A remocao direta tambem apaga somente a linha de `ativo_carteira`, preservando o catalogo e as demais carteiras. Essas operacoes verificam o investidor proprietario e nao exigem alteracao da estrutura do banco.

A implementacao preserva a exclusao fisica em cascata introduzida na branch de ativos: excluir investidor remove suas carteiras; excluir carteira remove seus vinculos. Esses vinculos nao apagam o catalogo global. Transacoes e historico financeiro ainda nao estao implementados; antes de vincula-los, rever essa politica de exclusao.

### Preparacao e migracao

Execute a partir da raiz do repositorio, com o ambiente Python ativo:

```powershell
python database/migrations/create_tables.py
python database/migrations/integrar_ativos.py
python database/migrations/ativos.py
```

O primeiro comando cria apenas tabelas ausentes. O segundo atualiza uma tabela de ativos preexistente; `create_all()` sozinho nao altera suas colunas. O terceiro importa o CSV do colega. Nenhum desses passos exige executar `backend/scripts/drop_tables.py`.

A migracao aceita tanto a estrutura anterior `id_ativo/codigo/setor/ativo/data_criacao` quanto a estrutura `ticker/nome/setor/subsetor/segmento`. Renomeia `codigo` para `ticker` quando necessario, preserva o ID numerico legado e sua chave primaria fisica, acrescenta campos faltantes e cria uma referencia unica para ticker. O ORM usa ticker como identidade; o ID legado permanece armazenado, mas nao e o identificador publico da API. Status e datas existentes sao mantidos; registros sem data recebem o instante da migracao.

No MySQL, a migracao amplia ticker e setor para os tamanhos do modelo, ajustando a FK do vinculo quando presente. DDL do MySQL pode confirmar alteracoes mesmo quando uma etapa posterior falha: mantenha backup do banco antes de aplicar em um ambiente com dados importantes. A migracao recusa tickers invalidos/duplicados, quantidades nao positivas e referencias externas a tabela de vinculos; esses casos exigem tratamento especifico, sem exclusao automatica de registros.

A importacao usa `csv` da biblioteca padrao e SQLAlchemy, sem pandas. Resolve o caminho pelo proprio arquivo, valida o catalogo completo antes de gravar e insere somente tickers ausentes numa transacao. Reexecutar nao duplica nem sobrescreve nome, setor ou status de ativos existentes. Uma falha de persistencia desfaz o lote.

### Verificacao desta integracao

Os testes SQLite verificam as duas estruturas anteriores, preservacao de IDs/status/datas/vinculos, reexecucao da migracao, importacao completa do CSV e reexecucao sem duplicidade. A consulta somente de leitura ao MySQL configurado nao encontrou as tabelas `ativo`, `ativo_carteira` e `carteira`. A tentativa de validar em um banco MySQL separado foi impedida por falta de permissao CREATE DATABASE do usuario configurado; nenhum banco temporario foi criado e os scripts nao foram aplicados ao banco do projeto.

## 8. Gerenciamento e reset da estrutura

A classe `GerenciadorBanco`, em `backend/app/db/maintenance.py`, centraliza as operacoes de estrutura:

- `criar_tabelas()`: registra os modelos e cria somente tabelas ausentes; mantem os registros existentes.
- `apagar_tabelas(confirmar=True)`: reflete a estrutura real do banco e remove suas tabelas na ordem de dependencias.
- `resetar(confirmar=True)`: remove as tabelas existentes e as recria a partir de `Base.metadata`, usando os modelos atuais.

O reset inclui tabelas e colunas legadas, mesmo quando nao existem mais nos modelos. Ele apaga todos os registros das tabelas do banco configurado, incluindo usuarios, analistas, investidores, carteiras e posicoes. O banco MySQL propriamente dito e suas permissoes permanecem; a operacao nao precisa de CREATE DATABASE, mas exige permissoes de leitura de estrutura, DROP e CREATE de tabelas. Views e outros objetos que nao sejam tabelas nao sao administrados por essa rotina.

Depois de alterar os modelos e decidir descartar os dados locais, execute na raiz do projeto com o ambiente Python ativo:

```powershell
python database/reset_database.py --confirmar --popular-ativos
```

Sem `--popular-ativos`, o comando recria as tabelas e cria apenas o analista padrao de teste e sua linha de usuario. Com essa opcao, o catalogo CSV e validado antes da exclusao e importado depois da recriacao. Nao e necessario executar as migrations de ativos apos um reset, pois as tabelas ja seguem os modelos atuais.

O comando imprime o nome do banco de destino e exige `--confirmar`. Nao e chamado no startup da API. Antes de usar, pare a aplicacao para que nao haja requisicoes usando as tabelas durante a recriacao. Para manter dados, use migrations em vez de reset. No MySQL, exclusao e criacao de tabelas podem ser confirmadas separadamente; uma falha intermediaria pode deixar a estrutura incompleta, sem recuperacao automatica dos dados apagados.

Criar tabelas e popular dados sao operacoes distintas. O cadastro de analista (`POST /analysts`) grava tambem sua linha de `usuario`; o cadastro de investidor (`POST /investors`, por analista autenticado) grava o investidor e sua linha de `usuario`. O comando de reset chama `criar_analista_teste()` de `database/seeds/analista_teste.py` depois de recriar as tabelas, antes da importacao opcional de ativos. A classe de manutencao permanece responsavel somente pela estrutura.

A conta fixa de desenvolvimento tem nome `Analista de Teste`, e-mail `analista@teste.local`, usuario `analista` e senha `12345`, conforme solicitado. E criada ativa pelo mesmo `AnalistaService`/`AnalistaRepository` usado no cadastro normal, com hash da senha e registros relacionados em `usuario` e `analista`. Nenhum e-mail e enviado e nenhum investidor e criado automaticamente. O seed reconhece a propria conta se for chamado novamente, sem duplica-la nem sobrescrever outra identidade; cada novo reset recria a conta com as credenciais originais.

O banco local e iniciado por `docker compose up -d mysql`; o nome e definido em `MYSQL_DATABASE` no Compose e no script de `database/init/`. Quando o banco ja existe, basta executar a criacao de tabelas, as migrations apropriadas ou o reset. Os comandos existentes `create_tables.py` e `drop_tables.py` agora delegam a classe de manutencao; a exclusao isolada tambem exige `--confirmar`.

Os testes de manutencao usam bancos SQLite temporarios com chaves estrangeiras habilitadas. Verificam dados relacionados de usuario/analista/investidor/carteira/ativo, remocao de estrutura legada, correspondencia das colunas com os modelos, recriacao repetida, bloqueio sem confirmacao, importacao opcional do catalogo e criacao do analista padrao. A conta gerada tambem foi validada pelos endpoints reais de login e perfil, usando e-mail e usuario. Nenhum reset foi executado no MySQL configurado durante esta implementacao.
