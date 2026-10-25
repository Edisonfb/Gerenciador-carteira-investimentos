import { useNavigate, useParams } from "react-router-dom";
import {
  FormularioInvestidor,
  type DadosFormularioInvestidor,
} from "../components/FormularioInvestidor";
import {
  atualizarInvestidor,
  buscarInvestidorPorId,
} from "../services/investidorService";
import { buscarUsuarioAutenticado } from "../services/autenticacaoService";

import "../styles/usuarios.css";

export function EdicaoInvestidorPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const usuarioAutenticado = buscarUsuarioAutenticado();

  const investidorId = Number(id);

  function voltarParaLista() {
    navigate("/investidores");
  }

  if (Number.isNaN(investidorId)) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Investidor inválido</h1>

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

  const investidor = buscarInvestidorPorId(investidorId);

  if (!investidor) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Investidor não encontrado</h1>

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

  if (
    !usuarioAutenticado ||
    usuarioAutenticado.perfil !== "analista" ||
    investidor.idAnalistaResponsavel !== usuarioAutenticado.id
  ) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Acesso não permitido</h1>

            <p>
              Esta funcionalidade é destinada ao gerenciamento de investidores
              pelo Analista responsável.
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

  function salvarAlteracoes(dados: DadosFormularioInvestidor) {
    const investidorAtualizado = atualizarInvestidor(investidorId, dados);

    if (!investidorAtualizado) {
      window.alert("Não foi possível atualizar o investidor.");
      return;
    }

    window.alert("Investidor atualizado com sucesso.");

    voltarParaLista();
  }

  return (
    <main className="pagina-usuarios">
      <div className="conteudo-usuarios">
        <div className="cabecalho-pagina">
          <h1>Editar Investidor</h1>
        </div>

        <div className="cartao">
          <FormularioInvestidor
            investidor={investidor}
            onSalvar={salvarAlteracoes}
            onCancelar={voltarParaLista}
            permitirAlterarCpf={false}
            textoBotaoSalvar="Salvar alterações"
          />
        </div>
      </div>
    </main>
  );
}
