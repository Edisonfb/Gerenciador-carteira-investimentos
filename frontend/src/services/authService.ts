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

/** Cadastra um novo usuario. */
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

/** Remove o token local e encerra a sessao no frontend. */
export function logoutUser(): void {
  setAccessToken(null)
}
