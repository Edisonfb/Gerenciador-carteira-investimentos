import { obterTokenAcesso } from "./autenticacaoService";

export interface ConviteInvestidor {
  id_investidor: number;
  id_usuario: number;
  email: string;
  primeiro_acesso_concluido: boolean;
  email_acesso_enviado: boolean;
}

export function validarEmailConvite(email: string): string | null {
  if (!email.trim()) return "Informe o e-mail do cliente";
  if (email.trim().length > 255 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) return "E-mail inválido";
  return null;
}

export async function gerarConviteInvestidor(email: string): Promise<ConviteInvestidor> {
  const erroEmail = validarEmailConvite(email);
  if (erroEmail) throw new Error(erroEmail);
  const token = obterTokenAcesso();
  if (!token) throw new Error("Sua sessão expirou. Entre novamente.");
  let resposta: Response;
  try {
    resposta = await fetch("http://127.0.0.1:8000/investors", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ email: email.trim().toLowerCase() }),
    });
  } catch (erro) {
    throw new Error("Não foi possível confirmar a geração do convite. Verifique a conexão e o backend antes de tentar novamente.", { cause: erro });
  }
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(typeof erro?.detail === "string" ? erro.detail : resposta.status >= 500
      ? "Não foi possível concluir o convite. Verifique o envio de e-mail no backend antes de tentar novamente."
      : "Não foi possível gerar o convite de acesso.");
  }
  const dados: ConviteInvestidor = await resposta.json();
  if (typeof dados.id_investidor !== "number" || typeof dados.email !== "string") throw new Error("O servidor retornou uma resposta inesperada. Confira o cadastro antes de tentar novamente.");
  return dados;
}
