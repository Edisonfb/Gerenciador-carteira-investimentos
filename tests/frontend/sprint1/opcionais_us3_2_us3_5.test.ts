// Histórias opcionais (amarelo) da Sprint 1 que já existem no front:
// US 3.2 - Consulta e busca de contas de investidores
// US 3.5 - Edição da própria conta pelo investidor
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { filtrarContasInvestidores } from "../../../frontend/src/services/consultaInvestidoresService";
import type { ContaInvestidorConsulta } from "../../../frontend/src/services/consultaInvestidoresService";
import { salvarContaInvestidor } from "../../../frontend/src/services/contaInvestidorService";
import { validarEdicaoConta } from "../../../frontend/src/types/contaInvestidor";
import { corpo, prepararNavegador, resposta } from "../apoio";

const CONTAS: ContaInvestidorConsulta[] = [
  { id_usuario: 1, email: "marina.souza@example.test", ativo: true, convite: "enviado", cadastro: "concluido" },
  { id_usuario: 2, email: "carlos.lima@email.com", ativo: false, convite: "enviado", cadastro: "pendente" },
];

describe("US 3.2 - Consulta de contas de investidores", () => {
  test("Cenário 2: busca por e-mail", () => {
    expect(filtrarContasInvestidores(CONTAS, "marina.souza").map(c => c.id_usuario)).toEqual([1]);
  });

  test("Cenário 3: filtro por status ativo", () => {
    expect(filtrarContasInvestidores(CONTAS, "", "ativas").map(c => c.id_usuario)).toEqual([1]);
  });

  test("Cenário 4: busca sem resultados", () => {
    expect(filtrarContasInvestidores(CONTAS, "Roberto Almeida")).toEqual([]);
  });
});

describe("US 3.5 - Edição da própria conta", () => {
  const EDICAO = {
    nomeUsuario: "marina.souza", emailComunicacao: "marina.souza@example.test",
    emailRecuperacao: "marina.recovery2@email.com", senhaAtual: "Marina@2025", novaSenha: "", confirmacaoSenha: "",
  };

  let navegador: ReturnType<typeof prepararNavegador>;
  beforeEach(() => {
    navegador = prepararNavegador();
    navegador.armazenamento.set("access_token", "token-investidor");
  });
  afterEach(() => vi.unstubAllGlobals());

  test("Cenário 1: altera o e-mail de recuperação", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({
      id_investidor: 1, nome_usuario: "marina.souza", email: "marina.souza@example.test", email_recuperacao: "marina.recovery2@email.com", ativo: true,
    }));
    const conta = await salvarContaInvestidor(EDICAO);
    expect(conta.emailRecuperacao).toBe("marina.recovery2@email.com");
    expect(corpo(navegador.fetchFalso, 0).email_recuperacao).toBe("marina.recovery2@email.com");
  });

  test("Cenário 2: nova senha vai junto com a senha atual", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({
      id_investidor: 1, nome_usuario: "marina.souza", email: "marina.souza@example.test", email_recuperacao: "x@email.com", ativo: true,
    }));
    await salvarContaInvestidor({ ...EDICAO, novaSenha: "Marina#Nova1", confirmacaoSenha: "Marina#Nova1" });
    expect(corpo(navegador.fetchFalso, 0)).toMatchObject({ senha_atual: "Marina@2025", nova_senha: "Marina#Nova1" });
  });

  test("Cenário 3: e-mail de outra conta mostra a mensagem da API", async () => {
    navegador.fetchFalso.mockResolvedValueOnce(resposta({ detail: "Um dos e-mails informados já está em uso por outra conta." }, 400));
    await expect(salvarContaInvestidor({ ...EDICAO, emailComunicacao: "carlos.lima@email.com" })).rejects.toThrow("já está em uso");
  });

  test("sem a senha atual não salva", () => {
    expect(validarEdicaoConta({ ...EDICAO, senhaAtual: "" })).toBe("Informe sua senha atual para confirmar as alterações.");
  });
});
