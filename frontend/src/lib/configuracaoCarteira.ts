import type { AtivoConfigurado, AtivoDisponivel } from "../types/configuracaoCarteira";

export const ERRO_CODIGO = "Código de ativo inválido. Use quatro letras e um número, sem espaços ou caracteres especiais";

// Inteiros em centésimos de percentual evitam imprecisão na soma de 100%.
export function percentualEmCentesimos(valor: string): number | null {
  if (!/^\d{1,3}(?:[.,]\d{1,2})?$/.test(valor)) return null;
  const [inteiro, decimal = ""] = valor.replace(",", ".").split(".");
  const numero = Number(inteiro) * 100 + Number(decimal.padEnd(2, "0"));
  return numero <= 10000 ? numero : null;
}

export function formatarPercentual(centesimos: number): string {
  return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 }).format(centesimos / 100);
}

export function filtrarAtivos(catalogo: AtivoDisponivel[], busca: string, setor: string) {
  return catalogo.filter(ativo => ativo.ativo && ativo.codigo.toUpperCase().includes(busca.trim().toUpperCase()) && (!setor || ativo.setor === setor));
}

export function validarInclusao(codigo: string, objetivo: string, catalogo: AtivoDisponivel[], selecionados: AtivoConfigurado[]): string | null {
  const normalizado = codigo.toUpperCase();
  if (!/^[A-Z]{4}\d$/.test(normalizado)) return ERRO_CODIGO;
  if (!catalogo.some(ativo => ativo.ativo && ativo.codigo.toUpperCase() === normalizado)) return "Ativo não encontrado na lista de ativos aceitos";
  if (selecionados.some(ativo => ativo.codigo.toUpperCase() === normalizado)) return "Ativo já incluído nesta carteira";
  if (percentualEmCentesimos(objetivo) === null) return "Informe um objetivo entre 0 e 100%, com até duas casas decimais";
  return null;
}

export function validarConfiguracao(nome: string, ativos: AtivoConfigurado[], nomesExistentes: string[] = []): string | null {
  if (!nome.trim()) return "Informe o nome da carteira";
  if (nome.trim().length > 100) return "O nome da carteira deve ter no máximo 100 caracteres";
  if (nomesExistentes.some(existente => existente.trim().toLocaleLowerCase("pt-BR") === nome.trim().toLocaleLowerCase("pt-BR"))) return "Já existe uma carteira com este nome";
  if (!ativos.length) return "Inclua pelo menos um ativo na carteira";
  if (ativos.some(ativo => percentualEmCentesimos(ativo.objetivo) === null)) return "Informe um objetivo entre 0 e 100% para cada ativo, com até duas casas decimais";
  const soma = ativos.reduce((total, ativo) => total + percentualEmCentesimos(ativo.objetivo)!, 0);
  if (soma !== 10000) return `O objetivo total da carteira deve somar 100%. Soma atual: ${formatarPercentual(soma)}%`;
  return null;
}
