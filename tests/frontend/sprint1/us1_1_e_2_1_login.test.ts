// US 1.1 - Login do investidor / US 2.1 - Login do analista
import { createElement } from "react";
import { renderToString } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { LayoutPadrao } from "../../../frontend/src/components/LayoutPadrao";
import { buscarUsuarioAutenticado, realizarLogin } from "../../../frontend/src/services/autenticacaoService";
import { API, corpo, prepararNavegador, resposta } from "../apoio";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => { navegador = prepararNavegador(); });
afterEach(() => vi.unstubAllGlobals());

function respostaLogin(perfil: "investidor" | "analista") {
  navegador.fetchFalso
    .mockResolvedValueOnce(resposta({ access_token: "token-teste", token_type: "bearer" }))
    .mockResolvedValueOnce(resposta({ id_usuario: 1, email: "marina.souza@example.test", tipo_usuario: perfil, ativo: true }));
}

function menuDo(perfil: "investidor" | "analista") {
  navegador.armazenamento.set("usuario_autenticado", JSON.stringify({ id: 1, email: "x@example.test", perfil }));
  const html = renderToString(createElement(MemoryRouter, null, createElement(LayoutPadrao)));
  return html.slice(html.indexOf("<nav"), html.indexOf("</nav>"));  // so o menu, sem o rodape
}

describe("US 1.1 - Login do investidor", () => {
  test("Cenário 1: login válido autentica como investidor", async () => {
    respostaLogin("investidor");
    const usuario = await realizarLogin(" marina.souza ", "Marina@2025");

    expect(usuario.perfil).toBe("investidor");
    expect(navegador.fetchFalso.mock.calls[0][0]).toBe(`${API}/auth/login`);
    expect(corpo(navegador.fetchFalso, 0)).toEqual({ nome_usuario: "marina.souza", senha: "Marina@2025" });
    expect(navegador.armazenamento.get("access_token")).toBe("token-teste");
    expect(buscarUsuarioAutenticado()?.perfil).toBe("investidor");
  });

  test("Cenário 1: menu do investidor tem Carteira, Transações, Histórico, Minha Conta e Sair", () => {
    const html = menuDo("investidor");
    for (const opcao of ["Carteira", "Transações", "Histórico", "Minha Conta", "Sair"]) expect(html).toContain(opcao);
  });

  test("Cenário 2: senha incorreta mostra a mensagem da API e não guarda sessão", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "E-mail, nome de usuário ou senha inválidos" }, 401));
    await expect(realizarLogin("marina.souza", "SenhaErrada1")).rejects.toThrow("E-mail, nome de usuário ou senha inválidos");
    expect(navegador.armazenamento.has("access_token")).toBe(false);
  });

  test("Cenário 3: conta inativa não conclui o login", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "Usuário inativo. Contate o administrador." }, 403));
    await expect(realizarLogin("marina.souza", "Marina@2025")).rejects.toThrow("Usuário inativo");
    expect(buscarUsuarioAutenticado()).toBeNull();
  });

  test("Cenário 4: investidor não vê a tela Gerar Token", () => {
    expect(menuDo("investidor")).not.toContain("Gerar token");
  });

  test("Cenário 6: usuário inexistente recebe a mesma mensagem genérica", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "E-mail, nome de usuário ou senha inválidos" }, 401));
    await expect(realizarLogin("usuario_inexistente", "Marina@2025")).rejects.toThrow("E-mail, nome de usuário ou senha inválidos");
  });

  test("erro sem mensagem da API usa texto padrão", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(new Response("erro", { status: 500 }));
    await expect(realizarLogin("marina.souza", "Marina@2025")).rejects.toThrow("Não foi possível realizar o login.");
  });
});

describe("US 2.1 - Login do analista", () => {
  test("Cenário 1: login válido autentica como analista", async () => {
    respostaLogin("analista");
    const usuario = await realizarLogin("paulo.ramos", "1234");
    expect(usuario.perfil).toBe("analista");
  });

  test("Cenário 2: senha incorreta recusa o acesso", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "E-mail, nome de usuário ou senha inválidos" }, 401));
    await expect(realizarLogin("paulo.ramos", "SenhaErrada1")).rejects.toThrow("inválidos");
  });

  test("Cenário 3: menu do analista não tem Carteira, Transações nem Histórico", () => {
    const html = menuDo("analista");
    expect(html).toContain("Investidores");
    expect(html).toContain("Gerar token");
    for (const opcao of ["Carteira", "Transações", "Histórico"]) expect(html).not.toContain(opcao);
  });
});
