import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { realizarLogin } from "../services/autenticacaoService";
import "../styles/login.css";

export const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mensagemErro, setMensagemErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function enviarLogin(evento: React.FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setCarregando(true);
    setMensagemErro("");
    try {
      const usuario = await realizarLogin(email.trim(), senha);
      navigate(usuario.perfil === "analista" ? "/dashboard" : "/minha-conta", { replace: true });
    } catch (erro) {
      setMensagemErro(erro instanceof Error ? erro.message : "Não foi possível realizar o login.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <section className="acesso-cartao" aria-labelledby="titulo-login">
      <h1 id="titulo-login">Login</h1>
      <form onSubmit={enviarLogin} className="acesso-formulario">
        <label htmlFor="email">E-mail</label>
        <input type="email" id="email" name="email" autoComplete="username" required value={email} onChange={(evento) => setEmail(evento.target.value)} />
        <label htmlFor="senha">Senha</label>
        <input type="password" id="senha" name="senha" autoComplete="current-password" required value={senha} onChange={(evento) => setSenha(evento.target.value)} />
        <Link className="acesso-link" to="/esqueci-senha">Esqueci minha senha</Link>
        {mensagemErro && <p role="alert" className="acesso-erro">{mensagemErro}</p>}
        <button id="botao_login" type="submit" disabled={carregando}>{carregando ? "Entrando..." : "Entrar"}</button>
        <Link className="acesso-link" to="/primeiro-acesso">Primeiro acesso</Link>
      </form>
    </section>
  );
};
