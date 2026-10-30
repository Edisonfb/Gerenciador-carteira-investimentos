// US 8.1 - Inclusão de ativo na carteira / US 8.2 - Busca e filtro de ativos por setor
import { describe, expect, test } from "vitest";
import { ERRO_CODIGO, filtrarAtivos, percentualEmCentesimos, validarInclusao } from "../../../frontend/src/lib/configuracaoCarteira";
import { filtrarAtivosCarteira } from "../../../frontend/src/lib/detalheCarteira";
import { APOSENTADORIA, CATALOGO, configurado } from "./catalogo";

// Carteira do cenário 2 da US 8.1: ABEV3, BBDC3, CRFB3 e EGIE3.
const SEM_ITUB4 = APOSENTADORIA.filter(a => a.ticker !== "ITUB4");

describe("US 8.1 - Inclusão de ativo", () => {
  test("Cenário 1: ITUB4 com objetivo 20% é aceito", () => {
    expect(validarInclusao("ITUB4", "20", CATALOGO, SEM_ITUB4)).toBeNull();
  });

  test("Cenário 1: código em minúsculas também é aceito", () => {
    expect(validarInclusao("itub4", "20", CATALOGO, SEM_ITUB4)).toBeNull();
  });

  test("Cenário 2: código com caractere especial (ITUB-4)", () => {
    expect(validarInclusao("ITUB-4", "20", CATALOGO, SEM_ITUB4)).toBe(ERRO_CODIGO);
    expect(ERRO_CODIGO).toBe("Código de ativo inválido. Use quatro letras e um número, sem espaços ou caracteres especiais");
  });

  test("Cenário 2: código com espaço (ITUB 4)", () => {
    expect(validarInclusao("ITUB 4", "20", CATALOGO, SEM_ITUB4)).toBe(ERRO_CODIGO);
  });

  test("Cenário 3: código com apenas três letras (ITU4)", () => {
    expect(validarInclusao("ITU4", "20", CATALOGO, SEM_ITUB4)).toBe(ERRO_CODIGO);
  });

  test("Cenário 4: formato correto, mas fora da lista (ZZZZ9)", () => {
    expect(validarInclusao("ZZZZ9", "20", CATALOGO, SEM_ITUB4)).toBe("Ativo não encontrado na lista de ativos aceitos");
  });

  test("Cenário 5: ativo já incluído na mesma carteira", () => {
    expect(validarInclusao("ITUB4", "10", CATALOGO, APOSENTADORIA)).toBe("Ativo já incluído nesta carteira");
  });

  test("objetivo zero ou acima de 100% não é aceito", () => {
    expect(validarInclusao("ITUB4", "0", CATALOGO, SEM_ITUB4)).toContain("Informe um objetivo maior que zero");
    expect(validarInclusao("ITUB4", "101", CATALOGO, SEM_ITUB4)).toContain("Informe um objetivo maior que zero");
  });

  test("percentual aceita vírgula e até duas casas decimais", () => {
    expect(percentualEmCentesimos("20")).toBe(2000);
    expect(percentualEmCentesimos("12,5")).toBe(1250);
    expect(percentualEmCentesimos("33.33")).toBe(3333);
    expect(percentualEmCentesimos("10.555")).toBeNull();
  });
});

describe("US 8.2 - Busca e filtro (cadastro/edição da carteira)", () => {
  test("Cenário 1: busca 'ITUB' mostra ITUB3 e ITUB4 como ativos distintos", () => {
    expect(filtrarAtivos(CATALOGO, "ITUB", "").map(a => a.ticker)).toEqual(["ITUB3", "ITUB4"]);
  });

  test("Cenário 2: filtro de setor 'Financeiro'", () => {
    const encontrados = filtrarAtivos(CATALOGO, "", "Financeiro");
    expect(encontrados.map(a => a.ticker)).toEqual(["BBDC3", "ITUB3", "ITUB4"]);
    expect(encontrados.every(a => a.setor === "Financeiro")).toBe(true);
  });

  test("Cenário 3: busca sem resultados (QQQQ9)", () => {
    expect(filtrarAtivos(CATALOGO, "QQQQ9", "")).toEqual([]);
  });

  test("ativos desativados não aparecem na busca", () => {
    expect(filtrarAtivos([...CATALOGO, { ticker: "OIBR3", setor: "Comunicações", ativo: false }], "OIBR", "")).toEqual([]);
  });
});

describe("US 8.2 - Busca e filtro (visualização da carteira, obrigatório)", () => {
  const carteira = [...APOSENTADORIA, configurado("ITUB3", "0")];

  test("Cenário 1: busca 'ITUB' no detalhe da carteira", () => {
    expect(filtrarAtivosCarteira(carteira, "itub", "").map(a => a.ticker)).toEqual(["ITUB4", "ITUB3"]);
  });

  test("Cenário 2: filtro por setor no detalhe da carteira", () => {
    expect(filtrarAtivosCarteira(carteira, "", "Financeiro").map(a => a.ticker)).toEqual(["BBDC3", "ITUB4", "ITUB3"]);
  });

  test("Cenário 3: busca sem resultados no detalhe", () => {
    expect(filtrarAtivosCarteira(carteira, "QQQQ9", "")).toEqual([]);
  });
});
