/** Protege rotas que exigem usuario autenticado. */

import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

/** Redireciona para login quando nao houver sessao valida. */
export function ProtectedRoute() {
  const { user, loading } = useAuth()

  if (loading) {
    return <p className="page-message">Carregando sessao...</p>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
