# Atualizacao de bancos existentes

Use `atualizar_estrutura_atual.py` para os campos atuais de conta e composicao de carteira. O script exige MySQL 8.0.16 ou superior. Nao apaga tabelas, contas, carteiras ou vinculos.

Execute na raiz do repositorio, com o `.env` apontando para o banco correto. Faca backup antes de aplicar: no MySQL, ALTER TABLE faz commit implicito e nao existe rollback automatico de toda a migracao. Execute sem alteracoes simultaneas pela aplicacao e confira as pendencias antes de liberar o acesso.

## Verificar sem alterar o banco

```powershell
.\backend\.venv\Scripts\python.exe database/migrations/atualizar_estrutura_atual.py
```

## Aplicar

```powershell
.\backend\.venv\Scripts\python.exe database/migrations/atualizar_estrutura_atual.py --aplicar
```

O script verifica o estado atual antes de gerar comandos. Pode ser executado novamente: nao tenta criar colunas, indices e restricoes que ja correspondem ao esperado.

Atualiza:

- `usuario.nome_usuario`: VARCHAR(50), opcional e unico.
- `investidor.email_recuperacao`: VARCHAR(255), opcional e unico.
- `investidor.primeiro_acesso_concluido`: obrigatorio.
- Campos pessoais existentes do investidor: passam a aceitar NULL, permitindo convite somente por e-mail.
- `token_acesso` legado, se existir: torna-se opcional, preservando os valores antigos. Tokens novos sao validados pelo hash; esta migracao nao emite nem envia convites.
- `ativo_carteira.quantidade`: INT NOT NULL, com CHECK quantidade >= 0.
- `ativo_carteira.objetivo_percentual`: DECIMAL(5,2) NOT NULL quando todos os percentuais reais estiverem definidos.

A migracao nao valida a soma de 100% no banco. Essa regra permanece no frontend.

## Vinculos antigos sem percentual

Se a coluna nao existe e ha ativos vinculados, a primeira aplicacao cria a coluna temporariamente aceitando NULL e informa a pendencia. NAO preenche com 0, 100 ou distribuicao automatica.

Defina os objetivos reais de cada carteira, identificando cada linha pela chave composta. Exemplo ilustrativo: substitua o ID, ticker e percentual pelos valores reais antes de executar:

```sql
UPDATE ativo_carteira
SET objetivo_percentual = 20.00
WHERE id_carteira = 123 AND ticker = 'ITUB4';
```

Para consultar as pendencias:

```sql
SELECT id_carteira, ticker, quantidade, objetivo_percentual
FROM ativo_carteira
WHERE objetivo_percentual IS NULL;
```

Depois de preencher todos os valores, execute novamente com `--aplicar`. O script valida a faixa maior que zero ate 100 e no maximo duas casas decimais e aplica NOT NULL. A etapa temporaria nao representa migracao concluida: a API atual exige percentuais preenchidos para consultar a composicao.

## Contas sem controle de primeiro acesso

Se ha investidores e a coluna `primeiro_acesso_concluido` nao existe, o script interrompe antes de alterar qualquer tabela, para nao adivinhar o estado das contas.

Se TODOS os investidores antigos ja concluiram o cadastro:

```powershell
.\backend\.venv\Scripts\python.exe database/migrations/atualizar_estrutura_atual.py --aplicar --primeiro-acesso-legado concluido
```

Se TODOS ainda estao pendentes:

```powershell
.\backend\.venv\Scripts\python.exe database/migrations/atualizar_estrutura_atual.py --aplicar --primeiro-acesso-legado pendente
```

Se houver os dois casos, defina a coluna e os estados individualmente antes de aplicar. A escolha afeta a possibilidade de login: contas pendentes exigem o fluxo de convite; contas concluidas precisam de nome de usuario e senha validos. A migracao nao inventa nomes de usuario, e-mails de recuperacao ou senhas para contas antigas.

## Limites e ordem de execucao

- Banco novo: use `create_tables.py` e `ativos.py`, conforme o README principal do banco.
- Banco existente com as tabelas atuais: use esta migracao.
- Se faltam tabelas, execute primeiro `create_tables.py`.
- Se `ativo_carteira` ainda nao tem `ticker`, revise a migracao anterior `integrar_ativos.py` antes desta. Nao execute migracoes antigas indiscriminadamente sobre a estrutura atual.
- Nao e necessario executar os SQL antigos de `nome_usuario` e `quantidade_zero` depois desta migracao; eles nao sao idempotentes.
- Valores duplicados, quantidades invalidas e percentuais invalidos interrompem o planejamento antes de executar DDL. Corrija os registros indicados e repita.
- Codigo de saida 0: verificacao/aplicacao sem pendencias; 2: percentuais reais pendentes; 1: pre-condicao invalida.
- Verifique sempre a ultima mensagem: se houver falha de infraestrutura durante um ALTER, comandos anteriores podem ja ter sido aplicados pelo MySQL. Depois de corrigir a causa, execute a verificacao novamente.
