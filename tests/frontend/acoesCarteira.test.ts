import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { excluirCarteira, renomearCarteira } from "../../frontend/src/services/configuracaoCarteiraService";

beforeEach(() => vi.stubGlobal("localStorage", { getItem: () => "sessao-teste" }));
afterEach(() => vi.unstubAllGlobals());
const resposta = (dados: unknown, status = 200) => new Response(JSON.stringify(dados), { status });
const carteiras = [
  { id_carteira: 3, nome: "Carro", ativa: true },
  { id_carteira: 8, nome: "Viagem", ativa: true },
];

it("edita somente o nome da carteira escolhida, sem enviar ativos ou quantidades", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(resposta(carteiras)).mockResolvedValueOnce(resposta({}));
  vi.stubGlobal("fetch", fetchMock);
  await renomearCarteira(3, " Aposentadoria ");
  expect(fetchMock.mock.calls[1]).toEqual(["http://127.0.0.1:8000/portfolios/3", {
    method: "PATCH", headers: { Authorization: "Bearer sessao-teste", "Content-Type": "application/json" }, body: JSON.stringify({ nome: "Aposentadoria" }),
  }]);
});

it("aceita manter o próprio nome", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(resposta(carteiras)).mockResolvedValueOnce(resposta({}));
  vi.stubGlobal("fetch", fetchMock);
  await renomearCarteira(3, "Carro");
  expect(fetchMock).toHaveBeenCalledTimes(2);
});

it("impede usar o nome de outra carteira antes de enviar PATCH", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(resposta(carteiras));
  vi.stubGlobal("fetch", fetchMock);
  await expect(renomearCarteira(3, " viagem ")).rejects.toThrow("Já existe uma carteira");
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

it.each([" ", "a".repeat(101)])("rejeita nome inválido sem requisição", async nome => {
  const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
  await expect(renomearCarteira(3, nome)).rejects.toThrow();
  expect(fetchMock).not.toHaveBeenCalled();
});

it("exclui somente a carteira selecionada e aceita resposta sem corpo", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetchMock);
  await excluirCarteira(8);
  expect(fetchMock).toHaveBeenCalledExactlyOnceWith("http://127.0.0.1:8000/portfolios/8", { method: "DELETE", headers: { Authorization: "Bearer sessao-teste" } });
});

it("aceita carteira já removida", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(resposta({}, 404)));
  await expect(excluirCarteira(8)).resolves.toBeUndefined();
});

it("mostra recusa da API sem indicar sucesso", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(resposta({ detail: "Acesso negado" }, 403)));
  await expect(excluirCarteira(8)).rejects.toThrow("Acesso negado");
});

it("orienta conferir a listagem se a exclusão perde a conexão", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
  await expect(excluirCarteira(8)).rejects.toThrow("Atualize a listagem");
});

it("não exclui sem sessão", async () => {
  vi.stubGlobal("localStorage", { getItem: () => null });
  const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
  await expect(excluirCarteira(8)).rejects.toThrow("sessão expirou");
  expect(fetchMock).not.toHaveBeenCalled();
});
