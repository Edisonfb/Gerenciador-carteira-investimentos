import { obterTokenAcesso, obterUsuarioAtual } from "./autenticacaoService";

export interface ContaAnalista {
  id_analista: number;
  id_usuario: number;
  nome: string;
  email: string;
  ativo: boolean;
}

async function consultar(caminho: string, opcoes: RequestInit = {}): Promise<Response> {
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  const resposta = await fetch(`http://127.0.0.1:8000${caminho}`, { ...opcoes,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
  });
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(typeof erro?.detail === "string" ? erro.detail : "Não foi possível acessar sua conta.");
  }
  return resposta;
}

export async function buscarMinhaContaAnalista(): Promise<ContaAnalista> {
  const sessao = await (await consultar("/auth/me")).json();
  if (sessao.tipo_usuario?.toLowerCase() !== "analista") throw new Error("Esta página é destinada à conta do analista.");
  // A API atual não possui /analysts/me; resolve o próprio perfil pela lista existente.
  const analistas: Omit<ContaAnalista, "ativo">[] = await (await consultar("/analysts/analistas")).json();
  const perfil = analistas.find(analista => analista.id_usuario === sessao.id_usuario);
  if (!perfil) throw new Error("Perfil de analista não encontrado.");
  return { ...perfil, email: sessao.email, ativo: sessao.ativo };
}

export async function atualizarMinhaContaAnalista(dados: { nome: string; email: string }): Promise<ContaAnalista> {
  const conta = await buscarMinhaContaAnalista();
  await consultar(`/analysts/analistas/${conta.id_analista}`, { method: "PATCH", body: JSON.stringify(dados) });
  await obterUsuarioAtual();
  return buscarMinhaContaAnalista();
}
