// SCRUM-30 - Distância do objetivo na tela da carteira (valores das US 11.1 e 11.2)
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { consultarConfiguracaoCarteira, consultarResumoFinanceiroCarteira } from "../../../frontend/src/services/configuracaoCarteiraService";
import { apiFalsa, prepararNavegador, resposta } from "../apoio";
import { API_APOSENTADORIA } from "./dados";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => {
  navegador = prepararNavegador();
  navegador.armazenamento.set("access_token", "token-investidor");
  navegador.fetchFalso.mockImplementation(apiFalsa(API_APOSENTADORIA));
});
afterEach(() => vi.unstubAllGlobals());

// Mesma conta da tela DetalheCarteiraPage: participação atual - objetivo.
async function distancias(id: number) {
  const [configuracao, resumo] = await Promise.all([consultarConfiguracaoCarteira(id), consultarResumoFinanceiroCarteira(id)]);
  return Object.fromEntries(configuracao.ativos.map(ativo => {
    const posicao = resumo.ativos.find(p => p.ticker === ativo.ticker)!;
    return [ativo.ticker, Number((posicao.participacao_percentual - Number(ativo.objetivo)).toFixed(2))];
  }));
}

describe("resumo financeiro usado no cálculo", () => {
  test("patrimônio, cotação, valor e participação chegam como números", async () => {
    const resumo = await consultarResumoFinanceiroCarteira(1);
    expect(resumo.patrimonio_total).toBe(17884);
    expect(resumo.ativos.find(p => p.ticker === "ITUB4")).toMatchObject({ quantidade: 300, cotacao: 40.89, valor_atual: 12267, participacao_percentual: 68.59 });
  });

  test("o objetivo de cada ativo vem da composição da carteira", async () => {
    const configuracao = await consultarConfiguracaoCarteira(1);
    expect(configuracao.ativos.map(a => [a.ticker, Number(a.objetivo)])).toEqual([["ABEV3", 50], ["BBDC4", 20], ["EGIE3", 20], ["ITUB4", 10]]);
  });

  test("ativo sem quantidade chega sem cotação e com participação zero", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "GET /portfolios/1/summary": { id_carteira: 1, patrimonio_total: "0.00", ativos: [
        { ticker: "ITUB4", quantidade: 0, cotacao: null, data_atualizacao: null, valor_atual: "0.00", participacao_percentual: "0.00" }] },
    }));
    const resumo = await consultarResumoFinanceiroCarteira(1);
    expect(resumo.ativos[0]).toMatchObject({ cotacao: null, valor_atual: 0, participacao_percentual: 0 });
  });

  test("resumo inválido da API é recusado", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ "GET /portfolios/1/summary": { id_carteira: 1, patrimonio_total: "abc", ativos: [] } }));
    await expect(consultarResumoFinanceiroCarteira(1)).rejects.toThrow("A API retornou um resumo financeiro inválido.");
  });

  test("cotação indisponível traz a mensagem da API", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "GET /portfolios/1/summary": () => resposta({ detail: "Não foi possível calcular o patrimônio: cotação de ITUB4 indisponível." }, 503),
    }));
    await expect(consultarResumoFinanceiroCarteira(1)).rejects.toThrow("cotação de ITUB4 indisponível");
  });
});

describe("US 11.1 e 11.2 - distância do objetivo", () => {
  test("US 11.1 Cenário 1: depois da compra, ITUB4 fica 68,59% e a distância +58,59%", async () => {
    expect((await distancias(1)).ITUB4).toBe(58.59);
  });

  test("US 11.1 Cenário 1: ativos abaixo do objetivo ficam com distância negativa", async () => {
    expect(await distancias(1)).toEqual({ ABEV3: -41.09, BBDC4: -11.94, EGIE3: -5.56, ITUB4: 58.59 });
  });

  test("US 11.2 Cenário 1: depois da venda, ITUB4 fica 42,13% e a distância 32,13%", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      ...API_APOSENTADORIA,
      "GET /portfolios/1/summary": { id_carteira: 1, patrimonio_total: "9706.00", ativos: [
        { ticker: "ABEV3", quantidade: 100, cotacao: "15.93", data_atualizacao: null, valor_atual: "1593.00", participacao_percentual: "16.41" },
        { ticker: "BBDC4", quantidade: 100, cotacao: "14.41", data_atualizacao: null, valor_atual: "1441.00", participacao_percentual: "14.85" },
        { ticker: "EGIE3", quantidade: 100, cotacao: "25.83", data_atualizacao: null, valor_atual: "2583.00", participacao_percentual: "26.61" },
        { ticker: "ITUB4", quantidade: 100, cotacao: "40.89", data_atualizacao: null, valor_atual: "4089.00", participacao_percentual: "42.13" },
      ] },
    }));
    expect((await distancias(1)).ITUB4).toBe(32.13);
  });
});
