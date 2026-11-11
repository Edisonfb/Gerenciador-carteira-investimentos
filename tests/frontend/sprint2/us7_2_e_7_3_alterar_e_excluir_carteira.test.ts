// US 7.2 - Alteração de carteira / US 7.3 - Exclusão de carteira
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import {
  consultarConfiguracaoCarteira, editarComposicaoCarteira, excluirCarteira, renomearCarteira,
} from "../../../frontend/src/services/configuracaoCarteiraService";
import { apiFalsa, chamadas, corpo, prepararNavegador, resposta, semConteudo } from "../apoio";
import { API_CARTEIRA_1 } from "./catalogo";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => {
  navegador = prepararNavegador();
  navegador.armazenamento.set("access_token", "token-investidor");
});
afterEach(() => vi.unstubAllGlobals());

describe("US 7.2 - Alteração de carteira", () => {
  test("Cenário 1: altera o nome para 'Aposentadoria 2040'", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ ...API_CARTEIRA_1, "PATCH /portfolios/1": { id_carteira: 1, nome: "Aposentadoria 2040" } }));
    await renomearCarteira(1, " Aposentadoria 2040 ");

    expect(chamadas(navegador.fetchFalso)).toEqual(["GET /portfolios", "PATCH /portfolios/1"]);
    expect(corpo(navegador.fetchFalso, 1)).toEqual({ nome: "Aposentadoria 2040" });
  });

  test("Cenário 1: na edição completa, mudar só o nome mantém ativos e quantidades", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ ...API_CARTEIRA_1, "PATCH /portfolios/1": {} }));
    const original = await consultarConfiguracaoCarteira(1);
    navegador.fetchFalso.mockClear();

    await editarComposicaoCarteira(original, "Aposentadoria 2040", original.ativos);

    const alteracoes = chamadas(navegador.fetchFalso).filter(c => !c.startsWith("GET"));
    expect(alteracoes).toEqual(["PATCH /portfolios/1"]);
  });

  test("Cenário 2: nome em branco não é salvo", async () => {
    await expect(renomearCarteira(1, "   ")).rejects.toThrow("Informe o nome da carteira");
    expect(navegador.fetchFalso).not.toHaveBeenCalled();
  });

  test("Cenário 4: nome já usado em outra carteira não é salvo", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa(API_CARTEIRA_1));
    await expect(renomearCarteira(2, "Aposentadoria")).rejects.toThrow("Já existe uma carteira com este nome");
    expect(chamadas(navegador.fetchFalso)).toEqual(["GET /portfolios"]);
  });

  test("manter o próprio nome não acusa duplicidade", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ ...API_CARTEIRA_1, "PATCH /portfolios/1": {} }));
    await expect(renomearCarteira(1, "Aposentadoria")).resolves.toBeUndefined();
  });
});

describe("US 7.3 - Exclusão de carteira", () => {
  test("Cenário 1: confirma a exclusão da carteira 'Carro'", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ "DELETE /portfolios/2": semConteudo }));
    await excluirCarteira(2);
    expect(chamadas(navegador.fetchFalso)).toEqual(["DELETE /portfolios/2"]);
  });

  test("carteira já excluída (404) não gera erro", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({}));
    await expect(excluirCarteira(2)).resolves.toBeUndefined();
  });

  test("id inválido não chama a API", async () => {
    await expect(excluirCarteira(0)).rejects.toThrow("Carteira inválida.");
    expect(navegador.fetchFalso).not.toHaveBeenCalled();
  });

  test("erro do servidor é mostrado", async () => {
    navegador.fetchFalso.mockImplementation(apiFalsa({ "DELETE /portfolios/2": () => resposta({ detail: "Erro ao excluir." }, 500) }));
    await expect(excluirCarteira(2)).rejects.toThrow("Erro ao excluir.");
  });
});
