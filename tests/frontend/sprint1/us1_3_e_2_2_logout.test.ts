// US 1.3 - Logout do investidor / US 2.2 - Logout do analista
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { buscarUsuarioAutenticado, encerrarSessao, obterTokenAcesso, obterUsuarioAtual } from "../../../frontend/src/services/autenticacaoService";
import { prepararNavegador } from "../apoio";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => { navegador = prepararNavegador(); });
afterEach(() => vi.unstubAllGlobals());

test.each(["investidor", "analista"])("Cenário 1: logout do %s apaga a sessão salva", perfil => {
  navegador.armazenamento.set("access_token", "token-teste");
  navegador.armazenamento.set("token_type", "bearer");
  navegador.armazenamento.set("usuario_autenticado", JSON.stringify({ id: 1, email: "x@example.test", perfil }));

  encerrarSessao();

  expect(obterTokenAcesso()).toBeNull();
  expect(buscarUsuarioAutenticado()).toBeNull();
  expect(navegador.armazenamento.size).toBe(0);
});

test("depois do logout as telas protegidas não encontram sessão", async () => {
  encerrarSessao();
  await expect(obterUsuarioAtual()).rejects.toThrow("Não há uma sessão ativa.");
  expect(navegador.fetchFalso).not.toHaveBeenCalled();
});
