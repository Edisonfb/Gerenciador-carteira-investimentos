export interface CadastroPrimeiroAcesso {
  nomeUsuario: string;
  emailComunicacao: string;
  emailRecuperacao: string;
  senha: string;
  confirmacaoSenha: string;
}

export function validarCadastroPrimeiroAcesso(dados: CadastroPrimeiroAcesso): string | null {
  if (!dados.nomeUsuario.trim()) return "Informe o nome de usuário.";
  if (dados.nomeUsuario.trim().length > 50) return "O nome de usuário deve ter no máximo 50 caracteres.";
  const emailValido = (email: string) => email.trim().length <= 255 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
  if (!emailValido(dados.emailComunicacao)) return "Informe um e-mail de comunicação válido.";
  if (!emailValido(dados.emailRecuperacao)) return "Informe um e-mail de recuperação válido.";
  if (dados.emailComunicacao.trim().toLowerCase() === dados.emailRecuperacao.trim().toLowerCase()) return "O e-mail de recuperação deve ser diferente do e-mail de comunicação.";
  if (dados.senha.length < 8 || new TextEncoder().encode(dados.senha).length > 72) return "A senha deve ter no mínimo 8 caracteres e no máximo 72 bytes.";
  if (dados.senha !== dados.confirmacaoSenha) return "As senhas não coincidem.";
  return null;
}
