// US 1.2 - Recuperação de senha (Esqueci minha senha)
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { redefinirSenha, solicitarAcessoSenha } from "../../../frontend/src/services/autenticacaoService";
import { API, corpo, prepararNavegador, resposta } from "../apoio";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => { navegador = prepararNavegador(); });
afterEach(() => vi.unstubAllGlobals());

test("Cenário 1: solicita o link informando o e-mail principal", async () => {
  navegador.fetchFalso.mockResolvedValueOnce(resposta({ message: "Se houver uma conta ativa elegível, enviaremos as instruções por e-mail." }));
  await solicitarAcessoSenha("marina.souza@example.test");

  expect(navegador.fetchFalso.mock.calls[0][0]).toBe(`${API}/auth/esqueci-senha`);
  expect(corpo(navegador.fetchFalso, 0)).toEqual({ email: "marina.souza@example.test" });
});

test("Cenário 3: e-mail não cadastrado recebe a mesma resposta (sem erro)", async () => {
  navegador.fetchFalso.mockResolvedValueOnce(resposta({ message: "Se houver uma conta ativa elegível, enviaremos as instruções por e-mail." }));
  await expect(solicitarAcessoSenha("marina.souza23@example.test")).resolves.toBeUndefined();
});

test("Cenário 5: link válido envia o token e a nova senha", async () => {
  navegador.fetchFalso.mockResolvedValueOnce(resposta({ message: "Senha definida com sucesso." }));
  await redefinirSenha("token-do-link", "NovaMarina@2025");

  expect(navegador.fetchFalso.mock.calls[0][0]).toBe(`${API}/auth/redefinir-senha`);
  expect(corpo(navegador.fetchFalso, 0)).toEqual({ token: "token-do-link", senha: "NovaMarina@2025" });
});

test("link expirado mostra a mensagem da API", async () => {
  navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "Link inválido ou expirado. Solicite um novo link." }, 400));
  await expect(redefinirSenha("token-velho", "NovaMarina@2025")).rejects.toThrow("Link inválido ou expirado. Solicite um novo link.");
});

test("serviço de e-mail fora do ar mostra a mensagem da API", async () => {
  navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "Envio de e-mail indisponível. Contate o responsável pelo sistema." }, 503));
  await expect(solicitarAcessoSenha("marina.souza@example.test")).rejects.toThrow("Envio de e-mail indisponível");
});
