import type { UsuarioAutenticado } from "../types/usuarioAutenticado";

const usuarioAutenticadoMock: UsuarioAutenticado = {
  id: 1,
  nome: "Ricardo Almeida",
  perfil: "analista",
};

export function buscarUsuarioAutenticado(): UsuarioAutenticado {
  return usuarioAutenticadoMock;
}
