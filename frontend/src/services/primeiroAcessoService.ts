import { validarCadastroPrimeiroAcesso } from "../lib/primeiroAcesso";
import type { CadastroPrimeiroAcesso } from "../lib/primeiroAcesso";

export async function concluirCadastroPrimeiroAcesso(token: string, dados: CadastroPrimeiroAcesso): Promise<void> {
  if (!token) throw new Error("Valide seu e-mail e token antes de concluir o cadastro.");
  const erro = validarCadastroPrimeiroAcesso(dados);
  if (erro) throw new Error(erro);
  let resposta: Response;
  try {
    resposta = await fetch("http://127.0.0.1:8000/investors/first-access", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token_definicao: token, nome_usuario: dados.nomeUsuario.trim(), email_comunicacao: dados.emailComunicacao.trim().toLowerCase(), email_recuperacao: dados.emailRecuperacao.trim().toLowerCase(), nova_senha: dados.senha }),
    });
  } catch (cause) {
    throw new Error("Não foi possível confirmar o cadastro. Verifique sua conexão. Caso ele já tenha sido concluído, entre com o usuário e a senha escolhidos.", { cause });
  }
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(typeof erro?.detail === "string" ? erro.detail : "Não foi possível concluir o cadastro. Confira os dados ou valide novamente seu convite.");
  }
}
