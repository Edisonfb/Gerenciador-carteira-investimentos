/** Tela inicial autenticada. */

import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

/** Visao geral com atalhos para as areas principais. */
export function HomePage() {
  const { user } = useAuth()

  return (
    <section className="page">
      <h1>Ola, {user?.name}</h1>
      <p className="muted">
        Gerencie investidores, carteiras, ativos e transacoes em um so lugar.
      </p>
      <div className="shortcut-grid">
        <Link className="shortcut" to="/investors">
          Investidores
        </Link>
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
