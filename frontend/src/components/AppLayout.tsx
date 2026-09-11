/** Layout principal da area autenticada. */

import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const analystLinks = [
  { to: '/', label: 'Inicio', end: true },
  { to: '/investors', label: 'Clientes', end: false },
  { to: '/portfolios', label: 'Carteiras', end: false },
  { to: '/assets', label: 'Ativos', end: false },
  { to: '/transactions', label: 'Transacoes', end: false },
]

const clientLinks = [
  { to: '/', label: 'Inicio', end: true },
  { to: '/portfolios', label: 'Minhas carteiras', end: false },
  { to: '/assets', label: 'Ativos', end: false },
  { to: '/transactions', label: 'Transacoes', end: false },
]

/** Barra de navegacao e area de conteudo das telas autenticadas. */
export function AppLayout() {
  const { user, logout } = useAuth()
  const links = user?.role === 'client' ? clientLinks : analystLinks
  const roleLabel = user?.role === 'client' ? 'Cliente' : 'Analista'

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="brand">Carteiras</p>
          <p className="muted">
            {user?.name} · {roleLabel}
          </p>
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
