import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { buscarMinhaContaAnalista } from "../../frontend/src/services/contaAnalistaService";

beforeEach(() => vi.stubGlobal("localStorage", { getItem: () => "sessao-teste" }));
afterEach(() => vi.unstubAllGlobals());

it("busca somente o perfil correspondente ao usuário autenticado, sem confundir IDs", async () => {
  const fetchMock = vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ id_usuario: 25, email: "meu@example.test", tipo_usuario: "analista", ativo: true })))
    .mockResolvedValueOnce(new Response(JSON.stringify([
      { id_analista: 25, id_usuario: 99, nome: "Outro", email: "outro@example.test" },
      { id_analista: 3, id_usuario: 25, nome: "Meu nome", email: "meu@example.test" },
    ])));
  vi.stubGlobal("fetch", fetchMock);
  expect(await buscarMinhaContaAnalista()).toMatchObject({ id_analista: 3, id_usuario: 25, nome: "Meu nome", ativo: true });
  expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe("Bearer sessao-teste");
});

it("recusa consultar perfil de analista quando a sessão é de investidor", async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ id_usuario: 25, tipo_usuario: "investidor" })));
  vi.stubGlobal("fetch", fetchMock);
  await expect(buscarMinhaContaAnalista()).rejects.toThrow("conta do analista");
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

it("não substitui o perfil ausente por dados de outro analista", async () => {
  vi.stubGlobal("fetch", vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ id_usuario: 25, tipo_usuario: "analista" })))
    .mockResolvedValueOnce(new Response(JSON.stringify([{ id_analista: 3, id_usuario: 99 }]))));
  await expect(buscarMinhaContaAnalista()).rejects.toThrow("Perfil de analista não encontrado");
});
