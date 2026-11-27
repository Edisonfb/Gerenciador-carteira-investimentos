import { obterTokenAcesso } from "./autenticacaoService";
import type { Distribuicao, Simulacao, ValoresPagos } from "../types/simulacaoAporte";

/** Envia simulacao ou confirmacao a API autenticada, sem calcular recomendacoes no front. */
async function enviar(caminho: string, dados?: object, signal?: AbortSignal): Promise<unknown> {
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  let resposta: Response;
  try {
    resposta = await fetch(`http://127.0.0.1:8000${caminho}`, {
      method: dados ? "POST" : "GET", signal,
      headers: { Authorization: `Bearer ${token}`, ...(dados ? { "Content-Type": "application/json" } : {}) },
      ...(dados ? { body: JSON.stringify(dados) } : {}),
    });
  } catch {
    throw new Error("Não foi possível confirmar a resposta. Confira o histórico antes de repetir um registro.");
  }
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(typeof erro?.detail === "string" ? erro.detail : `A API respondeu com erro ${resposta.status}.`);
  }
  return resposta.json();
}

/** Consulta cotacoes e limites calculados pelo backend antes de informar o aporte. */
export async function consultarMinimosAporte(id: number, distribuicao: Distribuicao, signal?: AbortSignal): Promise<Simulacao> {
  return await enviar(`/portfolios/${id}/contribution-options?distribuicao=${distribuicao}`, undefined, signal) as Simulacao;
}

/** Consulta compras sugeridas; nenhuma transacao e gravada. */
export async function simularAporte(id: number, aporte: string, distribuicao: Distribuicao): Promise<Simulacao> {
  return await enviar(`/portfolios/${id}/contribution-simulation`, { aporte, distribuicao }) as Simulacao;
}

/** Confirma todas as compras recomendadas em uma unica transacao do banco. */
export async function registrarRecomendacao(simulacao: Simulacao, valoresPagos?: ValoresPagos): Promise<void> {
  await enviar("/transactions/recommended-purchases", { compras: simulacao.ativos
    .filter(a => a.quantidade_sugerida > 0).map(a => ({ id_carteira: simulacao.id_carteira,
      ticker: a.ticker, tipo: "compra", quantidade: a.quantidade_sugerida, preco_unitario: a.cotacao,
      ...(valoresPagos ? { valor_total_pago: valoresPagos[a.ticker] } : {}) })) });
}
