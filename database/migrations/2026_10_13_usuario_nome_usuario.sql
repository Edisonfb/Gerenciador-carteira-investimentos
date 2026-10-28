-- Adiciona nome de usuario unico para login alternativo ao e-mail.
-- O campo pode ficar nulo ate o usuario escolher um nome de usuario.

ALTER TABLE usuario
  ADD COLUMN nome_usuario VARCHAR(50) NULL AFTER email;

CREATE UNIQUE INDEX uq_usuario_nome_usuario
  ON usuario (nome_usuario);
