/** Protege rotas que exigem usuario autenticado. */

import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

/** Redireciona para login ou troca de senha quando necessario. */
export function ProtectedRoute() {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <p className="page-message">Carregando sessao...</p>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (
    user.must_change_password &&
    location.pathname !== '/change-password'
  ) {
    return <Navigate to="/change-password" replace />
  }

  return <Outlet />
}
