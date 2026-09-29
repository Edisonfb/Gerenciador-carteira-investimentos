import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TabelaInvestidores } from "../components/TabelaInvestidores";
import { buscarUsuarioAutenticado } from "../services/autenticacaoService";
import {
  buscarInvestidoresPorAnalista,
  excluirInvestidor,
} from "../services/investidorService";
import "../styles/usuarios.css";
import type { Investidor } from "../types/investidor";

export function InvestidoresPage() {
  const navigate = useNavigate();

  const usuarioAutenticado = buscarUsuarioAutenticado();

  const [investidores, setInvestidores] = useState<Investidor[]>(
    buscarInvestidoresPorAnalista(usuarioAutenticado?.id ?? 0),
  );
  if (!usuarioAutenticado || usuarioAutenticado.perfil !== "analista") {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Acesso não permitido</h1>
            <p>
              Esta página é destinada ao gerenciamento de investidores pelo
              analista.
            </p>
          </div>
        </div>
      </main>
    );
  }

  const idAnalistaResponsavel = usuarioAutenticado.id;

  function iniciarCadastro() {
    navigate("/investidores/novo");
  }

  function editarInvestidor(id: number) {
    navigate(`/investidores/${id}/editar`);
  }

  function excluirContaInvestidor(id: number) {
    const investidor = investidores.find((investidor) => investidor.id === id);

    if (!investidor) {
      return;
    }

    const confirmouExclusao = window.confirm(
      `Tem certeza que deseja excluir a conta de ${investidor.nome} ${investidor.sobrenome}?`,
    );

    if (!confirmouExclusao) {
      return;
    }

    const investidorExcluido = excluirInvestidor(id);

    if (investidorExcluido) {
      setInvestidores(buscarInvestidoresPorAnalista(idAnalistaResponsavel));
    }
  }

  return (
    <main className="pagina-usuarios">
      <div className="conteudo-usuarios">
        <div className="cabecalho-pagina">
          <h1>Investidores</h1>
          <button className="botao botao-primario" onClick={iniciarCadastro}>
            Cadastrar Investidor +
          </button>
        </div>

        <div className="cartao">
          <TabelaInvestidores
            investidores={investidores}
            onEditarInvestidor={editarInvestidor}
            onExcluirInvestidor={excluirContaInvestidor}
          />
        </div>
      </div>
    </main>
  );
}
