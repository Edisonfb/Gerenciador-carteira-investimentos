import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { consultarConfiguracaoCarteira } from "../../frontend/src/services/configuracaoCarteiraService";
beforeEach(() => vi.stubGlobal("localStorage", { getItem: () => "sessao-teste" }));
afterEach(() => vi.unstubAllGlobals());
const resposta = (dados: unknown, status = 200) => new Response(JSON.stringify(dados), { status });
it("carrega a carteira pelo ID, os vínculos e o setor real, incluindo ativo desativado", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(resposta({ id_carteira: 9, nome: "Carro", ativa: true }))
    .mockResolvedValueOnce(resposta([{ ticker: "ITUB4", id_carteira: 9, quantidade: 25, objetivo_percentual: "100.00" }]))
    .mockResolvedValueOnce(resposta([{ ticker: "ITUB4", setor: "Financeiro", ativo: false }]));
  vi.stubGlobal("fetch", fetchMock);
  expect(await consultarConfiguracaoCarteira(9)).toEqual({ carteira: { id_carteira: 9, nome: "Carro", ativa: true }, ativos: [{ ticker: "ITUB4", setor: "Financeiro", ativo: false, quantidade: 25, objetivo: "100.00" }] });
  expect(fetchMock.mock.calls.map(([url]) => url)).toEqual(["http://127.0.0.1:8000/portfolios/9", "http://127.0.0.1:8000/assets/carteira/9", "http://127.0.0.1:8000/assets"]);
  for (const [, opcoes] of fetchMock.mock.calls) expect(opcoes.headers.Authorization).toBe("Bearer sessao-teste");
});
it("não consulta identificador inválido", async () => {
  const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
  await expect(consultarConfiguracaoCarteira(NaN)).rejects.toThrow("Carteira inválida");
  expect(fetchMock).not.toHaveBeenCalled();
});
it("mostra recusa de acesso sem substituir a carteira por outros dados", async () => {
  vi.stubGlobal("fetch", vi.fn().mockImplementation(async () => resposta({ detail: "Carteira não encontrada." }, 404)));
  await expect(consultarConfiguracaoCarteira(9)).rejects.toThrow("Carteira não encontrada");
});
it("aceita carteira sem ativos sem preencher dados financeiros fictícios", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(resposta({ id_carteira: 9, nome: "Carro", ativa: true })).mockResolvedValueOnce(resposta([])).mockResolvedValueOnce(resposta([])));
  expect((await consultarConfiguracaoCarteira(9)).ativos).toEqual([]);
});
