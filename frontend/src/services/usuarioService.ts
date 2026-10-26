import type { Usuario } from "../types/usuario";

let usuariosEmMemoria: Usuario[] = [];

export function buscarUsuarios(): Usuario[] {
  return usuariosEmMemoria;
}

export function buscarUsuarioPorId(id: number): Usuario | undefined {
  return usuariosEmMemoria.find((usuario) => usuario.id === id);
}

export function criarUsuario(novoUsuario: Omit<Usuario, "id">): Usuario {
  const usuarioCriado: Usuario = {
    ...novoUsuario,
    id: Date.now(),
  };

  usuariosEmMemoria = [...usuariosEmMemoria, usuarioCriado];

  return usuarioCriado;
}

export function atualizarUsuario(
  id: number,
  dadosAtualizados: Partial<Usuario>,
): Usuario | undefined {
  const usuarioEncontrado = buscarUsuarioPorId(id);

  if (!usuarioEncontrado) {
    return undefined;
  }

  const usuarioAtualizado: Usuario = {
    ...usuarioEncontrado,
    ...dadosAtualizados,
    id: usuarioEncontrado.id,
  };

  usuariosEmMemoria = usuariosEmMemoria.map((usuario) =>
    usuario.id === id ? usuarioAtualizado : usuario,
  );

  return usuarioAtualizado;
}

export function excluirUsuario(id: number): boolean {
  const quantidadeAnterior = usuariosEmMemoria.length;

  usuariosEmMemoria = usuariosEmMemoria.filter((usuario) => usuario.id !== id);

  return usuariosEmMemoria.length < quantidadeAnterior;
}
