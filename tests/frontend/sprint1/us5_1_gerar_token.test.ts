// US 5.1 - Geração de token de acesso para novo investidor
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { gerarConviteInvestidor, validarEmailConvite } from "../../../frontend/src/services/conviteInvestidorService";
import { API, corpo, prepararNavegador, resposta } from "../apoio";

describe("validação do e-mail do cliente", () => {
  test("Cenário 1: e-mail válido", () => {
    expect(validarEmailConvite("marina.souza@example.test")).toBeNull();
  });

  test("Cenário 2: e-mail em branco", () => {
    expect(validarEmailConvite("   ")).toBe("Informe o e-mail do cliente");
  });

  test("Cenário 3: e-mail em formato inválido", () => {
    expect(validarEmailConvite("marina.souza#email")).toBe("E-mail inválido");
  });
});

describe("geração do token", () => {
  let navegador: ReturnType<typeof prepararNavegador>;
  beforeEach(() => {
    navegador = prepararNavegador();
    navegador.armazenamento.set("access_token", "token-analista");
  });
  afterEach(() => vi.unstubAllGlobals());

  test("Cenário 1: envia o e-mail do cliente e recebe o convite", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({
      id_investidor: 7, id_usuario: 9, email: "marina.souza@example.test", primeiro_acesso_concluido: false, email_acesso_enviado: true,
    }, 201));
    const convite = await gerarConviteInvestidor(" Marina.Souza@Example.test ");

    expect(convite.email_acesso_enviado).toBe(true);
    expect(navegador.fetchFalso.mock.calls[0][0]).toBe(`${API}/investors`);
    expect(corpo(navegador.fetchFalso, 0)).toEqual({ email: "marina.souza@example.test" });
    expect((navegador.fetchFalso.mock.calls[0][1] as RequestInit).headers).toMatchObject({ Authorization: "Bearer token-analista" });
  });

  test.each([
    ["Cenário 2: e-mail em branco", "", "Informe o e-mail do cliente"],
    ["Cenário 3: e-mail inválido", "marina.souza#email", "E-mail inválido"],
  ])("%s não gera o token", async (_, email, mensagem) => {
    await expect(gerarConviteInvestidor(email)).rejects.toThrow(mensagem);
    expect(navegador.fetchFalso).not.toHaveBeenCalled();
  });

  test("Cenário 4: e-mail que já possui cadastro mostra a mensagem da API", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "Já existe um usuário com este e-mail." }, 400));
    await expect(gerarConviteInvestidor("marina.souza@email.com")).rejects.toThrow("Já existe um usuário com este e-mail.");
  });
});
