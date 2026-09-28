import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { realizarLogin } from "../services/autenticacaoService";

export const Login = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mensagemErro, setMensagemErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function enviarLogin(evento: React.FormEvent<HTMLFormElement>) {
  evento.preventDefault();

    try {
      setCarregando(true);
      setMensagemErro("");

      const resposta = await realizarLogin(email, senha);

      localStorage.setItem("access_token", resposta.access_token);
      localStorage.setItem("token_type", resposta.token_type);

      navigate("/dashboard");
    } catch (erro) {
      if (erro instanceof Error) {
        setMensagemErro(erro.message);
      } else {
        setMensagemErro("Não foi possível realizar o login.");
      }
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f8fafc' }}>
      <div style={{ background: '#fff', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', width: '100%', maxWidth: '400px' }}>
        <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Login</h2>
        <form onSubmit={enviarLogin}>
          <div>
            <label htmlFor="tipo_usuario">Tipo usuario:</label>

            <select 
              name="seletor_usuario" id="seletor_usuario_login"
              style={{ width: "100%", padding: "0.5rem", borderRadius: "4px", border: "1px solid #ccc", background: "#fff" }}
              required
            
            >
              
              <option value="Investidor">Investidor</option>
              <option value="Analista">Analista</option>
              <option value="Admin">Adiministrador</option>

            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem' }}>Email:</label>
            <input type="email" id="email" name="email" value={email}
              onChange={(evento) => setEmail(evento.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />

            <label htmlFor="senha" style={{ display: 'block', marginBottom: '0.5rem' }}>Senha:</label>
            <input type="password" id="senha" name="senha" value={senha}
              onChange={(evento) => setSenha(evento.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            {mensagemErro && <p style={{ color: "red" }}>{mensagemErro}</p>}
            <button id="botao_login" type="submit" disabled={carregando}>{carregando ? "Entrando..." : "Entrar"}</button>
          </div>

        </form>
      </div>
    </div>
  );
};