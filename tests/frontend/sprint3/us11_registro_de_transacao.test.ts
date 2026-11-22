// US 11.1 a 11.4 - Registro de transação (SCRUM-31: tela Transação)
import { createElement } from "react";
import { renderToString } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { TransacaoPage } from "../../../frontend/src/pages/TransacaoPage";
import {
  consultarCotacaoTransacao, listarAtivosDaCarteira, listarCarteirasParaTransacao, listarCatalogoTransacao, registrarTransacao,
} from "../../../frontend/src/services/transacaoService";
import { apiFalsa, chamadas, corpo, prepararNavegador, resposta } from "../apoio";
import { API_APOSENTADORIA, transacao } from "./dados";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => {
  navegador = prepararNavegador();
  navegador.armazenamento.set("access_token", "token-investidor");
});
afterEach(() => vi.unstubAllGlobals());

const COMPRA_ITUB4 = { id_carteira: 1, ticker: "ITUB4", tipo: "compra" as const, quantidade: 200, preco_unitario: 40.89 };

describe("US 11.1 - Registro de compra", () => {
  test("Cenário 1: registrar envia carteira, ativo, tipo, quantidade e preço, e devolve a transação gravada", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /transactions": () => resposta(transacao(5, "compra", "ITUB4", 200, "8178.00"), 201),
    }));

    const gravada = await registrarTransacao(COMPRA_ITUB4);

    expect(chamadas(navegador.fetchFalso)).toEqual(["POST /transactions"]);
    expect(corpo(navegador.fetchFalso, 0)).toEqual(COMPRA_ITUB4);
    expect(gravada).toMatchObject({ tipo: "compra", ticker: "ITUB4", quantidade: 200, valor_total: "8178.00", nome_carteira: "Aposentadoria" });
  });

  test("Cenário 2: a cotação usada no valor total vem da API (200 × R$ 40,89 = R$ 8.178,00)", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa(API_APOSENTADORIA));
    const cotacao = await consultarCotacaoTransacao("ITUB4");
    expect(Number(cotacao.preco) * 200).toBeCloseTo(8178, 2);
  });

  test("Cenário 2: abrir a tela não grava nenhuma transação", () => {
    navegador.fetchFalso.mockImplementation(apiFalsa(API_APOSENTADORIA));
    const html = renderToString(createElement(MemoryRouter, null, createElement(TransacaoPage)));
    expect(html).toContain("A carteira só será alterada após a confirmação.");
    expect(chamadas(navegador.fetchFalso).some(c => c.startsWith("POST"))).toBe(false);
  });

  test("Cenário 1: a tela lista as carteiras, o catálogo e os ativos da carteira com a quantidade atual", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa(API_APOSENTADORIA));
    expect((await listarCarteirasParaTransacao()).map(c => c.nome)).toEqual(["Aposentadoria", "Casa"]);
    expect((await listarCatalogoTransacao()).find(a => a.ticker === "ITUB4")?.setor).toBe("Financeiro");
    expect((await listarAtivosDaCarteira(1)).find(a => a.ticker === "ITUB4")?.quantidade).toBe(300);
  });
});

describe("US 11.2 - Registro de venda", () => {
  test("Cenário 1: a venda é enviada com o tipo venda", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /transactions": () => resposta(transacao(6, "venda", "ITUB4", 100, "4089.00"), 201),
    }));
    const gravada = await registrarTransacao({ ...COMPRA_ITUB4, tipo: "venda", quantidade: 100 });
    expect(corpo(navegador.fetchFalso, 0)).toMatchObject({ tipo: "venda", quantidade: 100 });
    expect(gravada.valor_total).toBe("4089.00");
  });

  test("Cenário 3: venda maior que a quantidade traz a mensagem da API e nada é gravado", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /transactions": () => resposta({ detail: "Quantidade insuficiente para venda. Você possui 100 ações deste ativo." }, 400),
    }));
    await expect(registrarTransacao({ ...COMPRA_ITUB4, tipo: "venda" })).rejects.toThrow(/quantidade insuficiente/i);
  });
});

describe("US 11.3 - Validação dos dados da transação", () => {
  test("Cenário 2: quantidade fora do lote traz a mensagem da API", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /transactions": () => resposta({ detail: "A quantidade deve ser em lotes de 100 ações." }, 400),
    }));
    await expect(registrarTransacao({ ...COMPRA_ITUB4, quantidade: 150 })).rejects.toThrow(/lotes de 100/i);
  });

  test("Cenário 5: ativo que não pertence à carteira traz a mensagem da API", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /transactions": () => resposta({ detail: "Ativo não encontrado nesta carteira." }, 404),
    }));
    await expect(registrarTransacao({ ...COMPRA_ITUB4, ticker: "PETR4" })).rejects.toThrow(/ativo não encontrado nesta carteira/i);
  });

  test("Cenário 8: com o perfil de analista a API nega o registro", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /transactions": () => resposta({ detail: "Esta operação é permitida apenas para investidores." }, 403),
    }));
    await expect(registrarTransacao(COMPRA_ITUB4)).rejects.toThrow("Esta operação é permitida apenas para investidores.");
  });

  test("sem sessão não chama a API", async () => {
    navegador.armazenamento.delete("access_token");
    await expect(registrarTransacao(COMPRA_ITUB4)).rejects.toThrow("Sua sessão expirou. Entre novamente.");
    expect(navegador.fetchFalso).not.toHaveBeenCalled();
  });
});

describe("US 11.4 - Conclusão da transação", () => {
  test("Cenário 3 (opcional): falha ao gravar (409) rejeita o registro", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /transactions": () => resposta({ detail: "Conflito ao registrar a transação. Tente novamente." }, 409),
    }));
    await expect(registrarTransacao(COMPRA_ITUB4)).rejects.toThrow(/conflito/i);
  });

  test("Cenário 3 (opcional): sem conexão com a API o registro é rejeitado", async () => {
    navegador.fetchFalso.mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(registrarTransacao(COMPRA_ITUB4)).rejects.toThrow("Não foi possível conectar à API");
  });

  test("Cenário 3 (opcional): erro sem mensagem usa o código da resposta", async () => {
    navegador.fetchFalso.mockResolvedValue(new Response("erro", { status: 500 }));
    await expect(registrarTransacao(COMPRA_ITUB4)).rejects.toThrow("A API respondeu com erro 500.");
  });
});
