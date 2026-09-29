import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import {
  encerrarSessao,
  obterUsuarioAtual,
} from "../services/autenticacaoService";
import type { PerfilUsuario } from "../types/usuario";
import type { UsuarioAutenticado } from "../types/usuarioAutenticado";

interface RotaProtegidaProps {
  perfisPermitidos: PerfilUsuario[];
}

function caminhoInicial(perfil: PerfilUsuario): string {
  if (perfil === "investidor") return "/minha-conta";
  if (perfil === "analista") return "/dashboard";
  return "/";
}

export function RotaProtegida({ perfisPermitidos }: RotaProtegidaProps) {
  const [usuario, setUsuario] = useState<UsuarioAutenticado | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    obterUsuarioAtual()
      .then(setUsuario)
      .catch(() => {
        encerrarSessao();
        setUsuario(null);
      })
      .finally(() => setCarregando(false));
  }, []);

  if (carregando) return <p>Verificando sessão...</p>;
  if (!usuario) return <Navigate to="/" replace />;
  if (!perfisPermitidos.includes(usuario.perfil)) {
    return <Navigate to={caminhoInicial(usuario.perfil)} replace />;
  }

  return <Outlet />;
}
