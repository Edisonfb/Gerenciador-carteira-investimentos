/** Hook para acessar o contexto de autenticacao. */

import { useContext } from 'react'
import { AuthContext, type AuthContextValue } from './authContext'

/** Retorna o estado e as acoes de autenticacao. */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider.')
  }
  return context
}
