import { useState } from "react";
import type { FormEvent } from "react";
import type { PerfilUsuario, Usuario } from "../types/usuario";

export interface DadosFormularioUsuario {
  nome: string;
  sobrenome: string;
  email: string;
  cpf: string;
  celular: string;
  rua: string;
  numero: string;
  bairro: string;
  cep: string;
  cidade: string;
  uf: string;
  perfil: PerfilUsuario;
}

interface FormularioUsuarioProps {
  usuario?: Usuario;
  onSalvar: (dados: DadosFormularioUsuario) => void;
  onCancelar: () => void;
  permitirAlterarPerfil?: boolean;
  permitirAlterarCpf?: boolean;
  textoBotaoSalvar?: string;
}

export function FormularioUsuario({
  usuario,
  onSalvar,
  onCancelar,
  permitirAlterarPerfil = false,
  permitirAlterarCpf = true,
  textoBotaoSalvar = "Salvar alterações",
}: FormularioUsuarioProps) {
  const [nome, setNome] = useState(usuario?.nome ?? "");
  const [sobrenome, setSobrenome] = useState(usuario?.sobrenome ?? "");
  const [email, setEmail] = useState(usuario?.email ?? "");
  const [cpf, setCpf] = useState(usuario?.cpf ?? "");
  const [celular, setCelular] = useState(usuario?.celular ?? "");
  const [rua, setRua] = useState(usuario?.rua ?? "");
  const [numero, setNumero] = useState(usuario?.numero ?? "");
  const [bairro, setBairro] = useState(usuario?.bairro ?? "");
  const [cep, setCep] = useState(usuario?.cep ?? "");
  const [cidade, setCidade] = useState(usuario?.cidade ?? "");
  const [uf, setUf] = useState(usuario?.uf ?? "");
  const [perfil, setPerfil] = useState<PerfilUsuario>(
    usuario?.perfil ?? "analista",
  );

  const [mensagemErro, setMensagemErro] = useState("");

  function somenteNumeros(valor: string) {
    return valor.replace(/\D/g, "");
  }

  function validarFormulario(): boolean {
    if (nome.trim() === "") {
      setMensagemErro("O nome é obrigatório.");
      return false;
    }

    if (sobrenome.trim() === "") {
      setMensagemErro("O sobrenome é obrigatório.");
      return false;
    }

    if (email.trim() === "") {
      setMensagemErro("O e-mail é obrigatório.");
      return false;
    }

    const formatoEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!formatoEmail.test(email.trim())) {
      setMensagemErro("Informe um e-mail válido.");
      return false;
    }

    const cpfNumerico = somenteNumeros(cpf);

    if (cpfNumerico.length !== 11) {
      setMensagemErro("O CPF deve possuir 11 dígitos.");
      return false;
    }

    const cepNumerico = somenteNumeros(cep);

    if (cep.trim() !== "" && cepNumerico.length !== 8) {
      setMensagemErro("O CEP deve possuir 8 dígitos.");
      return false;
    }

    if (uf.trim() !== "" && uf.trim().length !== 2) {
      setMensagemErro("A UF deve possuir 2 letras.");
      return false;
    }

    setMensagemErro("");
    return true;
  }

  function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const formularioValido = validarFormulario();

    if (!formularioValido) {
      return;
    }

    onSalvar({
      nome: nome.trim(),
      sobrenome: sobrenome.trim(),
      email: email.trim(),
      cpf: cpf.trim(),
      celular: celular.trim(),
      rua: rua.trim(),
      numero: numero.trim(),
      bairro: bairro.trim(),
      cep: cep.trim(),
      cidade: cidade.trim(),
      uf: uf.trim().toUpperCase(),
      perfil,
    });
  }

  return (
    <form className="formulario-usuario" onSubmit={enviarFormulario}>
      <div className="grade-formulario">
        <div className="campo-formulario">
          <label htmlFor="perfil">Tipo de usuário</label>

          <select
            id="perfil"
            value={perfil}
            disabled={!permitirAlterarPerfil}
            onChange={(evento) =>
              setPerfil(evento.target.value as PerfilUsuario)
            }
          >
            <option value="analista">Analista</option>
            <option value="administrador">Administrador</option>
          </select>
        </div>

        <div className="campo-formulario">
          <label htmlFor="nome">Nome</label>
          <input
            id="nome"
            type="text"
            value={nome}
            onChange={(evento) => setNome(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="sobrenome">Sobrenome</label>
          <input
            id="sobrenome"
            type="text"
            value={sobrenome}
            onChange={(evento) => setSobrenome(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="email">E-mail</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(evento) => setEmail(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="cpf">CPF</label>
          <input
            id="cpf"
            type="text"
            value={cpf}
            disabled={!permitirAlterarCpf}
            onChange={(evento) => setCpf(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="celular">Celular</label>
          <input
            id="celular"
            type="text"
            value={celular}
            onChange={(evento) => setCelular(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="rua">Rua</label>
          <input
            id="rua"
            type="text"
            value={rua}
            onChange={(evento) => setRua(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="numero">Número</label>
          <input
            id="numero"
            type="text"
            value={numero}
            onChange={(evento) => setNumero(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="bairro">Bairro</label>
          <input
            id="bairro"
            type="text"
            value={bairro}
            onChange={(evento) => setBairro(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="cep">CEP</label>
          <input
            id="cep"
            type="text"
            value={cep}
            onChange={(evento) => setCep(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="cidade">Cidade</label>
          <input
            id="cidade"
            type="text"
            value={cidade}
            onChange={(evento) => setCidade(evento.target.value)}
          />
        </div>

        <div className="campo-formulario">
          <label htmlFor="uf">UF</label>
          <input
            id="uf"
            type="text"
            value={uf}
            maxLength={2}
            onChange={(evento) => setUf(evento.target.value.toUpperCase())}
          />
        </div>
      </div>

      {mensagemErro && <p className="mensagem-erro">{mensagemErro}</p>}

      <div className="acoes-formulario">
        <button
          className="botao botao-secundario"
          type="button"
          onClick={onCancelar}
        >
          Cancelar
        </button>

        <button className="botao botao-primario" type="submit">
          {textoBotaoSalvar}
        </button>
      </div>
    </form>
  );
}
