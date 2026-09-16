import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TabelaUsuarios } from "../components/TabelaUsuarios";
import { buscarUsuarioAutenticado } from "../services/autenticacaoService";
import { buscarUsuarios, excluirUsuario } from "../services/usuarioService";
import type { Usuario } from "../types/usuario";
import "../styles/usuarios.css";

export function UsuariosPage() {
  const navigate = useNavigate();

  const usuarioAutenticado = buscarUsuarioAutenticado();

  const [usuarios, setUsuarios] = useState<Usuario[]>(buscarUsuarios());

  function iniciarCadastro() {
    navigate("/usuarios/novo");
  }

  function editarUsuario(id: number) {
    navigate(`/usuarios/${id}/editar`);
  }

  function excluirContaUsuario(id: number) {
    const usuario = usuarios.find((usuario) => usuario.id === id);

    if (!usuario) {
      return;
    }

    if (usuario.perfil !== "analista") {
      return;
    }

    const confirmouExclusao = window.confirm(
      `Tem certeza que deseja excluir a conta de ${usuario.nome} ${usuario.sobrenome}?`,
    );

    if (!confirmouExclusao) {
      return;
    }

    const usuarioExcluido = excluirUsuario(id);

    if (usuarioExcluido) {
      setUsuarios(buscarUsuarios());
    }
  }

  return (
    <main className="pagina-usuarios">
      <div className="conteudo-usuarios">
        <div className="cabecalho-pagina">
          <h1>Usuários do Sistema</h1>

          {usuarioAutenticado.perfil === "administrador" && (
            <button className="botao botao-primario" onClick={iniciarCadastro}>
              Cadastrar Usuário +
            </button>
          )}
        </div>

        <div className="cartao">
          <TabelaUsuarios
            usuarios={usuarios}
            onEditarUsuario={editarUsuario}
            onExcluirUsuario={excluirContaUsuario}
          />
        </div>
      </div>
    </main>
  );
}
