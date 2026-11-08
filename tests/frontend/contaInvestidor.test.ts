import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { buscarContaInvestidor, salvarContaInvestidor } from "../../frontend/src/services/contaInvestidorService";
import { validarEdicaoConta } from "../../frontend/src/types/contaInvestidor";
const perfil = { id_investidor: 3, nome_usuario: "ana", email: "contato@example.test", email_recuperacao: "recuperar@example.test", ativo: true };
const dados = { nomeUsuario: " Ana ", emailComunicacao: " Contato@example.test ", emailRecuperacao: "recuperar@example.test", senhaAtual: "senha-atual", novaSenha: "", confirmacaoSenha: "" };
beforeEach(() => vi.stubGlobal("localStorage", { getItem: () => "sessao-teste" }));
afterEach(() => vi.unstubAllGlobals());
it("carrega somente os dados da conta necessários para a tela", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(perfil))));
  expect(await buscarContaInvestidor()).toEqual({ id: 3, nomeUsuario: "ana", emailComunicacao: "contato@example.test", emailRecuperacao: "recuperar@example.test", ativo: true });
});
it("salva somente os campos da conta, sem enviar senha nova vazia", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(perfil))); vi.stubGlobal("fetch", fetchMock);
  await salvarContaInvestidor(dados);
  expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ nome_usuario: "Ana", email: "contato@example.test", email_recuperacao: "recuperar@example.test", senha_atual: "senha-atual" });
  expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe("Bearer sessao-teste");
});
it("envia nova senha somente quando confirmada", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(perfil))); vi.stubGlobal("fetch", fetchMock);
  await salvarContaInvestidor({ ...dados, novaSenha: "senha-nova", confirmacaoSenha: "senha-nova" });
  expect(JSON.parse(fetchMock.mock.calls[0][1].body).nova_senha).toBe("senha-nova");
  expect(JSON.parse(fetchMock.mock.calls[0][1].body)).not.toHaveProperty("confirmacaoSenha");
});
it.each([{ nomeUsuario: "" }, { emailComunicacao: "invalido" }, { emailRecuperacao: "contato@example.test" }, { senhaAtual: "" }, { novaSenha: "curta", confirmacaoSenha: "curta" }, { novaSenha: "senha-valida", confirmacaoSenha: "outra" }])("valida antes de enviar %j", alteracoes => {
  expect(validarEdicaoConta({ ...dados, ...alteracoes })).not.toBeNull();
});
it("mostra o erro de senha atual sem indicar sucesso", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Senha atual inválida." }), { status: 400 })));
  await expect(salvarContaInvestidor(dados)).rejects.toThrow("Senha atual inválida");
});
it("não consulta sem sessão", async () => {
  vi.stubGlobal("localStorage", { getItem: () => null });
  const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
  await expect(buscarContaInvestidor()).rejects.toThrow("sessão expirou");
  expect(fetchMock).not.toHaveBeenCalled();
});
