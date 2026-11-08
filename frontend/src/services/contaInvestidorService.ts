import { obterTokenAcesso } from "./autenticacaoService";
import { validarEdicaoConta } from "../types/contaInvestidor";
import type { ContaInvestidor, EdicaoContaInvestidor } from "../types/contaInvestidor";

function converter(dados: unknown): ContaInvestidor {
  const perfil = dados as { id_investidor: number; nome_usuario: string | null; email: string; email_recuperacao: string | null; ativo: boolean };
  if (!perfil || !Number.isInteger(perfil.id_investidor) || typeof perfil.email !== "string" || typeof perfil.ativo !== "boolean" || !(perfil.nome_usuario === null || typeof perfil.nome_usuario === "string") || !(perfil.email_recuperacao === null || typeof perfil.email_recuperacao === "string")) throw new Error("A API retornou dados da conta inválidos.");
  return { id: perfil.id_investidor, nomeUsuario: perfil.nome_usuario ?? "", emailComunicacao: perfil.email, emailRecuperacao: perfil.email_recuperacao ?? "", ativo: perfil.ativo };
}

async function requisitar(method: "GET" | "PATCH", dados?: object, signal?: AbortSignal): Promise<ContaInvestidor> {
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  let resposta: Response;
  try {
    resposta = await fetch("http://127.0.0.1:8000/investors/me", {
      method, signal, headers: { Authorization: `Bearer ${token}`, ...(dados ? { "Content-Type": "application/json" } : {}) },
      ...(dados ? { body: JSON.stringify(dados) } : {}),
    });
  } catch (cause) {
    if (cause instanceof Error && cause.name === "AbortError") throw cause;
    throw new Error(method === "GET" ? "Não foi possível carregar sua conta. Verifique a conexão e o backend." : "Não foi possível confirmar a atualização. Recarregue a conta para conferir os dados; se alterou a senha, tente entrar com a nova senha.", { cause });
  }
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(typeof erro?.detail === "string" ? erro.detail : "Não foi possível concluir a operação. Confira os dados informados.");
  }
  return converter(await resposta.json());
}

export function buscarContaInvestidor(signal?: AbortSignal): Promise<ContaInvestidor> {
  return requisitar("GET", undefined, signal);
}

export function salvarContaInvestidor(dados: EdicaoContaInvestidor): Promise<ContaInvestidor> {
  const erro = validarEdicaoConta(dados);
  if (erro) return Promise.reject(new Error(erro));
  return requisitar("PATCH", { nome_usuario: dados.nomeUsuario.trim(), email: dados.emailComunicacao.trim().toLowerCase(), email_recuperacao: dados.emailRecuperacao.trim().toLowerCase(), senha_atual: dados.senhaAtual, ...(dados.novaSenha ? { nova_senha: dados.novaSenha } : {}) });
}
