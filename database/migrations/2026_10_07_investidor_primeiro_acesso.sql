-- Ajusta investidores para cadastro inicial somente por e-mail.
-- A senha temporaria fica apenas em usuario.senha_hash, nunca em texto puro.

ALTER TABLE investidor
  MODIFY COLUMN nome VARCHAR(30) NULL,
  MODIFY COLUMN sobrenome VARCHAR(30) NULL,
  MODIFY COLUMN cpf VARCHAR(11) NULL,
  MODIFY COLUMN telefone VARCHAR(15) NULL,
  MODIFY COLUMN cep VARCHAR(8) NULL,
  MODIFY COLUMN uf VARCHAR(2) NULL,
  MODIFY COLUMN cidade VARCHAR(32) NULL,
  MODIFY COLUMN bairro VARCHAR(30) NULL,
  MODIFY COLUMN logradouro VARCHAR(50) NULL,
  MODIFY COLUMN numero VARCHAR(5) NULL,
  DROP COLUMN token_acesso,
  ADD COLUMN email_recuperacao VARCHAR(255) NULL UNIQUE,
  ADD COLUMN primeiro_acesso_concluido BOOLEAN NOT NULL DEFAULT FALSE;
