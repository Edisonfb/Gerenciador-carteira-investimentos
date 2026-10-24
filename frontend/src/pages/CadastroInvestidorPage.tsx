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
  const idUsuarioAutenticado = usuarioAutenticado.id;

  function voltarParaLista() {
    navigate("/dashboard");
  }

  async function cadastrarInvestidor(dados: DadosFormularioInvestidor) {
    try{
      const criado = await criarInvestidor({
        ...dados,
        idAnalistaResponsavel: idUsuarioAutenticado,
        perfil: "investidor",
        status: "ativo",
      });

      window.alert(
        criado.emailAcessoEnviado
          ? "Investidor cadastrado com sucesso. O acesso foi enviado para o e-mail informado."
          : "Investidor cadastrado com sucesso, mas o e-mail de acesso não foi enviado. Solicite ao responsável a configuração do envio de e-mail. Não é necessário cadastrar novamente.",
      );

      voltarParaLista();
    } catch (erro) {
      window.alert(erro instanceof Error ? erro.message : "Não foi possível cadastrar o investidor.");
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
