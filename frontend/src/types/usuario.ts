export type PerfilUsuario = "analista" | "administrador";

export type StatusUsuario = "ativo" | "bloqueado";

export interface Usuario {
  id: number;
  nome: string;
  sobrenome: string;
  email: string;
  cpf: string;
  celular: string;
  rua: string;
  numero: string;
  bairro: string;
  cep: string;
  cidade: string;
  uf: string;
  perfil: PerfilUsuario;
  status: StatusUsuario;
}
