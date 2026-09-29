import type { PerfilUsuario } from "./usuario";

export interface UsuarioAutenticado {
  id: number;
  email: string;
  perfil: PerfilUsuario;
}
