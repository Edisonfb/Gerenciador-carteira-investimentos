-- Campos temporários do token de primeiro acesso.
-- Ficam preenchidos até o investidor validar a conta e definir a senha.
-- Use este script só se a tabela investidor já existir sem estas colunas.
-- Em banco novo, o modelo do SQLAlchemy já cria as colunas.

ALTER TABLE investidor
    ADD COLUMN token_expira_em DATETIME NULL,
    ADD COLUMN token_utilizado TINYINT(1) NOT NULL DEFAULT 0;
