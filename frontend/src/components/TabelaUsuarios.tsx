import type { Usuario } from "../types/usuario";
import "../styles/usuarios.css";

interface TabelaUsuariosProps {
  usuarios: Usuario[];
  onEditarUsuario: (id: number) => void;
  onExcluirUsuario: (id: number) => void;
}

export function TabelaUsuarios({
  usuarios,
  onEditarUsuario,
  onExcluirUsuario,
}: TabelaUsuariosProps) {
  return (
    <div className="tabela-container">
      <table className="tabela-usuarios">
        <thead>
          <tr>
            <th>Nome</th>
            <th>E-mail</th>
            <th>Perfil</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>

        <tbody>
          {usuarios.map((usuario) => (
            <tr key={usuario.id}>
              <td>
                {usuario.nome} {usuario.sobrenome}
              </td>

              <td>{usuario.email}</td>

              <td>{usuario.perfil}</td>

              <td>
                <span
                  className={`status ${
                    usuario.status === "ativo"
                      ? "status-ativo"
                      : "status-bloqueado"
                  }`}
                >
                  {usuario.status}
                </span>
              </td>

              <td>
                {usuario.perfil === "analista" && (
                  <div className="acoes-tabela">
                    <button
                      className="botao botao-secundario"
                      onClick={() => onEditarUsuario(usuario.id)}
                    >
                      Editar
                    </button>

                    <button
                      className="botao botao-perigo"
                      onClick={() => onExcluirUsuario(usuario.id)}
                    >
                      Excluir
                    </button>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
