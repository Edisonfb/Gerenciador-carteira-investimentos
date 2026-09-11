/** Contexto React de autenticacao. */

import { createContext } from 'react'
import type {
  ChangePasswordPayload,
  LoginPayload,
  RegisterPayload,
} from '../services/authService'
import type { User } from '../types/api'

export type AuthContextValue = {
  user: User | null
  loading: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  changePassword: (payload: ChangePasswordPayload) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
