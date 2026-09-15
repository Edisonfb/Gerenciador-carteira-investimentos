
export const LoginAnalista = () => {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f8fafc' }}>
      <div style={{ background: '#fff', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', width: '100%', maxWidth: '400px' }}>
        <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Login do Analista</h2>
        <form>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="nome" style={{ display: 'block', marginBottom: '0.5rem' }}>Nome:</label>
            <input type="text" id="nome" name="nome" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />

            <label htmlFor="senha" style={{ display: 'block', marginBottom: '0.5rem' }}>Senha:</label>
            <input type="password" id="senha" name="senha" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />

          </div>
        </form>
      </div>
    </div>
  );
};