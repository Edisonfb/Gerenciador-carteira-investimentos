import { obterTokenAcesso } from "./autenticacaoService";
import type { AtivoDisponivel } from "../types/configuracaoCarteira";

const API_BASE = "http://127.0.0.1:8000";

async function consultar(caminho: string, signal?: AbortSignal): Promise<unknown> {
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  let resposta: Response;
  try {
    resposta = await fetch(`${API_BASE}${caminho}`, { headers: { Authorization: `Bearer ${token}` }, signal });
  } catch (erro) {
    if (erro instanceof Error && erro.name === "AbortError") throw erro;
    throw new Error("Não foi possível consultar a API. Verifique se o backend está iniciado.", { cause: erro });
  }
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(typeof erro?.detail === "string" ? erro.detail : "Não foi possível carregar os dados.");
  }
  return resposta.json();
}

export async function consultarAtivosAceitos(signal?: AbortSignal): Promise<AtivoDisponivel[]> {
  const dados = await consultar("/assets", signal);
  if (!Array.isArray(dados) || dados.some(a => typeof a?.ticker !== "string" || !a.ticker.trim() || typeof a?.setor !== "string" || typeof a?.ativo !== "boolean")) throw new Error("A API retornou um catálogo de ativos inválido.");
  return (dados as AtivoDisponivel[]).filter(ativo => ativo.ativo);
}

export async function consultarNomesCarteiras(signal?: AbortSignal): Promise<string[]> {
  const dados = await consultar("/portfolios", signal);
  if (!Array.isArray(dados) || dados.some(c => typeof c?.nome !== "string")) throw new Error("Não foi possível conferir os nomes das carteiras existentes.");
  return dados.map(carteira => carteira.nome as string);
}
