import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { consultarConfiguracaoCarteira, editarComposicaoCarteira } from "../../frontend/src/services/configuracaoCarteiraService";
import type { ConfiguracaoCarteira } from "../../frontend/src/services/configuracaoCarteiraService";

beforeEach(() => vi.stubGlobal("localStorage", { getItem: () => "sessao-teste" }));
afterEach(() => vi.unstubAllGlobals());
const original: ConfiguracaoCarteira = {
  carteira: { id_carteira: 5, nome: "Carro", ativa: true },
  ativos: [
    { ticker: "ITUB4", objetivo: "40.00", setor: "Financeiro", ativo: true, quantidade: 12 },
    { ticker: "EGIE3", objetivo: "60.00", setor: "Energia", ativo: true, quantidade: 7 },
  ],
};
const response = (dados: unknown, status = 200) => new Response(JSON.stringify(dados), { status });
function mockApi() {
  const fetchMock = vi.fn().mockImplementation(async (url: string, opcoes?: RequestInit) => {
    if (opcoes?.method) return opcoes.method === "DELETE" ? new Response(null, { status: 204 }) : response({});
    if (url.endsWith("/portfolios")) return response([original.carteira]);
    if (url.endsWith("/portfolios/5")) return response(original.carteira);
    if (url.endsWith("/assets/carteira/5")) return response(original.ativos.map(a => ({ ticker: a.ticker, id_carteira: 5, quantidade: a.quantidade, objetivo_percentual: a.objetivo })));
    if (url.endsWith("/assets")) return response(original.ativos);
    throw new Error(`Consulta inesperada: ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

it("carrega composição e mantém quantidades recebidas da API", async () => {
  mockApi();
  expect(await consultarConfiguracaoCarteira(5)).toEqual(original);
});

it("edita objetivos enviando apenas os percentuais, sem zerar as posições", async () => {
  const fetchMock = mockApi();
  await editarComposicaoCarteira(original, "Carro", original.ativos.map(a => ({ ...a, objetivo: "50" })));
  const gravacoes = fetchMock.mock.calls.filter(([, opcoes]) => opcoes?.method);
  expect(gravacoes).toHaveLength(2);
  for (const [url, opcoes] of gravacoes) {
    expect(url).toMatch(/\/assets\/carteira\/5\/(ITUB4|EGIE3)$/);
    expect(opcoes.method).toBe("PATCH");
    expect(JSON.parse(opcoes.body)).toEqual({ objetivo_percentual: "50.00" });
    expect(opcoes.headers.Authorization).toBe("Bearer sessao-teste");
  }
  expect(original.ativos.map(a => a.quantidade)).toEqual([12, 7]);
});

it("inclui novos ativos com zero, remove apenas os retirados e renomeia ao final", async () => {
  const fetchMock = mockApi();
  await editarComposicaoCarteira(original, "Aposentadoria", [original.ativos[0], { ticker: "ABEV3", objetivo: "60", setor: "Consumo", ativo: true, quantidade: 0 }]);
  const gravacoes = fetchMock.mock.calls.filter(([, opcoes]) => opcoes?.method);
  expect(gravacoes.map(([, opcoes]) => opcoes.method)).toEqual(["POST", "DELETE", "PATCH"]);
  expect(JSON.parse(gravacoes[0][1].body)).toEqual({ ticker: "ABEV3", id_carteira: 5, quantidade: 0, objetivo_percentual: "60.00" });
  expect(gravacoes[1][0]).toBe("http://127.0.0.1:8000/assets/carteira/5/EGIE3");
  expect(JSON.parse(gravacoes[2][1].body)).toEqual({ nome: "Aposentadoria" });
});

it("não grava nada se a composição ficou sem ativos ou não soma 100", async () => {
  const fetchMock = mockApi();
  await expect(editarComposicaoCarteira(original, "Carro", [])).rejects.toThrow("pelo menos um ativo");
  await expect(editarComposicaoCarteira(original, "Carro", [original.ativos[0]])).rejects.toThrow("100%");
  expect(fetchMock.mock.calls.filter(([, opcoes]) => opcoes?.method)).toEqual([]);
});

it("não envia alterações se houve mudança concorrente", async () => {
  const fetchMock = mockApi();
  const antiga = { ...original, ativos: original.ativos.map(a => ({ ...a, quantidade: 0 })) };
  await expect(editarComposicaoCarteira(antiga, "Carro", original.ativos)).rejects.toMatchObject({ impedirReenvio: true });
  expect(fetchMock.mock.calls.filter(([, opcoes]) => opcoes?.method)).toEqual([]);
});

it("em falha parcial bloqueia reenvio e não exclui a carteira existente", async () => {
  const fetchMock = mockApi();
  const normal = fetchMock.getMockImplementation()!;
  fetchMock.mockImplementation(async (url: string, opcoes?: RequestInit) => {
    if (opcoes?.method === "PATCH") return response({ detail: "Ativo desativado" }, 400);
    return normal(url, opcoes);
  });
  await expect(editarComposicaoCarteira(original, "Carro", original.ativos.map(a => ({ ...a, objetivo: "50" })))).rejects.toMatchObject({ impedirReenvio: true, message: expect.stringContaining("Parte delas pode ter sido salva") });
  expect(fetchMock.mock.calls.filter(([, opcoes]) => opcoes?.method)).toHaveLength(1);
});

it("não faz requisições de gravação para edição sem mudanças", async () => {
  const fetchMock = mockApi();
  await editarComposicaoCarteira(original, "Carro", original.ativos);
  expect(fetchMock.mock.calls.filter(([, opcoes]) => opcoes?.method)).toEqual([]);
});
