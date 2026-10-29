import { obterTokenAcesso } from "./autenticacaoService";
import { percentualEmCentesimos, validarConfiguracao } from "../lib/configuracaoCarteira";
import type { AtivoConfigurado, AtivoDisponivel } from "../types/configuracaoCarteira";

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

export interface CarteiraResumo {
  id_carteira: number;
  nome: string;
  ativa: boolean;
}

export async function consultarCarteiras(signal?: AbortSignal): Promise<CarteiraResumo[]> {
  const dados = await consultar("/portfolios", signal);
  if (!Array.isArray(dados) || dados.some(c => !Number.isInteger(c?.id_carteira) || c.id_carteira <= 0 || typeof c.nome !== "string" || typeof c.ativa !== "boolean")) {
    throw new Error("A API retornou uma lista de carteiras inválida.");
  }
  return dados;
}

export class ErroSalvarCarteira extends Error {
  readonly impedirReenvio: boolean;
  constructor(mensagem: string, impedirReenvio = false) {
    super(mensagem);
    this.name = "ErroSalvarCarteira";
    this.impedirReenvio = impedirReenvio;
  }
}

async function mensagemResposta(resposta: Response): Promise<string> {
  const dados = await resposta.json().catch(() => null);
  if (typeof dados?.detail === "string") return dados.detail;
  if (Array.isArray(dados?.detail)) {
    return dados.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join("; ") || "Dados recusados pela API.";
  }
  return `A API respondeu com erro ${resposta.status}.`;
}

// Requisicoes sequenciais: se um ativo falhar, tenta remover somente a carteira criada aqui.
export async function salvarCarteira(nome: string, ativos: AtivoConfigurado[]): Promise<number> {
  const erro = validarConfiguracao(nome, ativos);
  if (erro) throw new Error(erro);
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
  let resposta: Response;
  try {
    resposta = await fetch(`${API_BASE}/portfolios`, { method: "POST", headers, body: JSON.stringify({ nome: nome.trim() }) });
  } catch {
    throw new ErroSalvarCarteira("Não foi possível confirmar a criação da carteira. Consulte a listagem antes de tentar novamente para evitar duplicidade.", true);
  }
  if (!resposta.ok) {
    const mensagem = await mensagemResposta(resposta);
    throw new ErroSalvarCarteira(resposta.status >= 500 ? `${mensagem} Consulte a listagem antes de tentar novamente: a criação pode ter ocorrido.` : mensagem, resposta.status >= 500);
  }
  const criada = await resposta.json().catch(() => null);
  const id: unknown = criada?.id_carteira;
  if (typeof id !== "number" || !Number.isInteger(id) || id <= 0) {
    throw new ErroSalvarCarteira("A API não retornou o ID da carteira criada. Consulte a listagem antes de tentar novamente.", true);
  }
  try {
    for (const ativo of ativos) {
      const centesimos = percentualEmCentesimos(ativo.objetivo)!;
      const resultado = await fetch(`${API_BASE}/assets/carteira`, {
        method: "POST", headers,
        body: JSON.stringify({ ticker: ativo.ticker, id_carteira: id, quantidade: 0, objetivo_percentual: (centesimos / 100).toFixed(2) }),
      });
      if (!resultado.ok) throw new Error(`${ativo.ticker}: ${await mensagemResposta(resultado)}`);
    }
  } catch (falha) {
    const motivo = falha instanceof Error ? falha.message : "Falha ao cadastrar os ativos.";
    try {
      const exclusao = await fetch(`${API_BASE}/portfolios/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      if (!exclusao.ok && exclusao.status !== 404) throw new Error("Exclusão não confirmada", { cause: falha });
    } catch {
      throw new ErroSalvarCarteira(`O cadastro não foi concluído e não foi possível confirmar a exclusão da carteira ${id}. Consulte a listagem antes de tentar novamente. Detalhe: ${motivo}`, true);
    }
    throw new ErroSalvarCarteira(`Não foi possível salvar os ativos. A carteira criada nesta tentativa foi removida; seus dados continuam no formulário. Detalhe: ${motivo}`);
  }
  return id;
}

async function alterarCarteira(id: number, method: "PATCH" | "DELETE", dados?: { nome: string }): Promise<void> {
  if (!Number.isInteger(id) || id <= 0) throw new Error("Carteira inválida.");
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  let resposta: Response;
  try {
    resposta = await fetch(`${API_BASE}/portfolios/${id}`, {
      method,
      headers: { Authorization: `Bearer ${token}`, ...(dados ? { "Content-Type": "application/json" } : {}) },
      ...(dados ? { body: JSON.stringify(dados) } : {}),
    });
  } catch (cause) {
    throw new Error("Não foi possível confirmar a operação. Atualize a listagem para conferir o resultado antes de tentar novamente.", { cause });
  }
  if (method === "DELETE" && resposta.status === 404) return;
  if (!resposta.ok) throw new Error(await mensagemResposta(resposta));
}

export async function renomearCarteira(id: number, nome: string): Promise<void> {
  const nomeLimpo = nome.trim();
  if (!nomeLimpo) throw new Error("Informe o nome da carteira");
  if (nomeLimpo.length > 100) throw new Error("O nome da carteira deve ter no máximo 100 caracteres");
  const carteiras = await consultarCarteiras();
  if (carteiras.some(c => c.id_carteira !== id && c.nome.trim().toLocaleLowerCase("pt-BR") === nomeLimpo.toLocaleLowerCase("pt-BR"))) {
    throw new Error("Já existe uma carteira com este nome");
  }
  await alterarCarteira(id, "PATCH", { nome: nomeLimpo });
}

export async function excluirCarteira(id: number): Promise<void> {
  await alterarCarteira(id, "DELETE");
}

export interface ConfiguracaoCarteira {
  carteira: CarteiraResumo;
  ativos: AtivoConfigurado[];
}

export async function consultarConfiguracaoCarteira(id: number, signal?: AbortSignal): Promise<ConfiguracaoCarteira> {
  if (!Number.isInteger(id) || id <= 0) throw new Error("Carteira inválida.");
  const [carteira, vinculos, catalogo] = await Promise.all([
    consultar(`/portfolios/${id}`, signal), consultar(`/assets/carteira/${id}`, signal), consultar("/assets", signal),
  ]);
  const resumo = carteira as CarteiraResumo;
  if (resumo?.id_carteira !== id || typeof resumo.nome !== "string" || typeof resumo.ativa !== "boolean" || !Array.isArray(vinculos) || !Array.isArray(catalogo)) throw new Error("A API retornou dados da carteira inválidos.");
  const ativos = vinculos.map(vinculo => {
    const ativo = catalogo.find(a => a?.ticker === vinculo?.ticker);
    const percentual = String(vinculo?.objetivo_percentual);
    if (!ativo || typeof ativo.setor !== "string" || typeof ativo.ativo !== "boolean" || vinculo.id_carteira !== id || !Number.isInteger(vinculo.quantidade) || vinculo.quantidade < 0 || percentualEmCentesimos(percentual) === null) throw new Error("A API retornou uma composição inválida.");
    return { ticker: String(vinculo.ticker), setor: ativo.setor, ativo: ativo.ativo, objetivo: percentual, quantidade: vinculo.quantidade };
  });
  return { carteira: resumo, ativos };
}

function assinaturaConfiguracao(configuracao: ConfiguracaoCarteira): string {
  return JSON.stringify({ nome: configuracao.carteira.nome, ativa: configuracao.carteira.ativa, ativos: configuracao.ativos.map(a => [a.ticker, a.quantidade, percentualEmCentesimos(a.objetivo)]).sort((a, b) => String(a[0]).localeCompare(String(b[0]))) });
}

export async function editarComposicaoCarteira(original: ConfiguracaoCarteira, nome: string, ativos: AtivoConfigurado[]): Promise<void> {
  const id = original.carteira.id_carteira;
  const carteiras = await consultarCarteiras();
  const erro = validarConfiguracao(nome, ativos, carteiras.filter(c => c.id_carteira !== id).map(c => c.nome));
  if (erro) throw new Error(erro);
  const atual = await consultarConfiguracaoCarteira(id);
  if (assinaturaConfiguracao(atual) !== assinaturaConfiguracao(original)) throw new ErroSalvarCarteira("A carteira foi alterada desde a abertura da tela. Recarregue os dados antes de salvar.", true);
  if (!atual.carteira.ativa) throw new Error("A carteira está desativada.");
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
  const existentes = new Map(original.ativos.map(a => [a.ticker, a]));
  const desejados = new Set(ativos.map(a => a.ticker));
  const operacoes: { caminho: string; method: string; dados?: object }[] = [];
  for (const ativo of ativos) {
    const anterior = existentes.get(ativo.ticker);
    const objetivo = percentualEmCentesimos(ativo.objetivo)!;
    if (!anterior) operacoes.push({ caminho: "/assets/carteira", method: "POST", dados: { ticker: ativo.ticker, id_carteira: id, quantidade: 0, objetivo_percentual: (objetivo / 100).toFixed(2) } });
    else if (objetivo !== percentualEmCentesimos(anterior.objetivo)) operacoes.push({ caminho: `/assets/carteira/${id}/${encodeURIComponent(ativo.ticker)}`, method: "PATCH", dados: { objetivo_percentual: (objetivo / 100).toFixed(2) } });
  }
  // Remocoes por ultimo; nunca exclui a carteira existente para compensar falhas.
  for (const ativo of original.ativos) if (!desejados.has(ativo.ticker)) operacoes.push({ caminho: `/assets/carteira/${id}/${encodeURIComponent(ativo.ticker)}`, method: "DELETE" });
  if (nome.trim() !== original.carteira.nome) operacoes.push({ caminho: `/portfolios/${id}`, method: "PATCH", dados: { nome: nome.trim() } });
  for (const op of operacoes) {
    try {
      const resposta = await fetch(`${API_BASE}${op.caminho}`, { method: op.method, headers, ...(op.dados ? { body: JSON.stringify(op.dados) } : {}) });
      if (!resposta.ok) throw new Error(await mensagemResposta(resposta));
    } catch (falha) {
      throw new ErroSalvarCarteira(`Não foi possível concluir todas as alterações. Parte delas pode ter sido salva. Recarregue os dados da carteira antes de tentar novamente. Detalhe: ${falha instanceof Error ? falha.message : "Falha de conexão"}`, true);
    }
  }
}
