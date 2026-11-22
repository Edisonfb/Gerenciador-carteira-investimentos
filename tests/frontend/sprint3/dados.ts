// Dados falsos usados nos testes da Sprint 3: carteira "Aposentadoria" das historias (17/11/2026).

export const CATALOGO = [
  { ticker: "ABEV3", setor: "Consumo não Cíclico", ativo: true },
  { ticker: "BBDC4", setor: "Financeiro", ativo: true },
  { ticker: "EGIE3", setor: "Utilidade Pública", ativo: true },
  { ticker: "ITUB4", setor: "Financeiro", ativo: true },
  { ticker: "PETR4", setor: "Energia", ativo: true },
].map(a => ({ ...a, nome: "", subsetor: "", segmento: "", data_criacao: "2026-11-01T00:00:00" }));

// Valores como a API devolve (Decimal vira texto no JSON).
export function transacao(id: number, tipo: "compra" | "venda", ticker: string, quantidade: number, valor: string, data = "2026-11-17T23:29:00") {
  const preco = (Number(valor) / quantidade).toFixed(2);
  return { id_transacao: id, id_carteira: 1, nome_carteira: "Aposentadoria", ticker, tipo, quantidade, preco_unitario: preco, valor_total: valor, data_transacao: data };
}

// Historico da US 12.1, do mais recente para o mais antigo (ordem da API).
export const HISTORICO_APOSENTADORIA = [
  transacao(4, "compra", "ITUB4", 100, "4089.00", "2026-11-17T16:00:00"),
  transacao(3, "venda", "ITUB4", 100, "4089.00", "2026-11-17T15:00:00"),
  transacao(2, "compra", "EGIE3", 100, "2583.00", "2026-11-17T14:00:00"),
  transacao(1, "compra", "ITUB4", 200, "8178.00", "2026-11-17T13:00:00"),
];

// Carteira 1 com ITUB4 em 300 acoes (depois da compra da US 11.1): patrimonio de R$ 17.884,00.
export const API_APOSENTADORIA = {
  "GET /portfolios": [{ id_carteira: 1, nome: "Aposentadoria", ativa: true }, { id_carteira: 2, nome: "Casa", ativa: true }],
  "GET /portfolios/1": { id_carteira: 1, id_investidor: 1, nome: "Aposentadoria", ativa: true, data_criacao: "2026-11-01T00:00:00" },
  "GET /assets": CATALOGO,
  "GET /assets/carteira/1": [
    { ticker: "ABEV3", id_carteira: 1, quantidade: 100, objetivo_percentual: "50.00" },
    { ticker: "BBDC4", id_carteira: 1, quantidade: 100, objetivo_percentual: "20.00" },
    { ticker: "EGIE3", id_carteira: 1, quantidade: 100, objetivo_percentual: "20.00" },
    { ticker: "ITUB4", id_carteira: 1, quantidade: 300, objetivo_percentual: "10.00" },
  ],
  "GET /portfolios/1/summary": {
    id_carteira: 1, patrimonio_total: "17884.00", ativos: [
      { ticker: "ABEV3", quantidade: 100, cotacao: "15.93", data_atualizacao: "2026-11-17T23:29:00", valor_atual: "1593.00", participacao_percentual: "8.91" },
      { ticker: "BBDC4", quantidade: 100, cotacao: "14.41", data_atualizacao: "2026-11-17T23:29:00", valor_atual: "1441.00", participacao_percentual: "8.06" },
      { ticker: "EGIE3", quantidade: 100, cotacao: "25.83", data_atualizacao: "2026-11-17T23:29:00", valor_atual: "2583.00", participacao_percentual: "14.44" },
      { ticker: "ITUB4", quantidade: 300, cotacao: "40.89", data_atualizacao: "2026-11-17T23:29:00", valor_atual: "12267.00", participacao_percentual: "68.59" },
    ],
  },
  "GET /quotes/ITUB4": { ticker: "ITUB4", preco: "40.89", data_atualizacao: "2026-11-17T23:29:00" },
  "GET /transactions?id_carteira=1": HISTORICO_APOSENTADORIA,
  "GET /transactions?id_carteira=2": [],
};
