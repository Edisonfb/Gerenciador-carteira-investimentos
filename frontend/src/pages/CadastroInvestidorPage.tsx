import {
  FormularioInvestidor,
  type DadosFormularioInvestidor,
} from "../components/FormularioInvestidor";
import { criarInvestidor } from "../services/investidorService";
import { buscarUsuarioAutenticado } from "../services/autenticacaoService";
import { useNavigate } from "react-router-dom";
import "../styles/usuarios.css";

export function CadastroInvestidorPage() {
  const navigate = useNavigate();
  const usuarioAutenticado = buscarUsuarioAutenticado();

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
  function voltarParaLista() {
    navigate("/investidores");
  }

  async function cadastrarInvestidor(dados: DadosFormularioInvestidor) {
    try{
      await criarInvestidor({
        ...dados,
        idAnalistaResponsavel: usuarioAutenticado.id,
        perfil: "investidor",
        status: "ativo",
      });

      window.alert(
        "Investidor cadastrado com sucesso. O acesso será enviado para o e-mail informado.",
      );

      voltarParaLista();
    } catch(erro){
    window.alert("Não foi possível cadastrar o investidor");
    }
  }

  return (
    <main className="pagina-usuarios">
      <div className="conteudo-usuarios">
        <div className="cabecalho-pagina">
          <h1>Cadastrar Investidor</h1>
        </div>

        <div className="cartao">
          <FormularioInvestidor
            onSalvar={cadastrarInvestidor}
            onCancelar={voltarParaLista}
            textoBotaoSalvar="Cadastrar"
          />
        </div>
      </div>
    </main>
  );
}
