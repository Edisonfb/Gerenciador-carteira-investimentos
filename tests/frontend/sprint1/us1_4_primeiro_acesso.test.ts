// US 1.4 - Primeiro acesso do investidor
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { validarPrimeiroAcesso } from "../../../frontend/src/services/autenticacaoService";
import { API, corpo, prepararNavegador, resposta } from "../apoio";

const MENSAGEM = "E-mail ou token inválido, ou primeiro acesso já concluído.";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => { navegador = prepararNavegador(); });
afterEach(() => vi.unstubAllGlobals());

test("Cenário 2: e-mail e senha temporária corretos liberam o Cadastro", async () => {
  navegador.fetchFalso.mockResolvedValueOnce(resposta({ token_definicao: "autorizacao-cadastro" }));
  const autorizacao = await validarPrimeiroAcesso("marina.souza@example.test", "eU6qTAwJi_A");

  expect(autorizacao).toBe("autorizacao-cadastro");
  expect(navegador.fetchFalso.mock.calls[0][0]).toBe(`${API}/auth/primeiro-acesso`);
  expect(corpo(navegador.fetchFalso, 0)).toEqual({ email: "marina.souza@example.test", token: "eU6qTAwJi_A" });
});

test.each([
  ["Cenário 4: senha temporária incorreta", "marina.souza@example.test", "Temp#0000"],
  ["Cenário 5: e-mail diferente do convite", "marina.souzaa@example.test", "eU6qTAwJi_A"],
  ["Cenário 7: acesso já utilizado", "marina.souza@email.com", "Temp#4821"],
])("%s mostra a mensagem e não libera o Cadastro", async (_, email, token) => {
  navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: MENSAGEM }, 400));
  await expect(validarPrimeiroAcesso(email, token)).rejects.toThrow(MENSAGEM);
});

test("erro de validação da API (lista) usa mensagem padrão", async () => {
  navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: [{ msg: "Field required" }] }, 422));
  await expect(validarPrimeiroAcesso("", "")).rejects.toThrow("Não foi possível concluir a solicitação.");
});
