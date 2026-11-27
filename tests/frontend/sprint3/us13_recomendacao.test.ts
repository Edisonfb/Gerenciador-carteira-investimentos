import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { consultarMinimosAporte, registrarRecomendacao, simularAporte } from "../../../frontend/src/services/simulacaoAporteService";
import type { Simulacao } from "../../../frontend/src/types/simulacaoAporte";
import { prepararNavegador, resposta, corpo, chamadas } from "../apoio";

let navegador: ReturnType<typeof prepararNavegador>;
beforeEach(() => { navegador = prepararNavegador(); navegador.armazenamento.set("access_token", "teste"); });
afterEach(() => vi.unstubAllGlobals());

test("a simulacao envia somente aporte e modo e nao registra compras", async () => {
  navegador.fetchFalso.mockResolvedValue(resposta({ ativos: [] }));
  await simularAporte(2, "3500.00", "linear");
  expect(chamadas(navegador.fetchFalso)).toEqual(["POST /portfolios/2/contribution-simulation"]);
  expect(corpo(navegador.fetchFalso, 0)).toEqual({ aporte: "3500.00", distribuicao: "linear" });
});

test("confirmacao envia em conjunto somente compras com quantidade sugerida", async () => {
  navegador.fetchFalso.mockResolvedValue(resposta([]));
  const simulacao = { id_carteira: 2, ativos: [
    { ticker: "ABEV3", quantidade_sugerida: 200, cotacao: "10.00" },
    { ticker: "CRFB3", quantidade_sugerida: 100, cotacao: "10.00" },
    { ticker: "ITUB4", quantidade_sugerida: 0, cotacao: "40.89" },
  ] } as Simulacao;
  await registrarRecomendacao(simulacao);
  expect(chamadas(navegador.fetchFalso)).toEqual(["POST /transactions/recommended-purchases"]);
  expect(corpo(navegador.fetchFalso, 0).compras).toEqual([
    { id_carteira: 2, ticker: "ABEV3", tipo: "compra", quantidade: 200, preco_unitario: "10.00" },
    { id_carteira: 2, ticker: "CRFB3", tipo: "compra", quantidade: 100, preco_unitario: "10.00" },
  ]);
});

test("erro de negocio da API aparece na simulacao", async () => {
  navegador.fetchFalso.mockResolvedValue(resposta({ detail: "Carteira não encontrada." }, 404));
  await expect(simularAporte(2, "3000", "balanceamento")).rejects.toThrow("Carteira não encontrada.");
});

test("sem sessao nao envia simulacao", async () => {
  navegador.armazenamento.delete("access_token");
  await expect(simularAporte(2, "3000", "balanceamento")).rejects.toThrow("Sua sessão expirou.");
  expect(navegador.fetchFalso).not.toHaveBeenCalled();
});

test("consulta os custos minimos antes de digitar aporte sem enviar compras", async () => {
  navegador.fetchFalso.mockResolvedValue(resposta({ aporte_minimo: "4256.00", ativos: [] }));
  const dados = await consultarMinimosAporte(2, "linear");
  expect(chamadas(navegador.fetchFalso)).toEqual(["GET /portfolios/2/contribution-options?distribuicao=linear"]);
  expect(dados.aporte_minimo).toBe("4256.00");
});

test("envia o total real confirmado sem substituir pela cotacao sugerida", async () => {
  navegador.fetchFalso.mockResolvedValue(resposta([]));
  const simulacao = { id_carteira: 2, ativos: [
    { ticker: "AERI3", quantidade_sugerida: 300, cotacao: "1.75" },
  ] } as Simulacao;
  await registrarRecomendacao(simulacao, { AERI3: "532.00" });
  expect(corpo(navegador.fetchFalso, 0).compras).toEqual([
    { id_carteira: 2, ticker: "AERI3", tipo: "compra", quantidade: 300,
      preco_unitario: "1.75", valor_total_pago: "532.00" },
  ]);
});
