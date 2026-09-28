import type { UsuarioAutenticado } from "../types/usuarioAutenticado";

const usuarioAutenticadoMock: UsuarioAutenticado = {
  id: 2,
  nome: "Ricardo Almeida",
  perfil: "analista",
};

export function buscarUsuarioAutenticado(): UsuarioAutenticado {
  return usuarioAutenticadoMock;
}

interface LoginResposta {
  access_token: string;
  token_type: string;
}

export async function realizarLogin(
  email: string,
  senha: string,
): Promise<LoginResposta> {
  const resposta = await fetch("http://127.0.0.1:8000/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      senha,
    }),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(erro?.detail ?? "Não foi possível realizar o login.");
  }

  return resposta.json();
}