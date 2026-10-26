import { beforeEach, expect, test, vi } from "vitest";

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  vi.resetModules();
  fetchMock = vi.fn();
  vi.stubGlobal("fetch", fetchMock);
});

function dadosInvestidor() {
  return {
    idAnalistaResponsavel: 1,
    nome: "Ana",
    sobrenome: "Silva",
    email: "ana@email.com",
    cpf: "123.456.789-01",
    celular: "(51) 99999-9999",
    rua: "Rua A",
    numero: "10",
    bairro: "Centro",
    cep: "90000-000",
    cidade: "Porto Alegre",
    uf: "RS",
    perfil: "investidor" as const,
    status: "ativo" as const,
  };
}

test("lista somente os investidores do analista responsavel", async () => {
  const { buscarInvestidoresPorAnalista } = await import(
    "../../frontend/src/services/investidorService"
  );

  const investidores = buscarInvestidoresPorAnalista(1);

  expect(investidores.map((investidor) => investidor.email)).toEqual([
    "lucas.mendes@email.com",
    "camila.oliveira@email.com",
    "bruno.ferreira@email.com",
  ]);
  expect(buscarInvestidoresPorAnalista(99)).toHaveLength(1);
});

test("atualiza a conta do investidor sem trocar o id nem o perfil", async () => {
  const { atualizarInvestidor, buscarInvestidorPorId } = await import(
    "../../frontend/src/services/investidorService"
  );

  const atualizado = atualizarInvestidor(1, {
    nome: "Lucas Souza",
    email: "lucas.souza@email.com",
  });

  expect(atualizado).toMatchObject({
    id: 1,
    nome: "Lucas Souza",
    email: "lucas.souza@email.com",
    perfil: "investidor",
    idAnalistaResponsavel: 1,
  });
  expect(buscarInvestidorPorId(1)?.nome).toBe("Lucas Souza");
  expect(atualizarInvestidor(999, { nome: "Ninguem" })).toBeUndefined();
});

test("cadastro envia os dados limpos e devolve o id criado pela api", async () => {
  fetchMock.mockResolvedValue({
    ok: true,
    json: async () => ({
      id_investidor: 15,
      cpf: "12345678901",
      telefone: "51999999999",
    }),
  });

  const { criarInvestidor } = await import("../../frontend/src/services/investidorService");
  const criado = await criarInvestidor(dadosInvestidor());

  expect(criado).toMatchObject({
    id: 15,
    nome: "Ana",
    cpf: "12345678901",
    celular: "51999999999",
    perfil: "investidor",
  });
  expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/investors", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id_analista_responsavel: 1,
      nome: "Ana",
      sobrenome: "Silva",
      email: "ana@email.com",
      cpf: "12345678901",
      telefone: "51999999999",
      cep: "90000000",
      uf: "RS",
      cidade: "Porto Alegre",
      bairro: "Centro",
      logradouro: "Rua A",
      numero: "10",
    }),
  });
});

test("cadastro falha quando a api recusa o investidor", async () => {
  fetchMock.mockResolvedValue({ ok: false, json: async () => ({}) });

  const { criarInvestidor } = await import("../../frontend/src/services/investidorService");

  await expect(criarInvestidor(dadosInvestidor())).rejects.toThrow(
    "Não foi possível cadastrar o investidor.",
  );
});
