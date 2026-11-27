/** Valores decimais da API sao recebidos como strings para preservar centavos. */
export interface AtivoSimulado {
  ticker: string;
  cotacao: string;
  quantidade_sugerida: number;
  custo_sugerido: string;
  participacao_atual: string;
  participacao_projetada: string;
  distancia_atual: string;
  distancia_projetada: string;
  objetivo_percentual: string;
  custo_lote: string;
  aporte_minimo_ativo: string | null;
}
export interface Simulacao {
  id_carteira: number;
  aporte: string;
  patrimonio_atual: string;
  patrimonio_projetado: string;
  valor_investido: string;
  saldo_restante: string;
  ativos: AtivoSimulado[];
  aporte_minimo: string | null;
}
export type Distribuicao = "balanceamento" | "linear";

/** Totais efetivos informados na conferencia das compras, em reais. */
export type ValoresPagos = Record<string, string>;
