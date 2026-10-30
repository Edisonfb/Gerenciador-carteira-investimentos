// Dados falsos usados nos testes da Sprint 2.
import type { AtivoConfigurado, AtivoDisponivel } from "../../../frontend/src/types/configuracaoCarteira";

export const CATALOGO: AtivoDisponivel[] = [
  { ticker: "AALR3", setor: "Saúde", ativo: true },
  { ticker: "ABEV3", setor: "Consumo não Cíclico", ativo: true },
  { ticker: "BBDC3", setor: "Financeiro", ativo: true },
  { ticker: "CRFB3", setor: "Consumo não Cíclico", ativo: true },
  { ticker: "EGIE3", setor: "Utilidade Pública", ativo: true },
  { ticker: "ITUB3", setor: "Financeiro", ativo: true },
  { ticker: "ITUB4", setor: "Financeiro", ativo: true },
];

export function configurado(ticker: string, objetivo: string, quantidade = 0): AtivoConfigurado {
  const ativo = CATALOGO.find(a => a.ticker === ticker)!;
  return { ...ativo, objetivo, quantidade };
}

// Carteira "Aposentadoria" do exemplo: 10% + 10% + 40% + 20% + 20% = 100%.
export const APOSENTADORIA = [
  configurado("ABEV3", "10"), configurado("BBDC3", "10"), configurado("CRFB3", "40"),
  configurado("EGIE3", "20"), configurado("ITUB4", "20"),
];

// Respostas da API para a carteira 1 ja salva (ITUB4 com quantidade 25).
export const API_CARTEIRA_1 = {
  "GET /portfolios": [{ id_carteira: 1, nome: "Aposentadoria", ativa: true }, { id_carteira: 2, nome: "Carro", ativa: true }],
  "GET /portfolios/1": { id_carteira: 1, nome: "Aposentadoria", ativa: true },
  "GET /assets": CATALOGO.map(a => ({ ...a, nome: "", subsetor: "", segmento: "", data_criacao: "2026-10-29T00:00:00" })),
  "GET /assets/carteira/1": [
    { ticker: "ABEV3", id_carteira: 1, quantidade: 0, objetivo_percentual: "10.00" },
    { ticker: "BBDC3", id_carteira: 1, quantidade: 0, objetivo_percentual: "10.00" },
    { ticker: "CRFB3", id_carteira: 1, quantidade: 0, objetivo_percentual: "40.00" },
    { ticker: "EGIE3", id_carteira: 1, quantidade: 0, objetivo_percentual: "20.00" },
    { ticker: "ITUB4", id_carteira: 1, quantidade: 25, objetivo_percentual: "20.00" },
  ],
};
