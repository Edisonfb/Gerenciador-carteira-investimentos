import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { consultarCarteiras, salvarCarteira } from "../../frontend/src/services/configuracaoCarteiraService";
import type { AtivoConfigurado } from "../../frontend/src/types/configuracaoCarteira";

beforeEach(() => vi.stubGlobal("localStorage", { getItem: () => "sessao-teste" }));
afterEach(() => vi.unstubAllGlobals());
const ativos: AtivoConfigurado[] = [
  { ticker: "ITUB4", setor: "Financeiro", ativo: true, objetivo: "20,50", quantidade: 0 },
  { ticker: "EGIE3", setor: "Energia", ativo: true, objetivo: "79.50", quantidade: 0 },
];
const resposta = (dados: unknown, status = 200) => new Response(JSON.stringify(dados), { status });

it("cria a carteira e cadastra os ativos em sequência com o ID retornado", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(resposta({ id_carteira: 42 }, 201))
    .mockResolvedValueOnce(resposta({}, 201)).mockResolvedValueOnce(resposta({}, 201));
  vi.stubGlobal("fetch", fetchMock);
  expect(await salvarCarteira(" Carro ", ativos)).toBe(42);
  expect(fetchMock).toHaveBeenCalledTimes(3);
  expect(fetchMock.mock.calls[0][0]).toBe("http://127.0.0.1:8000/portfolios");
  expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ nome: "Carro" });
  for (const [index, ticker, percentual] of [[1, "ITUB4", "20.50"], [2, "EGIE3", "79.50"]] as const) {
    const [url, opcoes] = fetchMock.mock.calls[index];
    expect(url).toBe("http://127.0.0.1:8000/assets/carteira");
    expect(opcoes.method).toBe("POST");
    expect(opcoes.headers.Authorization).toBe("Bearer sessao-teste");
    expect(JSON.parse(opcoes.body)).toEqual({ ticker, id_carteira: 42, quantidade: 0, objetivo_percentual: percentual });
  }
});

it.each([[], [ativos[0]], [{ ...ativos[0], objetivo: "0" }, { ...ativos[1], objetivo: "100" }]])("não cria carteira com composição inválida %j", async composicao => {
  const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
  await expect(salvarCarteira("Carro", composicao)).rejects.toThrow();
  expect(fetchMock).not.toHaveBeenCalled();
});

it("não cadastra ativos nem exclui nada se o cadastro da carteira for recusado", async () => {
  const fetchMock = vi.fn().mockResolvedValue(resposta({ detail: "Nome inválido" }, 400));
  vi.stubGlobal("fetch", fetchMock);
  await expect(salvarCarteira("Carro", ativos)).rejects.toThrow("Nome inválido");
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

it("remove somente a carteira recém-criada se um ativo falhar após outro ter sido salvo", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(resposta({ id_carteira: 42 }, 201))
    .mockResolvedValueOnce(resposta({}, 201))
    .mockResolvedValueOnce(resposta({ detail: "Ativo desativado" }, 400))
    .mockResolvedValueOnce(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetchMock);
  await expect(salvarCarteira("Carro", ativos)).rejects.toMatchObject({ impedirReenvio: false, message: expect.stringContaining("foi removida") });
  expect(fetchMock.mock.calls[3]).toEqual(["http://127.0.0.1:8000/portfolios/42", { method: "DELETE", headers: { Authorization: "Bearer sessao-teste" } }]);
  expect(ativos[0].objetivo).toBe("20,50");
});

it("também tenta limpar a carteira se a requisição de ativo perder a conexão", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(resposta({ id_carteira: 42 }, 201))
    .mockRejectedValueOnce(new TypeError("Failed to fetch"))
    .mockResolvedValueOnce(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetchMock);
  await expect(salvarCarteira("Carro", ativos)).rejects.toMatchObject({ impedirReenvio: false });
  expect(fetchMock.mock.calls[2][1].method).toBe("DELETE");
});

it("informa carteira possivelmente incompleta e bloqueia reenvio quando a limpeza falha", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(resposta({ id_carteira: 42 }, 201))
    .mockResolvedValueOnce(resposta({ detail: "Falha no ativo" }, 400))
    .mockResolvedValueOnce(resposta({}, 500));
  vi.stubGlobal("fetch", fetchMock);
  await expect(salvarCarteira("Carro", ativos)).rejects.toMatchObject({ impedirReenvio: true, message: expect.stringContaining("carteira 42") });
});

it("trata exclusão 404 como carteira já ausente", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(resposta({ id_carteira: 42 }, 201))
    .mockResolvedValueOnce(resposta({}, 422)).mockResolvedValueOnce(resposta({}, 404)));
  await expect(salvarCarteira("Carro", ativos)).rejects.toMatchObject({ impedirReenvio: false });
});

it.each(["rede", "id", "servidor"])("exige conferência manual se o resultado da criação é incerto: %s", async caso => {
  const fetchMock = vi.fn();
  if (caso === "rede") fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));
  else fetchMock.mockResolvedValue(caso === "id" ? resposta({}) : resposta({}, 500));
  vi.stubGlobal("fetch", fetchMock);
  await expect(salvarCarteira("Carro", ativos)).rejects.toMatchObject({ name: "ErroSalvarCarteira", impedirReenvio: true });
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

it("carrega as carteiras reais para a listagem", async () => {
  const dados = [{ id_carteira: 42, nome: "Carro", ativa: true }];
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(resposta(dados)));
  expect(await consultarCarteiras()).toEqual(dados);
});

it("não inventa carteiras se a listagem está vazia", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(resposta([])));
  expect(await consultarCarteiras()).toEqual([]);
});
