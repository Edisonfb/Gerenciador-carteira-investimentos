import { useState } from "react";
import {
  FormularioUsuario,
  type DadosFormularioUsuario,
} from "../components/FormularioUsuario";
import { buscarUsuarioAutenticado } from "../services/autenticacaoService";
import {
  atualizarUsuario,
  buscarUsuarioPorId,
} from "../services/usuarioService";
import "../styles/usuarios.css";

export function MinhaContaPage() {
  const usuarioAutenticado = buscarUsuarioAutenticado();

  const [estaEditando, setEstaEditando] = useState(false);

  if (usuarioAutenticado.perfil !== "analista") {
    return (
      <main className="pagina-usuarios">
        <div className="conteudo-usuarios">
          <div className="cartao">
            <h1>Acesso não permitido</h1>
            <p>Esta página é destinada à conta do analista.</p>
          </div>
        </div>
      </main>
    );
  }

  const usuario = buscarUsuarioPorId(usuarioAutenticado.id);

  if (!usuario) {
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

  const usuarioId = usuario.id;

  function salvarMinhaConta(dados: DadosFormularioUsuario) {
    const usuarioAtualizado = atualizarUsuario(usuarioId, {
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

    if (!usuarioAtualizado) {
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
            <FormularioUsuario
              key={usuario.id}
              usuario={usuario}
              onSalvar={salvarMinhaConta}
              onCancelar={cancelarEdicao}
              permitirAlterarPerfil={false}
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
            <strong>Tipo de usuário:</strong> Analista
          </p>

          <p>
            <strong>Nome:</strong> {usuario.nome}
          </p>

          <p>
            <strong>Sobrenome:</strong> {usuario.sobrenome}
          </p>

          <p>
            <strong>E-mail:</strong> {usuario.email}
          </p>

          <p>
            <strong>CPF:</strong> {usuario.cpf}
          </p>

          <p>
            <strong>Celular:</strong> {usuario.celular}
          </p>

          <p>
            <strong>Rua:</strong> {usuario.rua}
          </p>

          <p>
            <strong>Número:</strong> {usuario.numero}
          </p>

          <p>
            <strong>Bairro:</strong> {usuario.bairro}
          </p>

          <p>
            <strong>CEP:</strong> {usuario.cep}
          </p>

          <p>
            <strong>Cidade:</strong> {usuario.cidade}
          </p>

          <p>
            <strong>UF:</strong> {usuario.uf}
          </p>

          <p>
            <strong>Status:</strong> {usuario.status}
          </p>
        </div>
      </div>
    </main>
  );
}
