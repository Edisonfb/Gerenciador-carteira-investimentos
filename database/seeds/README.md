# Seeds

Guarde aqui dados iniciais ou dados de exemplo usados em ambiente de desenvolvimento e testes.

## Analista de teste

`analista_teste.py` fornece a funcao `criar_analista_teste(engine)`, chamada automaticamente pelo comando de reset:

```powershell
python database/reset_database.py --confirmar --popular-ativos
```

O analista tambem e criado quando `--popular-ativos` e omitido. Credenciais fixas de desenvolvimento:

- E-mail: `analista@teste.local`
- Usuario: `analista`
- Senha: `12345`

O cadastro usa os servicos existentes, armazena hash da senha, cria o perfil ativo e permite entrar no frontend com o e-mail. Investidores podem ser cadastrados por esse analista pela aplicacao. O catalogo CSV de ativos continua opcional no reset.
