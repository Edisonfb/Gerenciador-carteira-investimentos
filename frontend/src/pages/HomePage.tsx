/** Tela inicial autenticada. */

import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

/** Visao geral com atalhos conforme o perfil do usuario. */
export function HomePage() {
  const { user } = useAuth()
  const isAnalyst = user?.role === 'analyst'

  return (
    <section className="page">
      <h1>Ola, {user?.name}</h1>
      <p className="muted">
        {isAnalyst
          ? 'Pre-cadastre clientes e acompanhe carteiras, ativos e transacoes.'
          : 'Gerencie suas carteiras, ativos e transacoes.'}
      </p>
      <div className="shortcut-grid">
        {isAnalyst && (
          <Link className="shortcut" to="/investors">
            Clientes
          </Link>
        )}
        <Link className="shortcut" to="/portfolios">
          Carteiras
        </Link>
        <Link className="shortcut" to="/assets">
          Ativos
        </Link>
        <Link className="shortcut" to="/transactions">
          Transacoes
        </Link>
      </div>
    </section>
  )
}
