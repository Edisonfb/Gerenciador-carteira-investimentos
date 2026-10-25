import { useEffect, useState } from "react";
import {
  FormularioInvestidor,
  type DadosFormularioInvestidor,
} from "../components/FormularioInvestidor";
import {
  atualizarMeuPerfilInvestidor,
  buscarMeuPerfilInvestidor,
} from "../services/investidorService";
import type { Investidor } from "../types/investidor";
import "../styles/usuarios.css";

export function MinhaContaInvestidorPage() {
  const [investidor, setInvestidor] = useState<Investidor | null>(null);
  const [estaEditando, setEstaEditando] = useState(false);
  const [carregando, setCarregando] = useState(true);
  const [mensagemErro, setMensagemErro] = useState("");

  useEffect(() => {
    buscarMeuPerfilInvestidor()
      .then(setInvestidor)
      .catch((erro: unknown) => {
        setMensagemErro(
          erro instanceof Error ? erro.message : "Não foi possível carregar o perfil.",
        );
      })
      .finally(() => setCarregando(false));
  }, []);

  async function salvarMinhaConta(dados: DadosFormularioInvestidor) {
    try {
      const atualizado = await atualizarMeuPerfilInvestidor(dados);
      setInvestidor(atualizado);
      setEstaEditando(false);
      window.alert("Conta atualizada com sucesso.");
    } catch (erro) {
      window.alert(
        erro instanceof Error ? erro.message : "Não foi possível atualizar sua conta.",
      );
    }
  }

  if (carregando) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios"><p>Carregando sua conta...</p></div>
      </main>
    );
  }

  if (mensagemErro || !investidor) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Não foi possível abrir sua conta</h1>
            <p>{mensagemErro || "Perfil de investidor não encontrado."}</p>
          </div>
        </div>
      </main>
    );
  }

  if (estaEditando) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cabecalho-pagina"><h1>Editar Minha Conta</h1></div>
          <div className="cartao">
            <FormularioInvestidor
              key={investidor.id}
              investidor={investidor}
              onSalvar={salvarMinhaConta}
              onCancelar={() => setEstaEditando(false)}
              permitirAlterarCpf={false}
              textoBotaoSalvar="Salvar alterações"
            />
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="pagina-usuarios">
      <div className="conteudo-usuarios">
        <div className="cabecalho-pagina">
          <h1>Minha Conta</h1>
          <button className="botao botao-primario" onClick={() => setEstaEditando(true)}>
            Editar dados
          </button>
        </div>
        <div className="cartao">
          <p><strong>Tipo de usuário:</strong> Investidor</p>
          <p><strong>Nome:</strong> {investidor.nome}</p>
          <p><strong>Sobrenome:</strong> {investidor.sobrenome}</p>
          <p><strong>E-mail:</strong> {investidor.email}</p>
          <p><strong>CPF:</strong> {investidor.cpf}</p>
          <p><strong>Celular:</strong> {investidor.celular}</p>
          <p><strong>Rua:</strong> {investidor.rua}</p>
          <p><strong>Número:</strong> {investidor.numero}</p>
          <p><strong>Bairro:</strong> {investidor.bairro}</p>
          <p><strong>CEP:</strong> {investidor.cep}</p>
          <p><strong>Cidade:</strong> {investidor.cidade}</p>
          <p><strong>UF:</strong> {investidor.uf}</p>
          <p><strong>Status:</strong> {investidor.status}</p>
        </div>
      </div>
    </main>
  );
}
