import { obterTokenAcesso } from "./autenticacaoService";

const API_BASE = "http://127.0.0.1:8000";

export interface CarteiraTransacao {
  id_carteira: number;
  nome: string;
  ativa: boolean;
}

export interface AtivoCarteiraTransacao {
  ticker: string;
  id_carteira: number;
  quantidade: number;
  objetivo_percentual: number;
}

export interface AtivoCatalogoTransacao {
  ticker: string;
  setor: string;
  ativo: boolean;
}

export interface CotacaoTransacao {
  ticker: string;
  preco: number;
  data_atualizacao: string;
}

export interface TransacaoHistorico {
  id_transacao: number;
  id_carteira: number | null;
  nome_carteira: string;
  ticker: string;
  tipo: "compra" | "venda";
  quantidade: number;
  preco_unitario: number;
  valor_total: number;
  data_transacao: string;
}

function token(): string {
  const valor = obterTokenAcesso();
  if (!valor) throw new Error("Sua sessão expirou. Entre novamente.");
  return valor;
}

async function requisitar<T>(caminho: string, opcoes: RequestInit = {}): Promise<T> {
  let resposta: Response;
  try {
    resposta = await fetch(`${API_BASE}${caminho}`, {
      ...opcoes,
      headers: { Authorization: `Bearer ${token()}`, ...(opcoes.body ? { "Content-Type": "application/json" } : {}), ...opcoes.headers },
    });
  } catch (erro) {
    if (erro instanceof Error && erro.name === "AbortError") throw erro;
    throw new Error("Não foi possível conectar à API. Verifique se o backend está iniciado.", { cause: erro });
  }
  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => null);
    throw new Error(typeof corpo?.detail === "string" ? corpo.detail : `A API respondeu com erro ${resposta.status}.`);
  }
  if (resposta.status === 204) return undefined as T;
  return resposta.json() as Promise<T>;
}

export function listarCarteirasParaTransacao(signal?: AbortSignal): Promise<CarteiraTransacao[]> {
  return requisitar("/portfolios", { signal });
}

export function listarAtivosDaCarteira(id: number, signal?: AbortSignal): Promise<AtivoCarteiraTransacao[]> {
  return requisitar(`/assets/carteira/${id}`, { signal });
}

export function listarCatalogoTransacao(signal?: AbortSignal): Promise<AtivoCatalogoTransacao[]> {
  return requisitar("/assets", { signal });
}

export function consultarCotacaoTransacao(ticker: string, signal?: AbortSignal): Promise<CotacaoTransacao> {
  return requisitar(`/quotes/${encodeURIComponent(ticker)}`, { signal });
}

export function registrarTransacao(dados: {
  id_carteira: number;
  ticker: string;
  tipo: "compra" | "venda";
  quantidade: number;
  preco_unitario: number;
}): Promise<TransacaoHistorico> {
  return requisitar("/transactions", { method: "POST", body: JSON.stringify(dados) });
}

export function listarHistoricoTransacoes(idCarteira: number, signal?: AbortSignal): Promise<TransacaoHistorico[]> {
  return requisitar(`/transactions?id_carteira=${encodeURIComponent(idCarteira)}`, { signal });
}
