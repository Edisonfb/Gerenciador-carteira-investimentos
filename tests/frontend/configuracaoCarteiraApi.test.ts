import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { consultarAtivosAceitos, consultarNomesCarteiras } from "../../frontend/src/services/configuracaoCarteiraService";

beforeEach(() => vi.stubGlobal("localStorage", { getItem: () => "sessao-teste" }));
afterEach(() => vi.unstubAllGlobals());

const ativo = { ticker: "ITUB4", nome: "Itaú", setor: "Financeiro", subsetor: "Bancos", segmento: "Bancos", ativo: true, data_criacao: "2026-10-28T10:00:00" };

it("consome ticker sem exigir os antigos id_ativo e codigo e filtra inativos", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify([ativo, { ...ativo, ticker: "ITUB3", ativo: false }])));
  vi.stubGlobal("fetch", fetchMock);
  const controller = new AbortController();
  expect(await consultarAtivosAceitos(controller.signal)).toEqual([ativo]);
  expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/assets", {
    headers: { Authorization: "Bearer sessao-teste" }, signal: controller.signal,
  });
});

it("consulta nomes somente na API autenticada de carteiras", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify([{ id_carteira: 5, id_investidor: 3, nome: "Aposentadoria", ativa: true, data_criacao: "2026-10-28T10:00:00" }])));
  vi.stubGlobal("fetch", fetchMock);
  expect(await consultarNomesCarteiras()).toEqual(["Aposentadoria"]);
  expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/portfolios", expect.objectContaining({ headers: { Authorization: "Bearer sessao-teste" } }));
});

it.each([{}, [{ codigo: "ITUB4", setor: "Financeiro", ativo: true }], [{ ...ativo, ticker: "" }], [{ ...ativo, setor: null }]])("recusa catálogo incompatível %j", async dados => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(dados))));
  await expect(consultarAtivosAceitos()).rejects.toThrow("catálogo de ativos inválido");
});

it("aceita catálogo vazio sem inventar ativos", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("[]")));
  expect(await consultarAtivosAceitos()).toEqual([]);
});

it("informa expiração de sessão antes de consultar", async () => {
  vi.stubGlobal("localStorage", { getItem: () => null });
  const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
  await expect(consultarAtivosAceitos()).rejects.toThrow("sessão expirou");
  expect(fetchMock).not.toHaveBeenCalled();
});

it("mostra o erro de autorização devolvido pelo backend", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Não autenticado" }), { status: 401 })));
  await expect(consultarAtivosAceitos()).rejects.toThrow("Não autenticado");
});

it("informa indisponibilidade da API", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
  await expect(consultarAtivosAceitos()).rejects.toThrow("Verifique se o backend está iniciado");
});

it("preserva cancelamento ao sair da página", async () => {
  const erro = new DOMException("Cancelado", "AbortError");
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(erro));
  await expect(consultarAtivosAceitos()).rejects.toBe(erro);
});
