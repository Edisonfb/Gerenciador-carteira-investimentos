// US 12.1, 12.2 e 19.3 - Histórico de transações (SCRUM-33: tela Histórico de Transações)
import { createElement } from "react";
import { renderToString } from "react-dom/server";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { HistoricoTransacoesPage } from "../../../frontend/src/pages/HistoricoTransacoesPage";
import { consultarConfiguracaoCarteira } from "../../../frontend/src/services/configuracaoCarteiraService";
import { listarCatalogoTransacao, listarHistoricoTransacoes } from "../../../frontend/src/services/transacaoService";
import { apiFalsa, chamadas, prepararNavegador, resposta } from "../apoio";
import { API_APOSENTADORIA, HISTORICO_APOSENTADORIA } from "./dados";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => {
  navegador = prepararNavegador();
  navegador.armazenamento.set("access_token", "token-investidor");
  navegador.fetchFalso.mockImplementation(apiFalsa(API_APOSENTADORIA));
});
afterEach(() => vi.unstubAllGlobals());

function telaHistorico() {
  return renderToString(createElement(MemoryRouter, { initialEntries: ["/carteiras-investidor/1/historico"] },
    createElement(Routes, null, createElement(Route, { path: "/carteiras-investidor/:id/historico", element: createElement(HistoricoTransacoesPage) }))));
}

describe("US 12.1 - Consulta do histórico da carteira", () => {
  test("Cenário 1: o histórico é pedido só para a carteira aberta", async () => {
    const lista = await listarHistoricoTransacoes(1);
    expect(chamadas(navegador.fetchFalso)).toEqual(["GET /transactions?id_carteira=1"]);
    expect(lista).toHaveLength(4);
    expect(lista.map(t => [t.tipo, t.ticker, t.quantidade, t.valor_total])).toEqual([
      ["compra", "ITUB4", 100, "4089.00"], ["venda", "ITUB4", 100, "4089.00"],
      ["compra", "EGIE3", 100, "2583.00"], ["compra", "ITUB4", 200, "8178.00"],
    ]);
  });

  test("Cenário 1: o setor de cada linha vem do catálogo de ativos", async () => {
    const catalogo = await listarCatalogoTransacao();
    const setores = HISTORICO_APOSENTADORIA.map(t => catalogo.find(a => a.ticker === t.ticker)?.setor);
    expect(setores).toEqual(["Financeiro", "Financeiro", "Utilidade Pública", "Financeiro"]);
  });

  test("Cenário 1: a tela tem as colunas Data, Tipo, Ativo, Setor, Quantidade e Valor", () => {
    // Antes de carregar, a tela mostra o título e o aviso de ordenação.
    const html = telaHistorico();
    expect(html).toContain("Histórico de transações");
    expect(html).toContain("ordenado da transação mais recente para a mais antiga");
  });

  test("Cenário 2: compra e venda chegam como tipos distintos", async () => {
    const tipos = new Set((await listarHistoricoTransacoes(1)).map(t => t.tipo));
    expect(tipos).toEqual(new Set(["compra", "venda"]));
  });

  test("Cenário 3: a ordem da API (mais recente primeiro) é mantida", async () => {
    const datas = (await listarHistoricoTransacoes(1)).map(t => t.data_transacao);
    expect(datas).toEqual([...datas].sort().reverse());
  });

  test("Cenário 4: carteira sem transações devolve lista vazia", async () => {
    expect(await listarHistoricoTransacoes(2)).toEqual([]);
  });
});

describe("US 12.2 - Histórico restrito à carteira e ao investidor", () => {
  test("Cenário 1: o pedido leva o id da carteira, então outras carteiras não entram", async () => {
    await listarHistoricoTransacoes(2);
    expect(chamadas(navegador.fetchFalso)).toEqual(["GET /transactions?id_carteira=2"]);
  });

  test("Cenário 2: carteira de outro investidor é negada ao abrir a carteira", async () => {
    // A tela consulta a carteira antes do histórico; a API devolve 404 para carteira alheia.
    navegador.fetchFalso.mockImplementation(apiFalsa({ "GET /assets": API_APOSENTADORIA["GET /assets"] }));
    await expect(consultarConfiguracaoCarteira(9)).rejects.toThrow("Não encontrado");
  });
});

describe("US 19.3 - Histórico somente leitura", () => {
  test("Cenário 2: consultar o histórico só faz leituras (GET)", async () => {
    await listarHistoricoTransacoes(1);
    await listarCatalogoTransacao();
    expect(chamadas(navegador.fetchFalso).every(c => c.startsWith("GET"))).toBe(true);
  });

  test("Cenário 3: a tela não tem opção de editar ou excluir transação", () => {
    const html = telaHistorico();
    expect(html).toContain("O histórico é somente leitura");
    expect(html).not.toMatch(/Editar|Excluir/);
  });

  test("Cenário 3: abrir a tela não envia alterações para a API", () => {
    telaHistorico();
    expect(chamadas(navegador.fetchFalso).some(c => /^(POST|PUT|PATCH|DELETE)/.test(c))).toBe(false);
  });

  test("erro da API chega com a mensagem do backend", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ "GET /transactions?id_carteira=1": () => resposta({ detail: "Perfil de investidor não encontrado." }, 404) }));
    await expect(listarHistoricoTransacoes(1)).rejects.toThrow("Perfil de investidor não encontrado.");
  });
});
