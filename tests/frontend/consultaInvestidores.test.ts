import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { combinarContasEConvites, filtrarContasInvestidores, listarContasInvestidores } from "../../frontend/src/services/consultaInvestidoresService";
import type { ContaInvestidorConsulta } from "../../frontend/src/services/consultaInvestidoresService";

beforeEach(() => vi.stubGlobal("localStorage", { getItem: () => "sessao-analista-teste" }));
afterEach(() => vi.unstubAllGlobals());

const contas: ContaInvestidorConsulta[] = [
  { id_usuario: 25, email: "marina@example.test", ativo: true, convite: null, cadastro: null },
  { id_usuario: 26, email: "carlos@example.test", ativo: false, convite: null, cadastro: null },
];

describe("Consulta de todos os investidores", () => {
  it("usa a API existente, seleciona investidores e não envia filtro de analista", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify([
      { id_usuario: 1, email: "analista@example.test", tipo_usuario: "analista", ativo: true },
      { id_usuario: 25, email: "marina@example.test", tipo_usuario: "investidor", ativo: true },
      { id_usuario: 26, email: "carlos@example.test", tipo_usuario: "INVESTIDOR", ativo: false },
    ])));
    vi.stubGlobal("fetch", fetchMock);
    const resultado = await listarContasInvestidores();
    expect(resultado.map(c => c.id_usuario)).toEqual([26, 25]);
    expect(fetchMock.mock.calls[0][0]).toBe("http://127.0.0.1:8000/auth/usuarios");
    expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe("Bearer sessao-analista-teste");
    expect(resultado.every(c => c.convite === null && c.cadastro === null)).toBe(true);
  });
  it("busca parcialmente sem diferenciar maiúsculas e filtra ativa/inativa", () => {
    expect(filtrarContasInvestidores(contas, " MARINA ")).toEqual([contas[0]]);
    expect(filtrarContasInvestidores(contas, "example.test", "inativas")).toEqual([contas[1]]);
    expect(filtrarContasInvestidores(contas, "inexistente")).toEqual([]);
  });
  it("conta ativa não significa que o cadastro está concluído ou que o convite foi enviado", () => {
    const resultado = combinarContasEConvites(contas, []);
    expect(resultado.find(c => c.id_usuario === 25)).toMatchObject({ ativo: true, convite: null, cadastro: null });
  });
  it("combina o convite pelo id_usuario e não pelo id_investidor, sem duplicar contas", () => {
    const resultado = combinarContasEConvites(contas, [{ id_investidor: 3, id_usuario: 25, email: "marina@example.test", primeiro_acesso_concluido: false, email_acesso_enviado: false }]);
    expect(resultado).toHaveLength(2);
    expect(resultado.find(c => c.id_usuario === 25)).toMatchObject({ ativo: true, convite: "nao_confirmado", cadastro: "pendente" });
    expect(contas[0].cadastro).toBeNull();
  });
  it("não inventa situação ativa para uma conta conhecida somente pelo convite", () => {
    const resultado = combinarContasEConvites([], [{ id_investidor: 3, id_usuario: 25, email: "marina@example.test", primeiro_acesso_concluido: false, email_acesso_enviado: true }]);
    expect(resultado[0]).toMatchObject({ ativo: null, convite: "enviado", cadastro: "pendente" });
    expect(filtrarContasInvestidores(resultado, "", "ativas")).toEqual([]);
  });
  it("expõe falha de consulta e não trata como lista vazia", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Sessão inválida" }), { status: 401 })));
    await expect(listarContasInvestidores()).rejects.toThrow("Sessão inválida");
  });
  it("rejeita respostas incompatíveis", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify([{ email: "incompleto@example.test" }]))));
    await expect(listarContasInvestidores()).rejects.toThrow("lista de contas inválida");
  });
  it("aceita uma consulta vazia real", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("[]")));
    expect(await listarContasInvestidores()).toEqual([]);
  });
});
