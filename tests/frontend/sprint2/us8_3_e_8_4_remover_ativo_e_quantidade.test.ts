// US 8.3 - Remoção de ativo da carteira / US 8.4 - Campos calculados e quantidade protegidos
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { validarConfiguracao } from "../../../frontend/src/lib/configuracaoCarteira";
import { distribuicaoObjetivos } from "../../../frontend/src/lib/detalheCarteira";
import { consultarConfiguracaoCarteira, editarComposicaoCarteira } from "../../../frontend/src/services/configuracaoCarteiraService";
import { apiFalsa, chamadas, corpo, prepararNavegador, semConteudo } from "../apoio";
import { APOSENTADORIA, API_CARTEIRA_1 } from "./catalogo";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => {
  navegador = prepararNavegador();
  navegador.armazenamento.set("access_token", "token-investidor");
});
afterEach(() => vi.unstubAllGlobals());

async function carteiraSalva(rotasExtras: Record<string, unknown> = {}) {
  navegador.fetchFalso.mockImplementation(apiFalsa({ ...API_CARTEIRA_1, ...rotasExtras }));
  const original = await consultarConfiguracaoCarteira(1);
  navegador.fetchFalso.mockClear();
  return original;
}

describe("US 8.3 - Remoção de ativo", () => {
  test("Cenário 1: remover ITUB4 e redistribuir envia só a exclusão e o novo objetivo", async () => {
    const original = await carteiraSalva({ "DELETE /assets/carteira/1/ITUB4": semConteudo, "PATCH /assets/carteira/1/CRFB3": {} });
    const semItub4 = original.ativos.filter(a => a.ticker !== "ITUB4").map(a => a.ticker === "CRFB3" ? { ...a, objetivo: "60" } : a);

    await editarComposicaoCarteira(original, "Aposentadoria", semItub4);

    const alteracoes = chamadas(navegador.fetchFalso).filter(c => !c.startsWith("GET"));
    expect(alteracoes).toEqual(["PATCH /assets/carteira/1/CRFB3", "DELETE /assets/carteira/1/ITUB4"]);
    // Nenhuma transacao e registrada pela remocao.
    expect(chamadas(navegador.fetchFalso).some(c => c.includes("/transactions"))).toBe(false);
  });

  test("Cenário 3: sem redistribuir, a soma de 80% não é aceita", () => {
    const semItub4 = APOSENTADORIA.filter(a => a.ticker !== "ITUB4");
    expect(validarConfiguracao("Aposentadoria", semItub4)).toBe("O objetivo total da carteira deve somar 100%. Soma atual: 80%");
  });

  test("Cenário 3: com a soma errada nada é enviado para a API", async () => {
    const original = await carteiraSalva();
    const semItub4 = original.ativos.filter(a => a.ticker !== "ITUB4");

    await expect(editarComposicaoCarteira(original, "Aposentadoria", semItub4)).rejects.toThrow("Soma atual: 80%");
    expect(chamadas(navegador.fetchFalso).filter(c => !c.startsWith("GET"))).toEqual([]);
  });
});

describe("US 8.4 - Campos calculados e quantidade protegidos", () => {
  test("Cenário 2: a quantidade vem da API (ITUB4 = 25) e é mantida", async () => {
    const original = await carteiraSalva();
    expect(original.ativos.find(a => a.ticker === "ITUB4")?.quantidade).toBe(25);
  });

  test("Cenário 2: ao editar objetivo, a quantidade não é enviada", async () => {
    const original = await carteiraSalva({ "PATCH /assets/carteira/1/ITUB4": {}, "PATCH /assets/carteira/1/CRFB3": {} });
    const alterado = original.ativos.map(a =>
      a.ticker === "ITUB4" ? { ...a, objetivo: "25" } : a.ticker === "CRFB3" ? { ...a, objetivo: "35" } : a);

    await editarComposicaoCarteira(original, "Aposentadoria", alterado);

    const indice = chamadas(navegador.fetchFalso).indexOf("PATCH /assets/carteira/1/ITUB4");
    expect(corpo(navegador.fetchFalso, indice)).toEqual({ objetivo_percentual: "25.00" });
  });

  test("Cenário 2: ativo novo entra sempre com quantidade zero", async () => {
    const original = await carteiraSalva({ "POST /assets/carteira": {}, "PATCH /assets/carteira/1/CRFB3": {} });
    const comAalr3 = [...original.ativos.map(a => a.ticker === "CRFB3" ? { ...a, objetivo: "30" } : a),
      { ticker: "AALR3", setor: "Saúde", ativo: true, objetivo: "10", quantidade: 999 }];

    await editarComposicaoCarteira(original, "Aposentadoria", comAalr3);

    const indice = chamadas(navegador.fetchFalso).indexOf("POST /assets/carteira");
    expect(corpo(navegador.fetchFalso, indice)).toMatchObject({ ticker: "AALR3", quantidade: 0 });
  });

  test("Cenário 1: o gráfico de objetivos é calculado pelo sistema", () => {
    const { fatias, total } = distribuicaoObjetivos(APOSENTADORIA);
    expect(total).toBe(100);
    expect(fatias.map(f => f.percentual)).toEqual([10, 10, 40, 20, 20]);
  });
});
