/** Testes do cliente HTTP base do frontend. */

import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  apiRequest,
  getAccessToken,
  setAccessToken,
} from '../../../frontend/src/services/api'

describe('api client', () => {
  afterEach(() => {
    localStorage.clear()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('persiste e remove o access token', () => {
    expect(getAccessToken()).toBeNull()
    setAccessToken('token-abc')
    expect(getAccessToken()).toBe('token-abc')
    setAccessToken(null)
    expect(getAccessToken()).toBeNull()
  })

  it('envia Authorization quando houver token', async () => {
    setAccessToken('jwt-123')
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await apiRequest<{ ok: boolean }>('/health')

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/health',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Authorization: 'Bearer jwt-123',
        }),
      }),
    )
  })

  it('propaga detail de erro da API', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Nao autenticado.' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiRequest('/auth/me')).rejects.toThrow('Nao autenticado.')
  })

  it('trata resposta 204 sem corpo', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiRequest<void>('/transactions/1', { method: 'DELETE' })).resolves.toBeUndefined()
  })
})
