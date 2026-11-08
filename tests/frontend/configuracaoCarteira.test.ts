import { describe, expect, it } from "vitest";
import { ERRO_CODIGO, filtrarAtivos, percentualEmCentesimos, validarConfiguracao, validarInclusao } from "../../frontend/src/lib/configuracaoCarteira";
import type { AtivoConfigurado, AtivoDisponivel } from "../../frontend/src/types/configuracaoCarteira";

// Fixtures somente de teste; nenhum dado é incluído no catálogo da aplicação.
const catalogo: AtivoDisponivel[] = [
  { ticker: "ITUB4", setor: "Financeiro", ativo: true },
  { ticker: "ITUB3", setor: "Financeiro", ativo: true },
  { ticker: "EGIE3", setor: "Energia", ativo: true },
  { ticker: "ABEV3", setor: "Consumo", ativo: false },
];
const configurar = (indice: number, objetivo: string): AtivoConfigurado => ({ ...catalogo[indice], objetivo, quantidade: 0 });

describe("Configuração da carteira", () => {
  it("exige o nome e detecta duplicidade do mesmo investidor", () => {
    expect(validarConfiguracao("   ", [configurar(0, "100")])).toBe("Informe o nome da carteira");
    expect(validarConfiguracao(" Aposentadoria ", [configurar(0, "100")], ["aposentadoria"])).toBe("Já existe uma carteira com este nome");
  });
  it.each(["ITUB-4", "ITU4", "ITUB4 ", " ITUB4", "ITUB44"])("rejeita formato de código %s", codigo => {
    expect(validarInclusao(codigo, "20", catalogo, [])).toBe(ERRO_CODIGO);
  });
  it("rejeita código desconhecido e ativo inativo", () => {
    expect(validarInclusao("ZZZZ9", "20", catalogo, [])).toBe("Ativo não encontrado na lista de ativos aceitos");
    expect(validarInclusao("ABEV3", "20", catalogo, [])).toBe("Ativo não encontrado na lista de ativos aceitos");
  });
  it("impede duplicidade, mas permite papéis diferentes da mesma empresa", () => {
    expect(validarInclusao("ITUB4", "20", catalogo, [configurar(0, "10")])).toBe("Ativo já incluído nesta carteira");
    expect(validarInclusao("ITUB3", "20", catalogo, [configurar(0, "10")])).toBeNull();
  });
  it("combina busca parcial com filtro por setor", () => {
    expect(filtrarAtivos(catalogo, "itub", "Financeiro").map(a => a.ticker)).toEqual(["ITUB4", "ITUB3"]);
    expect(filtrarAtivos(catalogo, "ITUB", "Energia")).toEqual([]);
    expect(filtrarAtivos(catalogo, "QQQQ9", "")).toEqual([]);
  });
  it.each(["", "-1", "100.01", "101", "abc", "20%", "0.001"])("rejeita percentual inválido %s", valor => {
    expect(percentualEmCentesimos(valor)).toBeNull();
  });
  it("aceita vírgula, ponto e soma decimal exata", () => {
    expect(percentualEmCentesimos("33,33")).toBe(3333);
    expect(validarConfiguracao("Carro", [configurar(0, "33.33"), configurar(1, "33,33"), configurar(2, "33.34")])).toBeNull();
  });
  it("rejeita carteira vazia ou campo objetivo vazio", () => {
    expect(validarConfiguracao("Carro", [])).toBe("Inclua pelo menos um ativo na carteira");
    expect(validarConfiguracao("Carro", [configurar(0, "")])).not.toBeNull();
  });
  it("valida a redistribuição após remover um ativo", () => {
    expect(validarConfiguracao("Carro", [configurar(0, "80")])).toBe("O objetivo total da carteira deve somar 100%. Soma atual: 80%");
    expect(validarConfiguracao("Carro", [configurar(0, "100")])).toBeNull();
  });
});
