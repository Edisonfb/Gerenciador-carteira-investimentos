# Migrations

Guarde aqui scripts ou arquivos de migracao que alteram oficialmente a estrutura do banco.

Ordem atual:

1. `001_create_initial_tables.sql` — schema inicial
2. `002_roles_and_client_access.sql` — perfis (`role`), troca obrigatoria de senha e campos de cliente/acesso

Para ambiente Docker novo, o espelho completo fica em `database/init/02_create_initial_tables.sql`.
