import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import type { FormEvent } from "react";
import type { Investidor } from "../types/investidor";

export interface DadosFormularioInvestidor {
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
}

interface FormularioInvestidorProps {
  investidor?: Investidor;
  onSalvar: (dados: DadosFormularioInvestidor) => void;
  onCancelar: () => void;
  permitirAlterarCpf?: boolean;
  textoBotaoSalvar?: string;
  usarShadcn?: boolean;
  salvando?: boolean;
}

export function FormularioInvestidor({
  investidor,
  onSalvar,
  onCancelar,
  permitirAlterarCpf = true,
  textoBotaoSalvar = "Salvar alterações",
  usarShadcn = false,
  salvando = false,
}: FormularioInvestidorProps) {
  const CampoEntrada = usarShadcn ? Input : "input";

  const [nome, setNome] = useState(investidor?.nome ?? "");
  const [sobrenome, setSobrenome] = useState(investidor?.sobrenome ?? "");
  const [email, setEmail] = useState(investidor?.email ?? "");
  const [cpf, setCpf] = useState(investidor?.cpf ?? "");
  const [celular, setCelular] = useState(investidor?.celular ?? "");
  const [rua, setRua] = useState(investidor?.rua ?? "");
  const [numero, setNumero] = useState(investidor?.numero ?? "");
  const [bairro, setBairro] = useState(investidor?.bairro ?? "");
  const [cep, setCep] = useState(investidor?.cep ?? "");
  const [cidade, setCidade] = useState(investidor?.cidade ?? "");
  const [uf, setUf] = useState(investidor?.uf ?? "");

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

    if (celular.trim() === "") {
      setMensagemErro("O celular é obrigatório.");
      return false;
    }
    const celularNumerico = somenteNumeros(celular);

    if (celularNumerico.length !== 11) {
      setMensagemErro("O celular deve possuir 11 dígitos.");
      return false;
    }

    if (rua.trim() === "") {
      setMensagemErro("A rua é obrigatória.");
      return false;
    }

    if (numero.trim() === "") {
      setMensagemErro("O número é obrigatório.");
      return false;
    }

    if (bairro.trim() === "") {
      setMensagemErro("O bairro é obrigatório.");
      return false;
    }

    if (cep.trim() === "") {
      setMensagemErro("O CEP é obrigatório.");
      return false;
    }
    const cepNumerico = somenteNumeros(cep);

    if (cepNumerico.length !== 8) {
      setMensagemErro("O CEP deve possuir 8 dígitos.");
      return false;
    }

    if (cidade.trim() === "") {
      setMensagemErro("A cidade é obrigatória.");
      return false;
    }

    if (uf.trim() === "") {
      setMensagemErro("A UF é obrigatória.");
      return false;
    }

    if (uf.trim().length !== 2) {
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
    });
  }

  return (
    <form className={usarShadcn ? "space-y-6" : "formulario-usuario"} onSubmit={enviarFormulario} aria-busy={salvando}>
      <fieldset disabled={salvando} className={usarShadcn ? "m-0 min-w-0 border-0 p-0" : undefined}>
      <div className={usarShadcn ? "grid grid-cols-1 gap-5 sm:grid-cols-2" : "grade-formulario"}>
        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="nome">Nome</label>
          <CampoEntrada
            id="nome"
            type="text"
            value={nome}
            onChange={(evento) => setNome(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="sobrenome">Sobrenome</label>
          <CampoEntrada
            id="sobrenome"
            type="text"
            value={sobrenome}
            onChange={(evento) => setSobrenome(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="email">E-mail</label>
          <CampoEntrada
            id="email"
            type="email"
            value={email}
            onChange={(evento) => setEmail(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="cpf">CPF</label>
          <CampoEntrada
            id="cpf"
            type="text"
            value={cpf}
            disabled={!permitirAlterarCpf}
            onChange={(evento) => setCpf(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="celular">Celular</label>
          <CampoEntrada
            id="celular"
            type="text"
            value={celular}
            onChange={(evento) => setCelular(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="rua">Rua</label>
          <CampoEntrada
            id="rua"
            type="text"
            value={rua}
            onChange={(evento) => setRua(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="numero">Número</label>
          <CampoEntrada
            id="numero"
            type="text"
            value={numero}
            onChange={(evento) => setNumero(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="bairro">Bairro</label>
          <CampoEntrada
            id="bairro"
            type="text"
            value={bairro}
            onChange={(evento) => setBairro(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="cep">CEP</label>
          <CampoEntrada
            id="cep"
            type="text"
            value={cep}
            onChange={(evento) => setCep(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="cidade">Cidade</label>
          <CampoEntrada
            id="cidade"
            type="text"
            value={cidade}
            onChange={(evento) => setCidade(evento.target.value)}
          />
        </div>

        <div className={usarShadcn ? "flex flex-col gap-2 text-sm font-medium" : "campo-formulario"}>
          <label htmlFor="uf">UF</label>
          <CampoEntrada
            id="uf"
            type="text"
            value={uf}
            maxLength={2}
            onChange={(evento) => setUf(evento.target.value.toUpperCase())}
          />
        </div>
      </div>

      </fieldset>
      {mensagemErro && <p role="alert" className={usarShadcn ? "text-sm text-destructive" : "mensagem-erro"}>{mensagemErro}</p>}

      {usarShadcn ? (
        <div className="flex flex-col-reverse gap-3 border-t pt-6 sm:flex-row sm:justify-end">
          <Button variant="outline" type="button" onClick={onCancelar} disabled={salvando}>Cancelar</Button>
          <Button type="submit" disabled={salvando}>{salvando ? "Salvando..." : textoBotaoSalvar}</Button>
        </div>
      ) : (
        <div className="acoes-formulario">
          <button className="botao botao-secundario" type="button" onClick={onCancelar}>Cancelar</button>
          <button className="botao botao-primario" type="submit">{textoBotaoSalvar}</button>
        </div>
      )}
    </form>
  );
}
