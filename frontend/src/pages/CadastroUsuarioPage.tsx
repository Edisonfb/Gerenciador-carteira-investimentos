import { useNavigate } from "react-router-dom";
import {
  FormularioUsuario,
  type DadosFormularioUsuario,
} from "../components/FormularioUsuario";
import { criarUsuario } from "../services/usuarioService";
import "../styles/usuarios.css";

export function CadastroUsuarioPage() {
  const navigate = useNavigate();

  function voltarParaLista() {
    navigate("/usuarios");
  }

  function cadastrarUsuario(dados: DadosFormularioUsuario) {
    criarUsuario({
      ...dados,
      perfil: "analista",
      status: "ativo",
    });

    window.alert("Usuário cadastrado com sucesso.");

    voltarParaLista();
  }

  return (
    <main className="pagina-usuarios">
      <div className="conteudo-usuarios">
        <div className="cabecalho-pagina">
          <h1>Cadastrar Usuário</h1>
        </div>

        <div className="cartao">
          <FormularioUsuario
            onSalvar={cadastrarUsuario}
            onCancelar={voltarParaLista}
            textoBotaoSalvar="Cadastrar"
          />
        </div>
      </div>
    </main>
  );
}
