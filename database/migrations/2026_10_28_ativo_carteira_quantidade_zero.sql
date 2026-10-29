ALTER TABLE ativo_carteira
    DROP CHECK ck_ativo_carteira_quantidade_positiva,
    ADD CONSTRAINT ck_ativo_carteira_quantidade_nao_negativa
        CHECK (quantidade >= 0);
