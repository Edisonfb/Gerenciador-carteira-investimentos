// US 7.1 - Criação de carteira
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { validarConfiguracao } from "../../../frontend/src/lib/configuracaoCarteira";
import { consultarNomesCarteiras, salvarCarteira } from "../../../frontend/src/services/configuracaoCarteiraService";
import { apiFalsa, chamadas, corpo, prepararNavegador, resposta } from "../apoio";
import { APOSENTADORIA, configurado } from "./catalogo";

describe("validação da tela 'Defina o objetivo da sua carteira'", () => {
  test("Cenário 1: nome e ativos somando 100% são aceitos", () => {
    expect(validarConfiguracao("Aposentadoria", APOSENTADORIA)).toBeNull();
  });

  test("Cenário 2: nome da carteira em branco", () => {
    expect(validarConfiguracao("   ", APOSENTADORIA)).toBe("Informe o nome da carteira");
  });

  test("Cenário 4: outro nome é aceito mesmo já existindo 'Aposentadoria'", () => {
    expect(validarConfiguracao("Carro", [configurado("AALR3", "20"), configurado("ITUB3", "80")], ["Aposentadoria"])).toBeNull();
  });

  test("Cenário 5: nome já usado pelo mesmo investidor (sem diferenciar maiúsculas)", () => {
    expect(validarConfiguracao("aposentadoria ", APOSENTADORIA, ["Aposentadoria"])).toBe("Já existe uma carteira com este nome");
  });

  test("carteira sem ativos não é aceita", () => {
    expect(validarConfiguracao("Aposentadoria", [])).toBe("Inclua pelo menos um ativo na carteira");
  });
});

describe("salvar a carteira", () => {
  let navegador: ReturnType<typeof prepararNavegador>;
  beforeEach(() => {
    navegador = prepararNavegador();
    navegador.armazenamento.set("access_token", "token-investidor");
  });
  afterEach(() => vi.unstubAllGlobals());

  test("Cenário 1: cria a carteira e inclui cada ativo com quantidade zero", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /portfolios": () => resposta({ id_carteira: 1, id_investidor: 1, nome: "Aposentadoria", ativa: true, data_criacao: "2026-10-29T00:00:00" }, 201),
      "POST /assets/carteira": () => resposta({}, 201),
    }));

    expect(await salvarCarteira(" Aposentadoria ", APOSENTADORIA)).toBe(1);
    expect(chamadas(navegador.fetchFalso)).toEqual(["POST /portfolios", ...Array(5).fill("POST /assets/carteira")]);
    expect(corpo(navegador.fetchFalso, 0)).toEqual({ nome: "Aposentadoria" });
    expect(corpo(navegador.fetchFalso, 3)).toEqual({ ticker: "CRFB3", id_carteira: 1, quantidade: 0, objetivo_percentual: "40.00" });
  });

  test("Cenário 2: nome em branco não chama a API", async () => {
    await expect(salvarCarteira("", APOSENTADORIA)).rejects.toThrow("Informe o nome da carteira");
    expect(navegador.fetchFalso).not.toHaveBeenCalled();
  });

  test("Cenário 4: nomes das carteiras existentes vêm da listagem", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "GET /portfolios": [{ id_carteira: 1, nome: "Aposentadoria", ativa: true }, { id_carteira: 2, nome: "Carro", ativa: true }],
    }));
    expect(await consultarNomesCarteiras()).toEqual(["Aposentadoria", "Carro"]);
  });

  test("se um ativo falhar a carteira criada é removida", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({
      "POST /portfolios": () => resposta({ id_carteira: 9 }, 201),
      "POST /assets/carteira": () => resposta({ detail: "Ativo não encontrado." }, 404),
      "DELETE /portfolios/9": () => resposta(null, 204),
    }));
    await expect(salvarCarteira("Aposentadoria", APOSENTADORIA)).rejects.toThrow("A carteira criada nesta tentativa foi removida");
    expect(chamadas(navegador.fetchFalso)).toContain("DELETE /portfolios/9");
  });
});
