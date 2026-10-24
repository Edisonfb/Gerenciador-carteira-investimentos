import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { solicitarAcessoSenha, redefinirSenha } from "../services/autenticacaoService";
import "../styles/login.css";

export function AcessoSenhaPage({ primeiroAcesso = false, definirSenha = false }: { primeiroAcesso?: boolean; definirSenha?: boolean }) {
  const [parametros] = useSearchParams();
  const token = parametros.get("token") ?? "";
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erro, setErro] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [enviando, setEnviando] = useState(false);
  const titulo = definirSenha ? "Definir senha" : primeiroAcesso ? "Primeiro acesso" : "Esqueci minha senha";

  async function enviar(evento: React.FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setErro("");
    setMensagem("");
    if (definirSenha && senha !== confirmacao) { setErro("As senhas não coincidem."); return; }
    setEnviando(true);
    try {
      if (definirSenha) {
        await redefinirSenha(token, senha);
        setSenha(""); setConfirmacao("");
        setMensagem("Senha definida com sucesso. Volte ao login para entrar.");
      } else {
        await solicitarAcessoSenha(email.trim(), primeiroAcesso);
        setMensagem("Se houver uma conta ativa elegível para este e-mail, você receberá um link para definir sua senha. Verifique também a caixa de spam.");
      }
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : "Não foi possível concluir a solicitação.");
    } finally { setEnviando(false); }
  }

  return <section className="acesso-cartao" aria-labelledby="titulo-acesso">
    <h1 id="titulo-acesso">{titulo}</h1>
    <p>{definirSenha ? "Crie uma senha de 8 a 72 caracteres." : primeiroAcesso ? "Informe o e-mail cadastrado pelo responsável para criar sua senha." : "Informe o e-mail da sua conta para receber o link de recuperação."}</p>
    <form onSubmit={enviar} className="acesso-formulario">
      {definirSenha ? <>
        <label htmlFor="nova-senha">Nova senha</label>
        <input id="nova-senha" type="password" autoComplete="new-password" required minLength={8} maxLength={72} value={senha} onChange={e => setSenha(e.target.value)} />
        <label htmlFor="confirmacao">Confirmar senha</label>
        <input id="confirmacao" type="password" autoComplete="new-password" required minLength={8} maxLength={72} value={confirmacao} onChange={e => setConfirmacao(e.target.value)} />
      </> : <>
        <label htmlFor="email-acesso">E-mail cadastrado</label>
        <input id="email-acesso" type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} />
      </>}
      {erro && <p role="alert" className="acesso-erro">{erro}</p>}
      {mensagem && <p role="status" className="acesso-mensagem">{mensagem}</p>}
      <button type="submit" disabled={enviando || !!mensagem || (definirSenha && !token)}>{enviando ? "Enviando..." : definirSenha ? "Salvar senha" : "Enviar link por e-mail"}</button>
      {definirSenha && !token && <p role="alert" className="acesso-erro">Link inválido. Solicite um novo link.</p>}
      <Link className="acesso-link" to="/">Voltar ao login</Link>
    </form>
  </section>;
}
