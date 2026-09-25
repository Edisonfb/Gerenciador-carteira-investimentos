// frontend/src/components/LayoutPadrao.tsx
import React from 'react';
import { Outlet } from 'react-router-dom';

export const LayoutLogin: React.FC = () => {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
      {/* Cabeçalho de Navegação */}
      <header style={{ background: '#1e293b', color: '#fff', padding: '1rem 2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: '1.25rem' }}>Meta Ações</h2>
        </div>
      </header>

      {/* Renderização da parte principal, das páginas filhas */}
      <main style={{ flex: 1, padding: '2rem', background: '#f8fafc' }}>

        <Outlet />
      </main>

      {/* Renderização do rodape */}
      <footer style={{ background: '#0f172a', color: '#94a3b8', textAlign: 'center', padding: '1rem', fontSize: '0.875rem' }}>
        <p style={{ margin: 0 }}>© Meta Ações - Gerenciador de Carteira de Investimentos</p>
      </footer>
    </div>
  );
};