# Revisão de arquivos sem uso — 29/10/2026

Revisão estática dos imports a partir de `frontend/src/main.tsx`, das rotas, referências em serviços, testes, configuração e scripts. Não houve remoção de arquivos, execução de migrations nem acesso ao banco. A ausência de referência identifica candidatos; não comprova que um arquivo nunca seja executado manualmente ou consumido externamente.

## 1. Candidatos à remoção sem alterar os fluxos atuais

### Telas e componentes antigos de usuários

Não são alcançados pelas rotas ou pelo ponto de entrada atual:

- `frontend/src/pages/CadastroUsuarioPage.tsx`
- `frontend/src/pages/EdicaoUsuarioPage.tsx`
- `frontend/src/pages/UsuariosPage.tsx`
- `frontend/src/components/FormularioUsuario.tsx`
- `frontend/src/components/TabelaUsuarios.tsx`

Os componentes são usados apenas pelas três páginas acima. Remover em conjunto se esse cadastro genérico de usuários não será retomado.

`frontend/src/services/usuarioService.ts` também não é usado pelo aplicativo atual, mas é importado por `tests/frontend/contaAnalista.test.ts`. Para removê-lo, revisar ou substituir esses testes pela cobertura da API real. Já existe `tests/frontend/minhaContaAnalistaApi.test.ts`, mas a equivalência de cobertura deve ser conferida antes de descartar testes.

### Imagens sem referência encontrada

- `frontend/src/assets/hero.png`
- `frontend/src/assets/react.svg`
- `frontend/src/assets/vite.svg`
- `frontend/public/favicon.svg`
- `frontend/public/icons.svg`

Não encontrei referências nos fontes, HTML, documentação ou testes examinados. São candidatos à remoção, ressalvado acesso manual por URL no caso da pasta public.

`frontend/public/meta-acoes-logo.svg` também não tem referência atual, mas é uma variante da identidade visual: manter se for usada no tema claro ou em outros materiais.

### Arquivos temporários e gerados

- `frontend/visualizacao-carteira.html`: entrada alternativa para prévia da tela de carteira; não faz parte da entrada padrão do Vite nem das rotas.
- `tests/despejo_testes.txt`: arquivo textual de saída/cópia de testes, sem participação na descoberta de testes do pytest ou Vitest.
- `tmp/pdfs/guia-*.png` e `tmp/pdfs/contacto.png`: imagens de renderização do documento.
- `.pytest_cache/`, diretórios `__pycache__/`, `frontend/dist/` e caches `.vite/`: artefatos regeneráveis. Remover quando os processos correspondentes estiverem parados. O build precisa ser refeito antes de servir `dist`.

`tmp/pdfs/gerar_guia.py` é um gerador do documento, não apenas um cache. Guardar se quiser regenerar ou atualizar o PDF; sua exclusão não afeta a aplicação, mas remove essa ferramenta.

Arquivos `.gitkeep` em pastas que agora possuem arquivos podem ser retirados. Em pastas vazias, continuam servindo para que o Git mantenha a estrutura.

## 2. Backend sem referências encontradas

- `backend/app/core/exceptions.py`: `ProjectException` não é utilizada atualmente.
- `backend/app/shared/pagination.py`: utilitários de paginação não são chamados.
- `backend/app/modules/health/repository.py`: `HealthRepository` não é usado; `/health` está implementado diretamente em `app/main.py` e não consulta esse repositório.

São candidatos à remoção, não requisitos para o funcionamento atual. Se houver plano de paginação, exceções centralizadas ou health check do banco, podem ser mantidos como estrutura futura.

## 3. Limpeza que exige ajustar referências

### Edição antiga de investidores

`frontend/src/pages/EdicaoInvestidorPage.tsx` continua na rota `/investidores/:id/editar`. Portanto, não é um arquivo órfão.

Essa página usa `buscarInvestidorPorId` e `atualizarInvestidor` de `investidorService.ts`, que operam sobre `investidoresEmMemoria`, inicialmente vazio e sem alimentação no fluxo atual. Não edita a conta real pela API.

Para retirar esse fluxo antigo, remover/redefinir a rota e avaliar em conjunto:

- `frontend/src/pages/EdicaoInvestidorPage.tsx`
- `frontend/src/components/FormularioInvestidor.tsx`
- partes de `frontend/src/services/investidorService.ts`
- `frontend/src/styles/usuarios.css`, após retirar também as páginas antigas de usuários
- tipos antigos de dados pessoais, depois de conferir os consumidores restantes

Não remover o arquivo inteiro `investidorService.ts` enquanto a rota antiga ainda o importa.

### Funções antigas de Minha Conta e cadastro

Em `frontend/src/services/investidorService.ts`, não encontrei consumidores externos atuais para:

- `buscarMeuPerfilInvestidor`
- `atualizarMeuPerfilInvestidor`
- `buscarInvestidoresPorAnalista`
- `criarInvestidor`
- `excluirInvestidor`

Minha Conta agora usa `contaInvestidorService.ts`; o convite usa `conviteInvestidorService.ts`. `converterPerfilInvestidor` e a interface antiga também podem sair caso as duas funções antigas de perfil sejam removidas. Rever os demais consumidores antes de excluir o serviço inteiro.

### Edição antiga no diálogo de carteiras

`AcaoCarteiraDialog.tsx` ainda contém o modo de editar nome, mas a listagem atualmente abre esse diálogo somente para excluir. O botão Editar navega para a página completa.

É possível simplificar o diálogo para exclusão e retirar a ramificação antiga de edição. Só depois avaliar `renomearCarteira`, que ainda é importada pelo diálogo e testada em `acoesCarteira.test.ts`.

## 4. Arquivos que devem permanecer

- `frontend/src/styles/login.css`: ainda utilizado por `AcessoSenhaPage.tsx`.
- `frontend/src/styles/shadcn.css`, `components.json`, `components/ui/*` e as dependências do shadcn/Tailwind: em uso.
- `backend/app/modules/transactions/router.py`: importado por `app/main.py`, embora ainda sem endpoints. Os outros arquivos desse módulo são estrutura futura, não implementação funcional; avaliar a continuidade do módulo antes de remover.
- `backend/app/shared/validators.py` e `backend/app/shared/dados/ativos_b3.csv`: usados pelos testes do validador. O fato de não estarem no fluxo atual de assets não torna o CSV descartável.
- `database/migrations/*`, `database/seeds/*`, `database/reset_database.py`, `backend/scripts/drop_tables.py` e `backend/app/db/maintenance.py`: manutenção manual documentada; não precisam ser importados pela API para serem necessários.
- `__init__.py`: arquivos de pacote, não lixo por estarem vazios ou pequenos.
- `.env`, `.env.example`, arquivos de configuração, `package-lock.json`, `requirements.txt`, documentação e coleção do Insomnia.
- `.venv` e `node_modules`: ambientes/dependências utilizados para executar o projeto. São reconstruíveis, mas sua remoção interrompe a execução até reinstalar.

## 5. Verificação executada

`npm --prefix frontend test`: 114 testes, 113 aprovados e 1 falha.

A falha está em `tests/frontend/contaAnalista.test.ts`, teste "busca e atualiza a conta do analista sem trocar o id". Ele espera um analista mockado de ID 1 na lista em memória do serviço antigo, mas a lista está vazia. A falha foi observada antes de qualquer remoção; nenhum arquivo foi apagado nesta revisão.

## 6. Ordem sugerida para uma limpeza posterior

1. Remover imagens padrão sem referências, entrada HTML de prévia e arquivos gerados dispensáveis.
2. Retirar as cinco páginas/componentes órfãos de usuários.
3. Revisar a cobertura antiga de analista e, então, remover `usuarioService.ts`.
4. Decidir a continuidade da rota antiga de edição de investidor; depois limpar serviço, formulário e CSS relacionados.
5. Simplificar o diálogo de carteiras e retirar suas funções antigas de edição de nome.
6. Reavaliar os três utilitários sem referências do backend e os esqueletos de funcionalidades futuras.
7. Executar build, lint e os testes correspondentes após cada grupo de alterações.
