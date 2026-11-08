export interface ContaInvestidor {
  id: number;
  nomeUsuario: string;
  emailComunicacao: string;
  emailRecuperacao: string;
  ativo: boolean;
}

export interface EdicaoContaInvestidor {
  nomeUsuario: string;
  emailComunicacao: string;
  emailRecuperacao: string;
  senhaAtual: string;
  novaSenha: string;
  confirmacaoSenha: string;
}

export function validarEdicaoConta(dados: EdicaoContaInvestidor): string | null {
  if (!dados.nomeUsuario.trim() || dados.nomeUsuario.trim().length > 50) return "Informe um usuário de até 50 caracteres.";
  const emailValido = (valor: string) => valor.trim().length <= 255 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor.trim());
  if (!emailValido(dados.emailComunicacao)) return "Informe um e-mail de comunicação válido.";
  if (!emailValido(dados.emailRecuperacao)) return "Informe um e-mail de recuperação válido.";
  if (dados.emailComunicacao.trim().toLowerCase() === dados.emailRecuperacao.trim().toLowerCase()) return "O e-mail de recuperação deve ser diferente do e-mail de comunicação.";
  if (!dados.senhaAtual) return "Informe sua senha atual para confirmar as alterações.";
  if (dados.novaSenha && (!dados.novaSenha.trim() || dados.novaSenha.length < 8 || new TextEncoder().encode(dados.novaSenha).length > 72)) return "A nova senha deve ter no mínimo 8 caracteres e no máximo 72 bytes.";
  if (dados.novaSenha !== dados.confirmacaoSenha) return "As senhas não coincidem.";
  return null;
}
