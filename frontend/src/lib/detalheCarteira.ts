import type { AtivoConfigurado } from "../types/configuracaoCarteira";
import { percentualEmCentesimos } from "./configuracaoCarteira";

export function filtrarAtivosCarteira(ativos: AtivoConfigurado[], busca: string, setor: string): AtivoConfigurado[] {
  const termo = busca.trim().toUpperCase();
  // Inclui posicoes de ativos desativados: continuam pertencendo a carteira.
  return ativos.filter(a => a.ticker.toUpperCase().includes(termo) && (!setor || a.setor === setor));
}

const CORES = ["#0f172a", "#059669", "#0284c7", "#7c3aed", "#d97706", "#db2777", "#475569", "#0891b2"];
export function distribuicaoObjetivos(ativos: AtivoConfigurado[]) {
  let inicio = 0;
  const fatias = ativos.map((ativo, indice) => {
    const valor = percentualEmCentesimos(ativo.objetivo) ?? 0;
    const fatia = { ticker: ativo.ticker, cor: CORES[indice % CORES.length], inicio, fim: inicio + valor / 100, percentual: valor / 100 };
    inicio = fatia.fim;
    return fatia;
  });
  return { fatias, total: inicio };
}
