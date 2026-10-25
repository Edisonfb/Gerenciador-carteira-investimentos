import type { PerfilUsuario } from "../types/usuario";
import type { UsuarioAutenticado } from "../types/usuarioAutenticado";

const API_BASE = "http://127.0.0.1:8000";
const CHAVE_USUARIO = "usuario_autenticado";

interface LoginResposta {
  access_token: string;
  token_type: string;
}

interface UsuarioApi {
  id_usuario: number;
  email: string;
  tipo_usuario: PerfilUsuario;
  ativo: boolean;
}

export async function realizarLogin(
  email: string,
  senha: string,
): Promise<UsuarioAutenticado> {
  const resposta = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, senha }),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => null);
    throw new Error(erro?.detail ?? "Não foi possível realizar o login.");
  }

  const sessao: LoginResposta = await resposta.json();
  localStorage.setItem("access_token", sessao.access_token);
  localStorage.setItem("token_type", sessao.token_type);

  try {
    return await obterUsuarioAtual();
  } catch (erro) {
    encerrarSessao();
    throw erro;
  }
}

export async function obterUsuarioAtual(): Promise<UsuarioAutenticado> {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("Não há uma sessão ativa.");
  }

  const resposta = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resposta.ok) {
    throw new Error("Sessão inválida ou expirada.");
  }

  const usuarioApi: UsuarioApi = await resposta.json();
  const usuario: UsuarioAutenticado = {
    id: usuarioApi.id_usuario,
    email: usuarioApi.email,
    perfil: usuarioApi.tipo_usuario.toLowerCase() as PerfilUsuario,
  };
  localStorage.setItem(CHAVE_USUARIO, JSON.stringify(usuario));
  return usuario;
}

export function buscarUsuarioAutenticado(): UsuarioAutenticado | null {
  const usuarioSalvo = localStorage.getItem(CHAVE_USUARIO);
  if (!usuarioSalvo) return null;

  try {
    return JSON.parse(usuarioSalvo) as UsuarioAutenticado;
  } catch {
    encerrarSessao();
    return null;
  }
}

export function obterTokenAcesso(): string | null {
  return localStorage.getItem("access_token");
}

export function encerrarSessao(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_type");
  localStorage.removeItem(CHAVE_USUARIO);
}
