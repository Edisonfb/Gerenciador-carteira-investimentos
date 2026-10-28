import { beforeEach, expect, test, vi } from "vitest";

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  vi.resetModules();
  fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
});

test("login de analista e investidor devolve o token de acesso", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({ access_token: "10", token_type: "bearer" }),
  });

  const { realizarLogin } = await import("../../frontend/src/services/autenticacaoService");
  const resposta = await realizarLogin("ana@email.com", "senha123");

  expect(resposta).toEqual({ access_token: "10", token_type: "bearer" });
  expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "ana@email.com", senha: "senha123" }),
  });
});

test("login repassa a mensagem de erro da api", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => ({ detail: "Email ou senha inválidos" }),
  });

  const { realizarLogin } = await import("../../frontend/src/services/autenticacaoService");

  await expect(realizarLogin("ana@email.com", "errada")).rejects.toThrow(
    "Email ou senha inválidos",
  );
});

test("login usa a mensagem padrao quando a api nao explica o erro", async () => {
  fetchMock.mockResolvedValue({
    ok: false,
    json: async () => {
      throw new Error("sem corpo");
    },
  });

  const { realizarLogin } = await import("../../frontend/src/services/autenticacaoService");

  await expect(realizarLogin("ana@email.com", "errada")).rejects.toThrow(
    "Não foi possível realizar o login.",
  );
});

test("usuario autenticado do analista abre a area do analista", async () => {
  const { buscarUsuarioAutenticado } = await import(
    "../../frontend/src/services/autenticacaoService"
  );

  expect(buscarUsuarioAutenticado()).toMatchObject({
    id: 2,
    perfil: "analista",
  });
});
