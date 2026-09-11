/** Chamadas HTTP do modulo de autenticacao. */

import { apiRequest, setAccessToken } from './api'
import type { TokenResponse, User } from '../types/api'

export type RegisterPayload = {
  name: string
  email: string
  password: string
}

export type LoginPayload = {
  email: string
  password: string
}

export type ChangePasswordPayload = {
  current_password: string
  new_password: string
}

/** Cadastra um novo analista. */
export function registerUser(payload: RegisterPayload): Promise<User> {
  return apiRequest<User>('/auth/register', {
    method: 'POST',
    body: payload,
    auth: false,
  })
}

/** Autentica o usuario e persiste o token. */
export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  const token = await apiRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    body: payload,
    auth: false,
  })
  setAccessToken(token.access_token)
  return token
}

/** Retorna o usuario autenticado. */
export function getCurrentUser(): Promise<User> {
  return apiRequest<User>('/auth/me')
}

/** Troca a senha do usuario autenticado. */
export function changePassword(payload: ChangePasswordPayload): Promise<User> {
  return apiRequest<User>('/auth/change-password', {
    method: 'POST',
    body: payload,
  })
}

/** Remove o token local e encerra a sessao no frontend. */
export function logoutUser(): void {
  setAccessToken(null)
}
