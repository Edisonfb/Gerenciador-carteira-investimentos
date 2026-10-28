import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { gerarConviteInvestidor, validarEmailConvite } from "../../frontend/src/services/conviteInvestidorService";

beforeEach(() => {
  vi.stubGlobal("localStorage", { getItem: () => "sessao-de-teste" });
});
afterEach(() => vi.unstubAllGlobals());

describe("Convite de investidor por e-mail", () => {
  it("envia somente o e-mail normalizado com a sessão do analista", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ id_investidor: 11, id_usuario: 22, email: "cliente@example.test", primeiro_acesso_concluido: false, email_acesso_enviado: true }), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    const convite = await gerarConviteInvestidor(" Cliente@Example.Test ");
    expect(convite.email_acesso_enviado).toBe(true);
    const [url, opcoes] = fetchMock.mock.calls[0];
    expect(url).toBe("http://127.0.0.1:8000/investors");
    expect(opcoes.method).toBe("POST");
    expect(opcoes.headers.Authorization).toBe("Bearer sessao-de-teste");
    expect(JSON.parse(opcoes.body)).toEqual({ email: "cliente@example.test" });
  });
  it.each(["", "   ", "cliente#example.test", "cliente @example.test"])("não envia convite com e-mail inválido: %s", async email => {
    const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
    expect(validarEmailConvite(email)).not.toBeNull();
    await expect(gerarConviteInvestidor(email)).rejects.toThrow();
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it("recusa o envio sem sessão", async () => {
    vi.stubGlobal("localStorage", { getItem: () => null });
    const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
    await expect(gerarConviteInvestidor("cliente@example.test")).rejects.toThrow("Sua sessão expirou");
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it("mostra a mensagem da API para um e-mail já existente", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Já existe um usuário com este e-mail." }), { status: 400 })));
    await expect(gerarConviteInvestidor("cliente@example.test")).rejects.toThrow("Já existe um usuário com este e-mail.");
  });
  it("preserva o indicador de envio sem afirmar sucesso indevido", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ id_investidor: 11, id_usuario: 22, email: "cliente@example.test", primeiro_acesso_concluido: false, email_acesso_enviado: false }), { status: 201 })));
    expect((await gerarConviteInvestidor("cliente@example.test")).email_acesso_enviado).toBe(false);
  });
  it("informa falha de SMTP/servidor sem presumir que o convite foi entregue", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("Internal Server Error", { status: 500 })));
    await expect(gerarConviteInvestidor("cliente@example.test")).rejects.toThrow("Verifique o envio de e-mail no backend");
  });
});
