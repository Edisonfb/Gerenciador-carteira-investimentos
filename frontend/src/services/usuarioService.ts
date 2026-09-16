import type { Usuario } from "../types/usuario";

let usuariosMock: Usuario[] = [
  {
    id: 1,
    nome: "Ricardo",
    sobrenome: "Almeida",
    email: "ricardo.almeida@cerne.com",
    cpf: "000.000.000-00",
    celular: "(51) 99999-9999",
    rua: "Rua das Flores",
    numero: "100",
    bairro: "Centro",
    cep: "95700-000",
    cidade: "Bento Gonçalves",
    uf: "RS",
    perfil: "analista",
    status: "ativo",
  },
  {
    id: 2,
    nome: "Fernanda",
    sobrenome: "Dutra",
    email: "fernanda.dutra@cerne.com",
    cpf: "111.111.111-11",
    celular: "(51) 98888-8888",
    rua: "Rua Principal",
    numero: "250",
    bairro: "Centro",
    cep: "95700-001",
    cidade: "Bento Gonçalves",
    uf: "RS",
    perfil: "administrador",
    status: "ativo",
  },
];

export function buscarUsuarios(): Usuario[] {
  return usuariosMock;
}

export function buscarUsuarioPorId(id: number): Usuario | undefined {
  return usuariosMock.find((usuario) => usuario.id === id);
}

export function criarUsuario(novoUsuario: Omit<Usuario, "id">): Usuario {
  const usuarioCriado: Usuario = {
    ...novoUsuario,
    id: Date.now(),
  };

  usuariosMock = [...usuariosMock, usuarioCriado];

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

  usuariosMock = usuariosMock.map((usuario) =>
    usuario.id === id ? usuarioAtualizado : usuario,
  );

  return usuarioAtualizado;
}

export function excluirUsuario(id: number): boolean {
  const quantidadeAnterior = usuariosMock.length;

  usuariosMock = usuariosMock.filter((usuario) => usuario.id !== id);

  return usuariosMock.length < quantidadeAnterior;
}
