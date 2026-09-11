/** Provider de autenticacao do frontend. */

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  changePassword as changePasswordRequest,
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  type ChangePasswordPayload,
  type LoginPayload,
  type RegisterPayload,
} from '../services/authService'
import { getAccessToken } from '../services/api'
import type { User } from '../types/api'
import { AuthContext } from './authContext'

type AuthProviderProps = {
  children: ReactNode
}

/** Provider que mantem o estado do usuario autenticado. */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(() => Boolean(getAccessToken()))

  useEffect(() => {
    const token = getAccessToken()
    if (!token) {
      return
    }

    let cancelled = false

    getCurrentUser()
      .then((currentUser) => {
        if (!cancelled) {
          setUser(currentUser)
        }
      })
      .catch(() => {
        logoutUser()
        if (!cancelled) {
          setUser(null)
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (payload: LoginPayload) => {
    await loginUser(payload)
    const current = await getCurrentUser()
    setUser(current)
  }, [])

  const register = useCallback(async (payload: RegisterPayload) => {
    await registerUser(payload)
    await loginUser({ email: payload.email, password: payload.password })
    const current = await getCurrentUser()
    setUser(current)
  }, [])

  const changePassword = useCallback(async (payload: ChangePasswordPayload) => {
    const updated = await changePasswordRequest(payload)
    setUser(updated)
  }, [])

  const logout = useCallback(() => {
    logoutUser()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, changePassword, logout }),
    [user, loading, login, register, changePassword, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
