import { expect, it } from "vitest";
import { distribuicaoObjetivos, filtrarAtivosCarteira } from "../../frontend/src/lib/detalheCarteira";
import type { AtivoConfigurado } from "../../frontend/src/types/configuracaoCarteira";
const ativos: AtivoConfigurado[] = [
  { ticker: "ITUB4", setor: "Financeiro", ativo: true, quantidade: 12, objetivo: "30.50" },
  { ticker: "ITUB3", setor: "Financeiro", ativo: false, quantidade: 5, objetivo: "20,50" },
  { ticker: "EGIE3", setor: "Energia", ativo: true, quantidade: 0, objetivo: "49" },
];
it("busca somente nos ativos vinculados por código parcial e setor", () => {
  expect(filtrarAtivosCarteira(ativos, " itub ", "Financeiro").map(a => a.ticker)).toEqual(["ITUB4", "ITUB3"]);
  expect(filtrarAtivosCarteira(ativos, "ITUB", "Energia")).toEqual([]);
});
it("não oculta posição de ativo desativado", () => {
  expect(filtrarAtivosCarteira(ativos, "ITUB3", "")[0].quantidade).toBe(5);
});
it("retorna vazio quando não encontra um código", () => {
  expect(filtrarAtivosCarteira(ativos, "QQQQ9", "")).toEqual([]);
});
it("gráfico representa os objetivos salvos, sem inventar patrimônio", () => {
  const grafico = distribuicaoObjetivos(ativos);
  expect(grafico.total).toBe(100);
  expect(grafico.fatias.map(f => [f.inicio, f.fim])).toEqual([[0, 30.5], [30.5, 51], [51, 100]]);
  expect(ativos.map(a => a.quantidade)).toEqual([12, 5, 0]);
});
it("não normaliza para 100 uma composição incompleta", () => {
  expect(distribuicaoObjetivos([ativos[0]]).total).toBe(30.5);
  expect(distribuicaoObjetivos([])).toEqual({ fatias: [], total: 0 });
});
