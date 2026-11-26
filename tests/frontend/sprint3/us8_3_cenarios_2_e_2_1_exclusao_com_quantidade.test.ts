// US 8.3 - Cenários 2 e 2.1 (testados na Sprint 3): ativo/carteira com quantidade não são excluídos.
import { createElement } from "react";
import { renderToString } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { AcaoCarteiraDialog } from "../../../frontend/src/components/AcaoCarteiraDialog";
import { AvisoDialog } from "../../../frontend/src/components/AvisoDialog";
import {
  carteiraPossuiAtivoComQuantidade, consultarConfiguracaoCarteira, editarComposicaoCarteira, excluirCarteira,
  MENSAGEM_ATIVO_COM_QUANTIDADE, MENSAGEM_CARTEIRA_COM_QUANTIDADE,
} from "../../../frontend/src/services/configuracaoCarteiraService";
import { apiFalsa, chamadas, prepararNavegador, resposta } from "../apoio";
import { API_CARTEIRA_1 } from "../sprint2/catalogo";

const TEXTO_ATIVO = "Você possui quantidade desse ativo, faça um registro de venda para removê-lo da carteira.";
const TEXTO_CARTEIRA = "Você possui ativo(s) nessa carteira que possuem quantidade, faça registro de venda do(s) ativo(s).";

// Aposentadoria com CRFB3 = 200 ações (patrimônio de R$ 3.000,00).
const VINCULOS_COM_QUANTIDADE = [
  { ticker: "ABEV3", id_carteira: 1, quantidade: 0, objetivo_percentual: "10.00" },
  { ticker: "CRFB3", id_carteira: 1, quantidade: 200, objetivo_percentual: "90.00" },
];
const VINCULOS_ZERADOS = VINCULOS_COM_QUANTIDADE.map(v => ({ ...v, quantidade: 0 }));

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => {
  navegador = prepararNavegador();
  navegador.armazenamento.set("access_token", "token-investidor");
});
afterEach(() => vi.unstubAllGlobals());

test("as mensagens são as da história", () => {
  expect(MENSAGEM_ATIVO_COM_QUANTIDADE).toBe(TEXTO_ATIVO);
  expect(MENSAGEM_CARTEIRA_COM_QUANTIDADE).toBe(TEXTO_CARTEIRA);
});

describe("Cenário 2 - Remoção de ativo que já possui quantidade", () => {
  test("o aviso mostra a mensagem e só o botão Confirmar", () => {
    const html = renderToString(createElement(AvisoDialog, { titulo: "Remover ativo", mensagem: MENSAGEM_ATIVO_COM_QUANTIDADE, onFechar: () => {} }));
    expect(html).toContain("Você possui quantidade desse ativo, faça um registro de venda para removê-lo da carteira.");
    expect(html).toContain("Confirmar");
    expect(html).not.toContain("Cancelar");
  });

  test("a quantidade de cada ativo vem da API para a tela bloquear a remoção", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ ...API_CARTEIRA_1, "GET /assets/carteira/1": VINCULOS_COM_QUANTIDADE }));
    const configuracao = await consultarConfiguracaoCarteira(1);
    expect(configuracao.ativos.find(a => a.ticker === "CRFB3")?.quantidade).toBe(200);
    expect(configuracao.ativos.find(a => a.ticker === "ABEV3")?.quantidade).toBe(0);
  });

  test("se a API recusar a remoção, a mensagem chega na tela de edição", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ ...API_CARTEIRA_1, "GET /assets/carteira/1": VINCULOS_COM_QUANTIDADE }));
    const original = await consultarConfiguracaoCarteira(1);
    navegador.fetchFalso.mockImplementation(apiFalsa({
      ...API_CARTEIRA_1, "GET /assets/carteira/1": VINCULOS_COM_QUANTIDADE,
      "PATCH /assets/carteira/1/ABEV3": {},
      "DELETE /assets/carteira/1/CRFB3": () => resposta({ detail: TEXTO_ATIVO }, 400),
    }));
    const semCrfb3 = original.ativos.filter(a => a.ticker !== "CRFB3").map(a => ({ ...a, objetivo: "100" }));
    await expect(editarComposicaoCarteira(original, "Aposentadoria", semCrfb3)).rejects.toThrow(TEXTO_ATIVO);
  });
});

describe("Cenário 2.1 - Exclusão da carteira com ativos que têm quantidade", () => {
  test("carteira com ativo com quantidade é identificada sem tentar excluir", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ "GET /assets/carteira/1": VINCULOS_COM_QUANTIDADE }));
    await expect(carteiraPossuiAtivoComQuantidade(1)).resolves.toBe(true);
    expect(chamadas(navegador.fetchFalso)).toEqual(["GET /assets/carteira/1"]);
  });

  test("carteira com todos os ativos zerados pode ser excluída", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ "GET /assets/carteira/1": VINCULOS_ZERADOS }));
    await expect(carteiraPossuiAtivoComQuantidade(1)).resolves.toBe(false);
  });

  test("carteira sem ativos pode ser excluída", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ "GET /assets/carteira/1": [] }));
    await expect(carteiraPossuiAtivoComQuantidade(1)).resolves.toBe(false);
  });

  test("id inválido não chama a API", async () => {
    await expect(carteiraPossuiAtivoComQuantidade(0)).rejects.toThrow("Carteira inválida.");
    expect(navegador.fetchFalso).not.toHaveBeenCalled();
  });

  test("se a API recusar a exclusão, a mensagem da história é devolvida", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ "DELETE /portfolios/1": () => resposta({ detail: TEXTO_CARTEIRA }, 400) }));
    await expect(excluirCarteira(1)).rejects.toThrow(TEXTO_CARTEIRA);
  });

  test("a janela de exclusão abre com o botão Excluir travado até conferir as quantidades", () => {
    const carteira = { id_carteira: 1, nome: "Aposentadoria", ativa: true };
    const html = renderToString(createElement(AcaoCarteiraDialog, { carteira, acao: "excluir", onFechar: () => {}, onConcluido: () => {} }));
    expect(html).toMatch(/<button[^>]*disabled=""[^>]*>Excluir carteira<\/button>/);
  });
});
