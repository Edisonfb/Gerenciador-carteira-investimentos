import { useNavigate, useParams } from "react-router-dom";
import {
  FormularioUsuario,
  type DadosFormularioUsuario,
} from "../components/FormularioUsuario";
import {
  atualizarUsuario,
  buscarUsuarioPorId,
} from "../services/usuarioService";
import "../styles/usuarios.css";

export function EdicaoUsuarioPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const usuarioId = Number(id);

  function voltarParaLista() {
    navigate("/usuarios");
  }

  if (Number.isNaN(usuarioId)) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Usuário inválido</h1>

            <button
              className="botao botao-secundario"
              onClick={voltarParaLista}
            >
              Voltar
            </button>
          </div>
        </div>
      </main>
    );
  }

  const usuario = buscarUsuarioPorId(usuarioId);

  if (!usuario) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Usuário não encontrado</h1>

            <button
              className="botao botao-secundario"
              onClick={voltarParaLista}
            >
              Voltar
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (usuario.perfil !== "analista") {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Acesso não permitido</h1>

            <p>
              Esta funcionalidade é destinada ao gerenciamento de analistas.
            </p>

            <button
              className="botao botao-secundario"
              onClick={voltarParaLista}
            >
              Voltar
            </button>
          </div>
        </div>
      </main>
    );
  }

  function salvarAlteracoes(dados: DadosFormularioUsuario) {
    const usuarioAtualizado = atualizarUsuario(usuarioId, dados);

    if (!usuarioAtualizado) {
      window.alert("Não foi possível atualizar o usuário.");
      return;
    }

    window.alert("Usuário atualizado com sucesso.");

    voltarParaLista();
  }

  return (
    <main className="pagina-usuarios">
      <div className="conteudo-usuarios">
        <div className="cabecalho-pagina">
          <h1>Editar Usuário</h1>
        </div>

        <div className="cartao">
          <FormularioUsuario
            usuario={usuario}
            onSalvar={salvarAlteracoes}
            onCancelar={voltarParaLista}
          />
        </div>
      </div>
    </main>
  );
}
