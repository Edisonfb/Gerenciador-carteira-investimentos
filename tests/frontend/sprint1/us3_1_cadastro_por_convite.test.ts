// US 3.1 - Cadastro do investidor via link de convite
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { validarCadastroPrimeiroAcesso } from "../../../frontend/src/lib/primeiroAcesso";
import { concluirCadastroPrimeiroAcesso } from "../../../frontend/src/services/primeiroAcessoService";
import { API, corpo, prepararNavegador, resposta } from "../apoio";

const DADOS = {
  nomeUsuario: "marina.souza",
  emailComunicacao: "marina.souza@example.test",
  emailRecuperacao: "marina.souza2@example.test",
  senha: "Marina@2025",
  confirmacaoSenha: "Marina@2025",
};

describe("validação do formulário", () => {
  test("Cenário 1: dados corretos passam na validação", () => {
    expect(validarCadastroPrimeiroAcesso(DADOS)).toBeNull();
  });

  test("Cenário 2: e-mail de recuperação em branco", () => {
    expect(validarCadastroPrimeiroAcesso({ ...DADOS, emailRecuperacao: "" })).toBe("Informe um e-mail de recuperação válido.");
  });

  test("Cenário 2: usuário em branco", () => {
    expect(validarCadastroPrimeiroAcesso({ ...DADOS, nomeUsuario: "  " })).toBe("Informe o nome de usuário.");
  });

  test("Cenário 5: e-mail de comunicação em formato inválido", () => {
    expect(validarCadastroPrimeiroAcesso({ ...DADOS, emailComunicacao: "marina.souza#example.test" })).toBe("Informe um e-mail de comunicação válido.");
  });

  test("e-mail de recuperação igual ao de comunicação", () => {
    expect(validarCadastroPrimeiroAcesso({ ...DADOS, emailRecuperacao: "MARINA.SOUZA@example.test" }))
      .toBe("O e-mail de recuperação deve ser diferente do e-mail de comunicação.");
  });

  test("senha com menos de 8 caracteres", () => {
    expect(validarCadastroPrimeiroAcesso({ ...DADOS, senha: "1234567", confirmacaoSenha: "1234567" }))
      .toBe("A senha deve ter no mínimo 8 caracteres e no máximo 72 bytes.");
  });

  test("confirmação de senha diferente", () => {
    expect(validarCadastroPrimeiroAcesso({ ...DADOS, confirmacaoSenha: "Marina@2026" })).toBe("As senhas não coincidem.");
  });
});

describe("envio do cadastro", () => {
  let navegador: ReturnType<typeof prepararNavegador>;
  beforeEach(() => { navegador = prepararNavegador(); });
  afterEach(() => vi.unstubAllGlobals());

  test("Cenário 1: envia os dados para concluir o cadastro", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ message: "Cadastro concluído com sucesso. Entre com seu usuário e senha." }));
    await concluirCadastroPrimeiroAcesso("autorizacao", { ...DADOS, emailComunicacao: " Marina.Souza@Example.test " });

    expect(navegador.fetchFalso.mock.calls[0][0]).toBe(`${API}/investors/first-access`);
    expect(corpo(navegador.fetchFalso, 0)).toEqual({
      token_definicao: "autorizacao", nome_usuario: "marina.souza",
      email_comunicacao: "marina.souza@example.test", email_recuperacao: "marina.souza2@example.test", nova_senha: "Marina@2025",
    });
  });

  test("Cenário 2: campo inválido não chama a API", async () => {
    await expect(concluirCadastroPrimeiroAcesso("autorizacao", { ...DADOS, emailRecuperacao: "" })).rejects.toThrow("e-mail de recuperação");
    expect(navegador.fetchFalso).not.toHaveBeenCalled();
  });

  test("Cenário 3: usuário de login já existente mostra a mensagem da API", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "Já existe um usuário com este nome de usuário." }, 400));
    await expect(concluirCadastroPrimeiroAcesso("autorizacao", DADOS)).rejects.toThrow("Já existe um usuário com este nome de usuário.");
  });

  test("Cenário 4: e-mail de recuperação em uso mostra a mensagem da API", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "Este e-mail de recuperação já está em uso." }, 400));
    await expect(concluirCadastroPrimeiroAcesso("autorizacao", DADOS)).rejects.toThrow("Este e-mail de recuperação já está em uso.");
  });

  test("sem autorização do primeiro acesso não envia", async () => {
    await expect(concluirCadastroPrimeiroAcesso("", DADOS)).rejects.toThrow("Valide seu e-mail e token");
    expect(navegador.fetchFalso).not.toHaveBeenCalled();
  });
});
