import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { validarCadastroPrimeiroAcesso } from "../../frontend/src/lib/primeiroAcesso";
import { concluirCadastroPrimeiroAcesso } from "../../frontend/src/services/primeiroAcessoService";
const dados = { nomeUsuario: " Ana ", emailComunicacao: " Contato@example.test ", emailRecuperacao: "recuperar@example.test", senha: "senha-valida", confirmacaoSenha: "senha-valida" };
beforeEach(() => vi.stubGlobal("fetch", vi.fn()));
afterEach(() => vi.unstubAllGlobals());
it("aceita cadastro completo", () => expect(validarCadastroPrimeiroAcesso(dados)).toBeNull());
it.each([
  { nomeUsuario: " " }, { nomeUsuario: "a".repeat(51) }, { emailComunicacao: "sem-email" }, { emailRecuperacao: "invalido" },
  { emailRecuperacao: "contato@example.test" }, { senha: "123", confirmacaoSenha: "123" }, { confirmacaoSenha: "outra-senha" },
  { senha: "á".repeat(37), confirmacaoSenha: "á".repeat(37) },
])("rejeita campos inválidos %j", alteracoes => expect(validarCadastroPrimeiroAcesso({ ...dados, ...alteracoes })).not.toBeNull());
it("envia cadastro com autorização temporária sem criar sessão de login", async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response("{}")); vi.stubGlobal("fetch", fetchMock);
  await concluirCadastroPrimeiroAcesso("autorizacao-temporaria", dados);
  expect(fetchMock).toHaveBeenCalledExactlyOnceWith("http://127.0.0.1:8000/investors/first-access", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token_definicao: "autorizacao-temporaria", nome_usuario: "Ana", email_comunicacao: "contato@example.test", email_recuperacao: "recuperar@example.test", nova_senha: "senha-valida" }),
  });
});
it("não envia cadastro sem autorização", async () => {
  await expect(concluirCadastroPrimeiroAcesso("", dados)).rejects.toThrow("Valide seu e-mail e token");
  expect(fetch).not.toHaveBeenCalled();
});
it("não envia confirmação de senha divergente", async () => {
  await expect(concluirCadastroPrimeiroAcesso("temporario", { ...dados, confirmacaoSenha: "outra" })).rejects.toThrow("não coincidem");
  expect(fetch).not.toHaveBeenCalled();
});
it("mostra erro de usuário duplicado devolvido pela API", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Já existe um usuário com este nome de usuário." }), { status: 400 })));
  await expect(concluirCadastroPrimeiroAcesso("temporario", dados)).rejects.toThrow("Já existe um usuário");
});
