import { useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { solicitarAcessoSenha, redefinirSenha, validarPrimeiroAcesso } from "../services/autenticacaoService";
import "../styles/login.css";

export function AcessoSenhaPage({ primeiroAcesso = false, definirSenha = false }: { primeiroAcesso?: boolean; definirSenha?: boolean }) {
  const [parametros] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const estado = location.state as { tokenDefinicao?: string } | null;
  const token = primeiroAcesso ? estado?.tokenDefinicao ?? "" : parametros.get("token") ?? "";
  const [tokenInicial, setTokenInicial] = useState("");
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
        navigate("/", { replace: true, state: { mensagemSucesso: "Senha definida com sucesso. Entre com seu e-mail e sua nova senha." } });
      } else if (primeiroAcesso) {
        const tokenDefinicao = await validarPrimeiroAcesso(email.trim(), tokenInicial.trim());
        setTokenInicial("");
        navigate("/primeiro-acesso/definir-senha", { replace: true, state: { tokenDefinicao } });
      } else {
        await solicitarAcessoSenha(email.trim());
        setMensagem("Se houver uma conta ativa elegível, enviaremos o link ao e-mail de recuperação cadastrado do investidor. Para analistas, o envio é ao e-mail da conta. Verifique também a caixa de spam.");
      }
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : "Não foi possível concluir a solicitação.");
    } finally { setEnviando(false); }
  }

  return <section className="acesso-cartao" aria-labelledby="titulo-acesso">
    <h1 id="titulo-acesso">{titulo}</h1>
    <p>{definirSenha ? "Crie uma senha de 8 a 72 caracteres." : primeiroAcesso ? "Informe seu e-mail e o token recebido quando o analista cadastrou sua conta." : "Informe o e-mail principal da sua conta. Investidores recebem o link no e-mail de recuperação cadastrado; analistas, no e-mail da conta."}</p>
    <form onSubmit={enviar} className="acesso-formulario">
      {definirSenha ? <>
        <label htmlFor="nova-senha">Nova senha</label>
        <input id="nova-senha" type="password" autoComplete="new-password" required minLength={8} maxLength={72} value={senha} onChange={e => setSenha(e.target.value)} />
        <label htmlFor="confirmacao">Confirmar senha</label>
        <input id="confirmacao" type="password" autoComplete="new-password" required minLength={8} maxLength={72} value={confirmacao} onChange={e => setConfirmacao(e.target.value)} />
      </> : <>
        <label htmlFor="email-acesso">E-mail cadastrado</label>
        <input id="email-acesso" type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} />
        {primeiroAcesso && <>
          <label htmlFor="token-inicial">Token recebido por e-mail</label>
          <input id="token-inicial" type="text" autoComplete="one-time-code" autoCapitalize="none" spellCheck={false} required maxLength={255} value={tokenInicial} onChange={e => setTokenInicial(e.target.value)} />
        </>}
      </>}
      {erro && <p role="alert" className="acesso-erro">{erro}</p>}
      {mensagem && <p role="status" className="acesso-mensagem">{mensagem}</p>}
      <button type="submit" disabled={enviando || !!mensagem || (definirSenha && !token)}>{enviando ? "Enviando..." : definirSenha ? "Salvar senha" : primeiroAcesso ? "Validar token e continuar" : "Enviar link por e-mail"}</button>
      {definirSenha && !token && <p role="alert" className="acesso-erro">{primeiroAcesso ? <>Valide seu e-mail e token na <Link to="/primeiro-acesso">tela de primeiro acesso</Link>.</> : "Link inválido. Solicite um novo link."}</p>}
      <Link className="acesso-link" to="/">Voltar ao login</Link>
    </form>
  </section>;
}
