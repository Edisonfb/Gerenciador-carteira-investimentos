# Validacao das tasks e historias da Sprint 3

## Conferencia do total pago nas recomendacoes

- Implementada etapa editavel entre simular e registrar, com total pago por ativo.
- Confirmado no navegador, na carteira de demonstracao ID 2: sugestao de 300
  ABEV3 por R$ 4.929 ajustada para R$ 4.936. O historico exibiu R$ 4.936 apos
  confirmacao; as outras compras do conjunto mantiveram seus valores.
- Verificacao de persistencia cobre 300 acoes por R$ 532, cuja media nao cabe
  exatamente em duas casas: total preservado R$ 532,00, media informativa R$ 1,77.
- O historico usa o total efetivo, enquanto patrimonio/participacao usam mercado.
- Os registros adicionais foram mantidos na carteira de demonstracao.

Referencia: arquivo fornecido `Historias de Usuario - Sprint 3` (itens 11, 12, 19.3 e 13).

## Alteracoes

- SCRUM-35: recomendacoes no detalhe da carteira, aporte, modo de distribuicao, compras sugeridas, saldo e confirmacao.
- SCRUM-29: participacao atual ja calculada na API e exibida na tabela; preservada e conferida.
- SCRUM-62: implementacao anterior incompleta para a US 13.1. Agora seleciona os dois maiores deficits percentuais e divide proporcionalmente entre eles, arredondando cada parcela para lotes de 100 sem redistribuir a sobra.
- Distribuicao linear proporcional as metas de todos os ativos, conforme esclarecimento do usuario.
- US 13.2: confirmacao das compras em conjunto; qualquer falha desfaz todo o conjunto.
- Preco unitario editavel na transacao, com cotacao como sugestao.
- Quatro erros de lint corrigidos nas telas de detalhe, historico e transacao.

## Evidencia no navegador, com API e MySQL locais

Carteira criada para demonstracao: **Validacao Sprint 3**, ID 2. Os dados foram mantidos para conferencia.

| Verificacao | Resultado observado |
| --- | --- |
| Login de analista e investidor | Acesso as respectivas contas |
| Criacao de carteira com ABEV3 e ITUB4 a 50% cada | Gravacao e leitura posteriores pela API |
| Aporte vazio | Mensagem de valor maior que zero |
| Simulacao de R$ 10.000 | 300 ABEV3 por R$ 4.929 e 100 ITUB4 por R$ 4.256; sobra R$ 815 |
| Confirmacao da recomendacao | Duas compras exibidas no historico |
| Detalhe apos confirmar | Patrimonio R$ 9.185; ABEV3 300/53,66%; ITUB4 100/46,34% |
| Aporte de R$ 600 | Sem recomendacoes; mensagem de lote insuficiente; saldo integral |
| Modo linear | Consulta pela API, repartindo 50% para cada ativo e preservando a sobra |
| Quantidade 150 | Registro bloqueado pela validacao de lote |
| Compra de 100 ABEV3 a preco manual R$ 10 | Historico com valor R$ 1.000, diferente da cotacao R$ 16,43 |
| Tentativa de venda de 500 ABEV3 com 400 disponiveis | Bloqueada; mensagem com quantidade disponivel |
| Venda de 100 ABEV3 | Historico atualizado; quantidade final 300 |
| Historico | Compra e venda distintas, setor, data, quantidade e valor; sem botoes de edicao/exclusao |

As cotacoes acima sao o retrato da validacao e podem mudar em consultas futuras.

## Verificacoes isoladas complementares

Os testes novos exercitam services e repositories reais com persistencia em SQLite, sem simular respostas de negocio:

- exemplo Faculdade da US 13: aporte R$ 3.000 recomenda 200 ABEV3 e 100 CRFB3;
- aporte R$ 3.500 preserva R$ 500; aporte R$ 600 preserva todo o valor;
- apos registrar, patrimonio R$ 13.000 e participacoes 30,77%, 23,08% e 15,38% para os demais;
- erro no segundo item desfaz o primeiro, inclusive sua alteracao de quantidade;
- carteira balanceada 70/30 recebe distribuicao linear 70/30;
- testes de frontend verificam o contrato das chamadas; nao sao prova de funcionamento completo.

## Limites e ambiente

### Melhoria de orientacao sobre aporte minimo

- A tela consulta e exibe, antes da digitacao, preco por acao, custo de 100 acoes,
  minimo de aporte por ativo e minimo para gerar alguma compra no modo escolhido.
- O backend considera os pesos da distribuicao e arredonda o minimo para cima em
  centavos; o frontend apenas apresenta os valores retornados.
- Conferido no navegador com API e MySQL: minimo de R$ 4.256 no balanceamento;
  R$ 4.255,99 nao recomendou lote, R$ 4.256 recomendou 100 ITUB4.
- No modo linear 50/50, a tabela exibiu ABEV3 com lote R$ 1.643 e aporte minimo
  R$ 3.286; ITUB4 com lote R$ 4.256 e aporte minimo R$ 8.512.
- Nenhuma nova compra foi registrada nessa validacao dos minimos.

- O banco local estava sem a tabela `cotacao`; a criacao de tabelas ausentes com o script existente resolveu a falha. O historico e as transacoes tambem passaram a funcionar apos essa preparacao.
- O ambiente de execucao do agente bloqueia sockets e acesso ao Docker; o usuario iniciou a API e executou `database/migrations/create_tables.py` no terminal local. Nao houve reset dos dados.
- Testes HTTP assincronos nao concluiram neste ambiente: o traceback mostrou bloqueio em `asyncio`/`socketpair`. Permanecem disponiveis para execucao no terminal local.
- Nao foram repetidos no navegador todos os cenarios de permissao entre investidores, falha forcada de gravacao, indisponibilidade de cotacoes ou todos os filtros/ordenacoes. A revisao do codigo e os testes isolados nao equivalem a homologacao integral desses cenarios.
- Historias de outras sprints nao foram fornecidas para esta implementacao.
- Protecao das rotas administrativas e edicao de investidor pelo analista ficaram fora do escopo, conforme solicitado.
