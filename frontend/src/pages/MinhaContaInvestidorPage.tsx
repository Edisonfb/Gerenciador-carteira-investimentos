import { useState } from "react";
import {
  FormularioInvestidor,
  type DadosFormularioInvestidor,
} from "../components/FormularioInvestidor";
import { buscarUsuarioAutenticado } from "../services/autenticacaoService";
import {
  atualizarInvestidor,
  buscarInvestidorPorId,
} from "../services/investidorService";
import "../styles/usuarios.css";

export function MinhaContaInvestidorPage() {
  const usuarioAutenticado = buscarUsuarioAutenticado();

  const [estaEditando, setEstaEditando] = useState(false);

  if (usuarioAutenticado.perfil !== "investidor") {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Acesso não permitido</h1>
            <p>Esta página é destinada à conta do investidor.</p>
          </div>
        </div>
      </main>
    );
  }

  const investidor = buscarInvestidorPorId(usuarioAutenticado.id);

  if (!investidor) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Conta não encontrada</h1>
            <p>Não foi possível localizar os dados da sua conta.</p>
          </div>
        </div>
      </main>
    );
  }

  const investidorId = investidor.id;

  function salvarMinhaConta(dados: DadosFormularioInvestidor) {
    const investidorAtualizado = atualizarInvestidor(investidorId, {
      nome: dados.nome,
      sobrenome: dados.sobrenome,
      email: dados.email,
      celular: dados.celular,
      rua: dados.rua,
      numero: dados.numero,
      bairro: dados.bairro,
      cep: dados.cep,
      cidade: dados.cidade,
      uf: dados.uf,
    });

    if (!investidorAtualizado) {
      window.alert("Não foi possível atualizar sua conta.");
      return;
    }

    window.alert("Conta atualizada com sucesso.");
    setEstaEditando(false);
  }

  function cancelarEdicao() {
    setEstaEditando(false);
  }

  if (estaEditando) {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cabecalho-pagina">
            <h1>Editar Minha Conta</h1>
          </div>

          <div className="cartao">
            <FormularioInvestidor
              key={investidor.id}
              investidor={investidor}
              onSalvar={salvarMinhaConta}
              onCancelar={cancelarEdicao}
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

          <button
            className="botao botao-primario"
            onClick={() => setEstaEditando(true)}
          >
            Editar dados
          </button>
        </div>

        <div className="cartao">
          <p>
            <strong>Tipo de usuário:</strong> Investidor
          </p>

          <p>
            <strong>Nome:</strong> {investidor.nome}
          </p>

          <p>
            <strong>Sobrenome:</strong> {investidor.sobrenome}
          </p>

          <p>
            <strong>E-mail:</strong> {investidor.email}
          </p>

          <p>
            <strong>CPF:</strong> {investidor.cpf}
          </p>

          <p>
            <strong>Celular:</strong> {investidor.celular}
          </p>

          <p>
            <strong>Rua:</strong> {investidor.rua}
          </p>

          <p>
            <strong>Número:</strong> {investidor.numero}
          </p>

          <p>
            <strong>Bairro:</strong> {investidor.bairro}
          </p>

          <p>
            <strong>CEP:</strong> {investidor.cep}
          </p>

          <p>
            <strong>Cidade:</strong> {investidor.cidade}
          </p>

          <p>
            <strong>UF:</strong> {investidor.uf}
          </p>

          <p>
            <strong>Status:</strong> {investidor.status}
          </p>
        </div>
      </div>
    </main>
  );
}
