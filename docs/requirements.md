# Requisitos do Projeto

Este documento registra os requisitos iniciais do Gerenciador de Carteiras de Investimento.

Os requisitos podem mudar durante o desenvolvimento, mas qualquer mudanca importante deve ser registrada aqui.

## 1. Objetivo do sistema

Criar uma aplicacao para gerenciar carteiras de investimento, permitindo cadastrar investidores, carteiras, ativos financeiros e transacoes.

O sistema deve permitir consultar informacoes consolidadas da carteira, como historico de movimentacoes e resumo dos investimentos.

## 2. Perfis envolvidos

Perfis do grupo:

- PO: organiza prioridades, requisitos e regras do produto.
- Desenvolvedores: implementam frontend, backend, banco, testes e documentacao.

Perfis do sistema:

- usuario: pessoa que acessa a aplicacao;
- investidor: pessoa ou entidade que possui carteiras de investimento.

## 3. Requisitos funcionais iniciais

### RF01 - Autenticacao de usuarios

O sistema deve permitir cadastro, login e identificacao do usuario autenticado.

### RF02 - Gerenciamento de investidores

O sistema deve permitir cadastrar, listar, consultar, atualizar e remover ou desativar investidores.

### RF03 - Gerenciamento de carteiras

O sistema deve permitir criar, listar, consultar, atualizar e remover ou desativar carteiras de investimento.

### RF04 - Gerenciamento de ativos

O sistema deve permitir cadastrar, listar, consultar, atualizar e remover ou desativar ativos financeiros.

### RF05 - Registro de transacoes

O sistema deve permitir registrar transacoes como compra, venda, deposito, retirada, rendimento e taxa.

### RF06 - Historico de transacoes

O sistema deve permitir consultar o historico de transacoes de uma carteira.

### RF07 - Resumo da carteira

O sistema deve permitir consultar um resumo da carteira, incluindo dados consolidados de investimentos.

### RF08 - Validacoes de negocio

O sistema deve validar regras importantes, como:

- nao permitir valores financeiros negativos quando nao fizer sentido;
- nao permitir venda maior do que a quantidade disponivel, caso essa regra seja implementada;
- exigir campos obrigatorios para cadastros e transacoes.

## 4. Requisitos nao funcionais

### RNF01 - Organizacao do codigo

O codigo deve ser separado por responsabilidades, respeitando a arquitetura definida em `docs/architecture.md`.

### RNF02 - Padrao de API

O backend deve expor endpoints previsiveis e documentados em `docs/api-contract.md`.

### RNF03 - Banco relacional

O banco deve ser MySQL e seguir o modelo documentado em `docs/database.md`.

### RNF04 - Testabilidade

Regras de negocio relevantes devem ser testaveis de forma isolada.

### RNF05 - Documentacao objetiva

As decisoes importantes do projeto devem ser documentadas de forma curta e clara.

### RNF06 - Seguranca

Senhas, tokens e dados sensiveis nao devem ser salvos diretamente no codigo.

### RNF07 - Trabalho em equipe

Cada integrante deve evitar alterar arquivos fora da sua area sem alinhamento previo.

## 5. Prioridade inicial sugerida

Ordem recomendada para iniciar o desenvolvimento:

1. Definir modelo inicial do banco.
2. Criar configuracao real do backend com FastAPI e MySQL.
3. Implementar autenticacao basica.
4. Implementar investidores.
5. Implementar carteiras.
6. Implementar ativos.
7. Implementar transacoes.
8. Implementar resumo da carteira.
9. Criar telas principais no frontend.
10. Criar testes unitarios, integracao e e2e.

## 6. Fora do escopo inicial

Itens que podem ficar para uma versao futura:

- integracao automatica com bolsa de valores;
- importacao automatica de notas de corretagem;
- cotacoes em tempo real;
- recomendacoes automaticas de investimento;
- calculos avancados de imposto.
