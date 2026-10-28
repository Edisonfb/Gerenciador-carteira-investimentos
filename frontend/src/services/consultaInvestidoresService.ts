import { obterTokenAcesso } from "./autenticacaoService";
import type { ConviteInvestidor } from "./conviteInvestidorService";

export interface ContaInvestidorConsulta {
  id_usuario: number;
  email: string;
  ativo: boolean | null;
  convite: "enviado" | "nao_confirmado" | null;
  cadastro: "concluido" | "pendente" | null;
}

export async function listarContasInvestidores(signal?: AbortSignal): Promise<ContaInvestidorConsulta[]> {
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  let resposta: Response;
  try {
    resposta = await fetch("http://127.0.0.1:8000/auth/usuarios", {
      headers: { Authorization: `Bearer ${token}` }, signal,
    });
  } catch (erro) {
    if (erro instanceof Error && erro.name === "AbortError") throw erro;
    throw new Error("Não foi possível consultar os investidores. Verifique a conexão e o backend.", { cause: erro });
  }
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(typeof erro?.detail === "string" ? erro.detail : "Não foi possível consultar os investidores.");
  }
  const dados: unknown = await resposta.json();
  if (!Array.isArray(dados) || dados.some(conta => typeof conta?.id_usuario !== "number" || typeof conta?.email !== "string" || typeof conta?.tipo_usuario !== "string" || typeof conta?.ativo !== "boolean")) {
    throw new Error("O servidor retornou uma lista de contas inválida.");
  }
  return dados.filter(conta => conta.tipo_usuario.toLowerCase() === "investidor").map(conta => ({
    id_usuario: conta.id_usuario, email: conta.email, ativo: conta.ativo,
    convite: null, cadastro: null,
  })).sort((a, b) => a.email.localeCompare(b.email, "pt-BR"));
}

export function combinarContasEConvites(contas: ContaInvestidorConsulta[], convites: ConviteInvestidor[]): ContaInvestidorConsulta[] {
  const resultado = new Map(contas.map(conta => [conta.id_usuario, { ...conta }]));
  for (const convite of convites) {
    const existente = resultado.get(convite.id_usuario);
    resultado.set(convite.id_usuario, {
      id_usuario: convite.id_usuario, email: convite.email,
      ativo: existente?.ativo ?? null,
      convite: convite.email_acesso_enviado === true ? "enviado" : "nao_confirmado",
      cadastro: typeof convite.primeiro_acesso_concluido === "boolean" ? (convite.primeiro_acesso_concluido ? "concluido" : "pendente") : null,
    });
  }
  return [...resultado.values()].sort((a, b) => a.email.localeCompare(b.email, "pt-BR"));
}

export function filtrarContasInvestidores(contas: ContaInvestidorConsulta[], busca: string, situacao = "todas") {
  const termo = busca.trim().toLowerCase();
  return contas.filter(conta => conta.email.toLowerCase().includes(termo)
    && (situacao === "todas" || (situacao === "ativas" && conta.ativo === true) || (situacao === "inativas" && conta.ativo === false)));
}
