/** Cliente HTTP base para consumo da API. */

import type { ApiError } from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const TOKEN_KEY = 'access_token'

/** Recupera o token JWT salvo no navegador. */
export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/** Persiste o token JWT no navegador. */
export function setAccessToken(token: string | null): void {
  if (token === null) {
    localStorage.removeItem(TOKEN_KEY)
    return
  }
  localStorage.setItem(TOKEN_KEY, token)
}

type RequestOptions = {
  method?: string
  body?: unknown
  auth?: boolean
}

/**
 * Executa uma requisicao HTTP para a API.
 * Lanca Error com a mensagem retornada em `detail` quando a resposta falha.
 */
export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = 'GET', body, auth = true } = options
  const headers: Record<string, string> = {
    Accept: 'application/json',
  }

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  if (auth) {
    const token = getAccessToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const data = (await response.json().catch(() => null)) as T | ApiError | null

  if (!response.ok) {
    const detail =
      data && typeof data === 'object' && 'detail' in data
        ? String((data as ApiError).detail)
        : `Erro HTTP ${response.status}`
    throw new Error(detail)
  }

  return data as T
}
