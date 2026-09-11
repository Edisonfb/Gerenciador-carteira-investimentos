/** Layout principal da area autenticada. */

import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const links = [
  { to: '/', label: 'Inicio', end: true },
  { to: '/investors', label: 'Investidores' },
  { to: '/portfolios', label: 'Carteiras' },
  { to: '/assets', label: 'Ativos' },
  { to: '/transactions', label: 'Transacoes' },
]

/** Barra de navegacao e area de conteudo das telas autenticadas. */
export function AppLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="brand">Carteiras</p>
          <p className="muted">{user?.name}</p>
        </div>
        <nav className="nav">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                isActive ? 'nav-link active' : 'nav-link'
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <button type="button" className="button ghost" onClick={logout}>
          Sair
        </button>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
