# Banco de dados

Materiais relacionados ao banco de dados MySQL.

## Pastas

- `migrations/`: alteracoes oficiais na estrutura do banco.
- `seeds/`: dados iniciais ou de exemplo.
- `diagrams/`: diagramas MER, DER ou materiais visuais.
- `init/`: scripts executados na inicializacao do banco local.

## Criar, popular ou resetar

Na raiz do repositorio, com o ambiente Python ativo:

```powershell
# Cria tabelas ausentes sem apagar registros.
python database/migrations/create_tables.py

# Importa o catalogo de ativos, sem duplicar registros existentes.
python database/migrations/ativos.py

# Apaga as tabelas e dados, recria os modelos e cria o analista de teste.
python database/reset_database.py --confirmar

# Faz o reset com analista de teste e importa o catalogo de ativos.
python database/reset_database.py --confirmar --popular-ativos
```

O reset recria a estrutura de usuarios, analistas, investidores, carteiras e ativos e cria automaticamente um analista de teste. Todas as tabelas existentes no banco configurado sao removidas, inclusive tabelas antigas que nao aparecem mais nos modelos. Use somente no banco dedicado ao projeto e preserve um backup se precisar dos dados atuais.

Depois de qualquer reset pelo comando, entre no frontend com:

- E-mail: `analista@teste.local`
- Usuario: `analista`
- Senha: `12345`

A tela atual de login pede e-mail; a API tambem aceita o nome de usuario. A conta e ativa e tem perfil de analista, pronta para cadastrar investidores pela interface. As credenciais voltam a esses valores em cada reset, com ou sem `--popular-ativos`. A senha e armazenada como hash pelo fluxo normal de cadastro. O seed fica em `database/seeds/analista_teste.py` e nao envia e-mails nem cria investidores automaticamente.

A rotina fica na classe `GerenciadorBanco`, em `backend/app/db/maintenance.py`. O comando nao recria o servidor nem executa DROP DATABASE; ele trabalha dentro do banco ja existente, usando a conexao do `.env`. A aplicacao nao executa reset durante sua inicializacao.

Para iniciar o MySQL local definido no projeto:

```powershell
docker compose up -d mysql
```

O Compose configura a criacao de `investment_portfolio_manager`, complementada pelo script `init/01_create_database.sql` na inicializacao do volume. Depois execute o comando de criacao ou de reset das tabelas. Mudar os modelos nao atualiza tabelas existentes automaticamente: use migrations para preservar registros ou o reset para comecar com os dados vazios.

O comando legado de exclusao isolada agora exige confirmacao:

```powershell
python backend/scripts/drop_tables.py --confirmar
```
