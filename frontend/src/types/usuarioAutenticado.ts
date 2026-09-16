import type { PerfilUsuario } from "./usuario";

export interface UsuarioAutenticado {
  id: number;
  nome: string;
  perfil: PerfilUsuario;
}
