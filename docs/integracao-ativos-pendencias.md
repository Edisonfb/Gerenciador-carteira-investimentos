# Ajustes apos integrar a implementacao de ativos

Registro solicitado em 27/10/2026. Registro original de planejamento; a secao de resultado abaixo descreve os ajustes agora implementados.

## Objetivo e sequencia

O usuario vai atualizar o projeto com o codigo do colega. Depois dessa atualizacao, revisar o estado efetivo dos arquivos e aplicar os ajustes necessarios sobre essa implementacao, preservando sua contribuicao.

Nao substituir automaticamente o trabalho do colega pela versao anterior da main. A relacao entre ativo e carteira e uma funcionalidade nova que deve ser aproveitada.

Escopo desta etapa: somente este registro em documentacao. Escopo previsto da implementacao posterior: backend, banco de dados, testes e documentacao. Verificar impacto no frontend antes de propor alteracoes nessa area.

## Contribuicoes a preservar

- Associacao `AtivoCarteira`, com um ativo podendo participar de varias carteiras e uma carteira contendo varios ativos.
- Quantidade armazenada no vinculo entre ativo e carteira.
- Relacionamentos entre os modelos de ativos, carteiras e investidores, apos revisar o comportamento de exclusao.
- Cadastro e consulta dos ativos de uma carteira, com protecao de acesso.
- Campos descritivos `nome`, `subsetor` e `segmento`.
- Catalogo de ativos do CSV, adequando sua importacao ao modelo final.

## Verificacoes obrigatorias de acesso

- Exigir autenticacao nas rotas de ativos e de ativos da carteira, usando as dependencias existentes do projeto.
- Manter a restricao ao perfil de investidor nas operacoes destinadas a esse perfil.
- Obter o investidor a partir da sessao autenticada; nao confiar em identificador de usuario enviado pelo cliente.
- Antes de listar ou cadastrar ativos de uma carteira, consultar a carteira pelo seu identificador e pelo investidor autenticado.
- Impedir consulta e alteracao de carteira de outro investidor, inclusive quando ele conhece o ID.
- Aplicar a mesma verificacao a futuras operacoes de atualizacao e remocao do vinculo.
- Seguir o comportamento atual de carteiras para recurso inexistente ou pertencente a outra pessoa, sem revelar dados do proprietario.

## Validacoes de dados e persistencia

- Verificar se o ativo e a carteira existem antes de persistir o vinculo.
- Validar quantidade como inteiro, rejeitando booleanos e valores negativos; definir e documentar se zero e permitido ou se o cadastro exige quantidade positiva.
- Corrigir `AtivoCarteiraUpdate.quantidade`, que foi declarado como `bool` no trecho revisado.
- Definir o comportamento para ativo ja presente na carteira: rejeitar duplicidade ou atualizar quantidade conforme regra explicita. Nao decidir silenciosamente entre somar e substituir.
- Validar e normalizar ticker/codigo, incluindo tamanho compativel com a coluna do banco.
- Tratar conflitos de integridade, inclusive duplicidade concorrente, sem retornar erro interno por uma situacao prevista; realizar rollback apos falha na transacao.
- Preservar as validacoes existentes de cadastro e atualizacao que continuarem aplicaveis ao modelo escolhido.

## Compatibilidade com o que ja existe

- Revisar em conjunto os cinco arquivos de `backend/app/modules/assets/`: `models.py`, `repository.py`, `service.py`, `router.py` e `schemas.py`.
- Corrigir a duplicacao do prefixo: `/assets` mais `/assets` resulta em `/assets/assets`.
- Preservar ou adaptar explicitamente a consulta do catalogo, o filtro por codigo e a consulta individual. Evitar remover comportamento existente sem avaliar consumidores e requisitos.
- Conciliar `ticker` com `codigo` e a troca de chave primaria `id_ativo` por ticker. A decisao final depende do codigo integrado e do banco existente; manter `id_ativo` e uma possibilidade, nao uma exigencia de descartar a modelagem do colega.
- Avaliar o uso dos campos `ativo` e `data_criacao` antes de remove-los.
- Compatibilizar modelos, schemas de resposta, repositorios, servicos, testes e contrato da API. Nao manter duas representacoes divergentes do mesmo ativo sem necessidade.
- Verificar a ordem das rotas estaticas e parametrizadas para evitar que caminhos de carteira sejam interpretados como identificador de ativo.

## Dependencias fora da pasta de ativos

Na branch `feature/ativos`, commit revisado `d91ed259aea3a906728368512907d7a7d317efe2`, foram identificados 11 arquivos alterados ou novos em relacao ao ancestral comum com a main:

1. `backend/app/db/__init__.py`
2. `backend/app/modules/assets/models.py`
3. `backend/app/modules/assets/repository.py`
4. `backend/app/modules/assets/router.py`
5. `backend/app/modules/assets/schemas.py`
6. `backend/app/modules/assets/service.py`
7. `backend/app/modules/investors/models.py`
8. `backend/app/modules/portfolios/models.py`
9. `backend/scripts/drop_tables.py`
10. `database/migrations/ativos.py`
11. `database/seeds/ativos.csv`

Revisar os relacionamentos dos dois lados, inclusive `back_populates`, e o registro dos modelos. Aceitar apenas parte desses arquivos pode deixar referencias a modelos ou propriedades ausentes.

Revisar `cascade="all, delete-orphan"`: a proposta remove carteiras ao excluir investidor e remove vinculos de ativos ao excluir carteira. Confirmar compatibilidade com as regras de exclusao existentes e com historico de investimentos.

## Banco e importacao do catalogo

- Inspecionar a estrutura do banco em uso antes de definir a migracao.
- Criar migracao explicita para qualquer alteracao estrutural, preservando dados e relacionamentos existentes. `create_all()` nao atualiza colunas de uma tabela ja existente.
- O arquivo `database/migrations/ativos.py` revisado importa dados por CSV; ele nao realiza a conversao entre os dois modelos de tabela.
- Corrigir a resolucao do caminho do CSV para nao depender da pasta de onde o comando e executado.
- Resolver a dependencia de `pandas`, ausente dos requisitos revisados, usando as dependencias existentes ou justificando sua adicao.
- Garantir que a importacao respeite campos obrigatorios, valores padrao e duplicidades; definir comportamento seguro para reexecucao.
- Avaliar `backend/scripts/drop_tables.py` separadamente. Ele apaga tabelas quando executado e nao deve ser usado como substituto de migracao para um banco com dados a preservar.

## Testes necessarios apos a integracao

- Consultas do catalogo, filtro e consulta individual continuam funcionando conforme o contrato final.
- Requisicoes sem login sao recusadas e perfis sem permissao nao acessam as operacoes.
- Investidor consegue cadastrar e consultar ativos da propria carteira.
- Investidor nao consegue cadastrar, consultar, atualizar ou remover ativos de carteira alheia.
- Ativo ou carteira inexistente, quantidade invalida e vinculo duplicado possuem respostas previstas.
- Relacionamentos sao carregados sem falhas e exclusoes seguem a politica definida.
- Migracao e importacao sao verificadas em banco de teste, incluindo preservacao de registros e reexecucao da importacao.

Na revisao anterior a integracao, passaram 20 testes unitarios de servico de ativos e 13 testes de integracao de ativos da versao local baseada em main. Esses resultados nao validam a futura versao integrada. As rotas duplicadas e a aceitacao de quantidade negativa da branch do colega tambem foram confirmadas em memoria, sem executar seus scripts no MySQL.

## Criterio de conclusao

A implementacao do colega continua identificavel na funcionalidade de ativos da carteira e no catalogo, com autenticacao, verificacao de propriedade, validacao de dados, contratos coerentes, migracao adequada e testes dos fluxos afetados. Atualizar `docs/api-contract.md` e `docs/database.md` conforme as decisoes efetivamente implementadas.

## Resultado da implementacao

- Integrada a main local na backend, preservando o trabalho do colega em AtivoCarteira, relacionamentos e CSV.
- Recuperada a consulta por setor da backup afee521 (repository, service, router e documentacao); era a unica funcionalidade adicional desse commit.
- Login e perfil de investidor obrigatorios em todas as rotas de ativos.
- Proprietario identificado pela sessao; carteira alheia e inexistente retornam 404 antes da leitura ou gravacao do vinculo.
- Existencia e status do ativo/carteira verificados no cadastro; quantidade inteira positiva; duplicidade retorna 409 e nao altera a quantidade existente.
- Tratamento de falha de persistencia com rollback, inclusive conflito concorrente.
- Prefixos corrigidos e rotas estaticas declaradas antes da consulta individual.
- Ticker mantido como identidade publica da implementacao do colega. Consulta individual adaptada para ticker, com filtro codigo preservado como alias. Tamanho de 10 caracteres preserva a capacidade anterior do codigo.
- Status e data de criacao preservados no catalogo; dados descritivos legados podem ficar vazios. Ticker nao pode ser alterado pela atualizacao descritiva, evitando romper vinculos.
- Registro explicito de modelos evita import circular ao carregar modelos e scripts diretamente.
- Migracao e importacao sem pandas preparadas e testadas em SQLite. Catalogo existente nao e apagado nem sobrescrito pela importacao.
- Cascatas existentes revisadas e preservadas: excluir carteira remove vinculos, mantendo ativos globais; excluir investidor remove suas carteiras e vinculos. Rever antes de implementar historico financeiro.
- Atualizacao/remocao do vinculo foram implementadas em pedido posterior: PATCH substitui a quantidade, zero remove o vinculo e DELETE permite remocao direta. Ambas verificam o proprietario e preservam o catalogo.
- Contratos e orientacoes atualizados em api-contract.md e database.md.

Os comandos de preparacao do banco estao em database.md. A verificacao de leitura do MySQL local encontrou as tabelas de ativos/carteira ausentes. Os scripts nao foram executados nesse banco. A validacao em MySQL isolado depende de permissao para criar um banco de teste, indisponivel ao usuario configurado.

### Validacao final e problemas fora do escopo

Foram aprovados 60 testes afetados: 59 da selecao de servico de ativos, API de ativos/carteiras, migracao e importacao, mais o teste adicional da cascata de exclusao de investidor. A importacao direta do modelo de ativos e a inicializacao de app.main foram verificadas em processos novos, sem conectar ao banco do projeto.

A execucao ampliada de tests/backend resultou em 162 testes aprovados, 30 falhas e 1 falha esperada, antes dos dois ultimos testes adicionados. As mesmas 30 falhas foram reproduzidas numa copia temporaria da main original (e4e1444), sem os ajustes desta implementacao. Nao sao regressoes desta integracao.

Areas responsaveis e arquivos a revisar separadamente:

- Autenticacao e primeiro acesso: tests/backend/integration/api/test_auth_investidor_api.py e tests/backend/unit/services/test_investidor_service.py possuem expectativas antigas de mensagens/campos e ausencia de nome_usuario nas entradas de testes. A incompatibilidade de envio em password_service.py foi corrigida em pedido posterior, usando enviar_link_senha(email, link), com destino de recuperacao para investidores e email principal para analistas. O convite inicial continua usando enviar_token_acesso(email, token).
- Cadastro de investidor: tests/backend/unit/services/test_cadastro_investidor.py envia campos de um contrato anterior, que o schema atual recusa.
- Carteiras: tests/backend/unit/services/test_carteira_service.py ainda envia descricao, ausente do contrato atual; tests/backend/integration/api/test_carteiras_api.py possui tres XPASS(strict), porque comportamentos ja funcionam mas continuam marcados como falhas esperadas.

Esses problemas foram apenas registrados, pois o pedido autorizou a integracao de ativos e a recuperacao das correcoes da backup; a backup nao contem correcoes adicionais de autenticacao ou cadastro.
