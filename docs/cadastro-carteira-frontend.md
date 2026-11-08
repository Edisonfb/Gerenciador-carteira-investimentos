# Cadastro de carteira - frontend e aprovação pendente

Tela: frontend/src/pages/CadastroCarteiraPage.tsx.

Implementado: nome, catálogo real GET /assets com Bearer, busca parcial,
filtro por setor, validação de código (quatro letras + um número), inclusão
sem duplicidade, objetivos de 0 a 100% com até duas casas decimais, remoção,
soma exata de 100%, conferência preliminar de nomes por GET /portfolios e
cancelamento sem persistência. Quantidade inicial do rascunho: zero, não editável.
Não há POST ou alteração no backend/banco nesta entrega. Confirmar confere os
dados e informa que nada foi salvo. Não há catálogo fictício ou persistência local.

## Mudanças propostas para autorização

1. Backend: ampliar POST /portfolios para receber nome e ativos (id_ativo e
   objetivo percentual). Resolver o investidor somente pelo Bearer. Validar
   nome obrigatório, nome duplicado por investidor, ativos aceitos/ativos,
   código, duplicidade de papéis e soma 100% com Decimal. Gravar carteira e
   composição na mesma transação; quantidades novas são definidas como zero
   no servidor, nunca recebidas como quantidade livre no formulário.
2. Banco: criar relação carteira_ativo com FKs para carteira e ativo, objetivo
   decimal e quantidade inicial zero; unicidade carteira/ativo. Rever unicidade
   nome/investidor e a estratégia de normalização de nomes para evitar corrida.
   Migração preservando registros existentes; nenhuma exclusão de dados.
3. Corrigir o contrato de descricao: service/schema usam o campo, mas o modelo
   Carteira não o define. Proposta: retirar descricao do contrato para esta
   história (o formulário só usa nome), em vez de criar campo não solicitado.
4. Frontend após aprovação: enviar POST completo, retornar à lista e consultar
   GET /portfolios para exibir a carteira salva. Sem criar carteira incompleta
   e depois tentar salvar ativos em chamadas separadas.

A lista do catálogo precisa conter ativos reais. Se GET /assets retornar vazio
ou erro, a tela informa a situação. Popular catálogo, criar tabelas ou aplicar
migrations exigem autorização separada conforme solicitado pelo usuário.

## Escopo

Esta implementação trata do cadastro (US 7.1 e requisitos aplicáveis de 8.1,
8.2, 8.3 e 8.4). Edição, detalhe, exclusão, cálculos patrimoniais e histórico
(US 7.2 e 7.3) exigem fluxos próprios. Ao implementá-los, preservar histórico,
quantidades existentes e impedir acesso de outro investidor. Não usar exclusão
em cascata de transações para satisfazer a remoção de uma carteira.
