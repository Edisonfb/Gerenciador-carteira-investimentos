import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { buscarUsuarioAutenticado, realizarLogin } from "../../frontend/src/services/autenticacaoService";

let fetchMock: ReturnType<typeof vi.fn>;
let armazenamento: Map<string, string>;
beforeEach(() => {
  armazenamento = new Map();
  vi.stubGlobal("localStorage", {
    getItem: (chave: string) => armazenamento.get(chave) ?? null,
    setItem: (chave: string, valor: string) => armazenamento.set(chave, valor),
    removeItem: (chave: string) => armazenamento.delete(chave),
  });
  fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
});
afterEach(() => vi.unstubAllGlobals());
const resposta = (dados: unknown, status = 200) => new Response(JSON.stringify(dados), { status });

test.each(["analista", "investidor"])("login com nome de usuário recupera o perfil %s", async perfil => {
  fetchMock.mockResolvedValueOnce(resposta({ access_token: "sessao-teste", token_type: "bearer" }))
    .mockResolvedValueOnce(resposta({ id_usuario: 2, nome_usuario: "ana", email: "ana@example.test", tipo_usuario: perfil, ativo: true }));
  expect(await realizarLogin(" ana ", "senha123")).toEqual({ id: 2, email: "ana@example.test", perfil });
  expect(fetchMock.mock.calls[0]).toEqual(["http://127.0.0.1:8000/auth/login", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome_usuario: "ana", senha: "senha123" }),
  }]);
  expect(fetchMock.mock.calls[1]).toEqual(["http://127.0.0.1:8000/auth/me", { headers: { Authorization: "Bearer sessao-teste" } }]);
  expect(buscarUsuarioAutenticado()?.perfil).toBe(perfil);
});

test("login repassa a mensagem de erro da API", async () => {
  fetchMock.mockResolvedValueOnce(resposta({ detail: "Nome de usuário ou senha inválidos" }, 401));
  await expect(realizarLogin("ana", "errada")).rejects.toThrow("Nome de usuário ou senha inválidos");
  expect(fetchMock).toHaveBeenCalledTimes(1);
  expect(armazenamento.has("access_token")).toBe(false);
});

test("login usa mensagem padrão quando a API não explica o erro", async () => {
  fetchMock.mockResolvedValueOnce(new Response("sem corpo", { status: 500 }));
  await expect(realizarLogin("ana", "errada")).rejects.toThrow("Não foi possível realizar o login.");
});

test("descarta sessão se não conseguir recuperar o perfil autenticado", async () => {
  fetchMock.mockResolvedValueOnce(resposta({ access_token: "sessao-teste", token_type: "bearer" }))
    .mockResolvedValueOnce(resposta({}, 401));
  await expect(realizarLogin("ana", "senha123")).rejects.toThrow("Sessão inválida");
  expect(armazenamento.size).toBe(0);
});

test("sem sessão não inventa um usuário autenticado", () => {
  expect(buscarUsuarioAutenticado()).toBeNull();
});
