/** Restringe rotas ao perfil de analista. */

import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

/** Bloqueia acesso de clientes a funcionalidades exclusivas do analista. */
export function AnalystRoute() {
  const { user } = useAuth()

  if (user?.role !== 'analyst') {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
