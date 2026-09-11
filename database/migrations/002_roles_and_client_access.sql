-- Migration 002: perfis de usuario e acesso do cliente (pre-cadastro).
-- Aplicar apos 001_create_initial_tables.sql

USE investment_portfolio_manager;

ALTER TABLE users
    ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'analyst' AFTER password_hash,
    ADD COLUMN must_change_password TINYINT(1) NOT NULL DEFAULT 0 AFTER role;

ALTER TABLE investors
    ADD COLUMN account_user_id INT UNSIGNED NULL AFTER user_id,
    ADD COLUMN first_name VARCHAR(80) NOT NULL DEFAULT '' AFTER account_user_id,
    ADD COLUMN last_name VARCHAR(80) NOT NULL DEFAULT '' AFTER first_name,
    ADD COLUMN rg VARCHAR(32) NOT NULL DEFAULT '' AFTER last_name,
    ADD COLUMN phone VARCHAR(32) NOT NULL DEFAULT '' AFTER email,
    ADD COLUMN address VARCHAR(255) NOT NULL DEFAULT '' AFTER phone;

-- Preenche nome/sobrenome a partir do campo name legado.
UPDATE investors
SET
    first_name = CASE
        WHEN TRIM(name) = '' THEN 'Cliente'
        WHEN LOCATE(' ', TRIM(name)) > 0 THEN SUBSTRING_INDEX(TRIM(name), ' ', 1)
        ELSE TRIM(name)
    END,
    last_name = CASE
        WHEN LOCATE(' ', TRIM(name)) > 0 THEN TRIM(SUBSTRING(TRIM(name), LOCATE(' ', TRIM(name)) + 1))
        ELSE '-'
    END
WHERE first_name = '' OR last_name = '';

ALTER TABLE investors
    ADD UNIQUE KEY uq_investors_account_user_id (account_user_id),
    ADD CONSTRAINT fk_investors_account_user
        FOREIGN KEY (account_user_id) REFERENCES users (id)
        ON DELETE SET NULL ON UPDATE CASCADE;
