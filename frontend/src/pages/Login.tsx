
export const Login = () => {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f8fafc' }}>
      <div style={{ background: '#fff', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', width: '100%', maxWidth: '400px' }}>
        <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Login</h2>
        <form>
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
            <input type="email" id="nome" name="nome" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />

            <label htmlFor="senha" style={{ display: 'block', marginBottom: '0.5rem' }}>Senha:</label>
            <input type="password" id="senha" name="senha" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <button id="botao_login" type="submit">Entrar</button>
          </div>

        </form>
      </div>
    </div>
  );
};