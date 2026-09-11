/** Testes do authService alinhados ao contrato da API. */

import { afterEach, describe, expect, it, vi } from 'vitest'
import { getAccessToken, setAccessToken } from '../../../frontend/src/services/api'
import {
  loginUser,
  logoutUser,
  registerUser,
} from '../../../frontend/src/services/authService'

describe('authService', () => {
  afterEach(() => {
    localStorage.clear()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('register chama POST /auth/register sem Authorization', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: 1,
          name: 'Maria',
          email: 'maria@example.com',
          created_at: '2026-01-10T10:00:00',
          updated_at: '2026-01-10T10:00:00',
        }),
        { status: 201, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const user = await registerUser({
      name: 'Maria',
      email: 'maria@example.com',
      password: 'senha123',
    })

    expect(user.email).toBe('maria@example.com')
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/auth/register',
      expect.objectContaining({
        method: 'POST',
        headers: expect.not.objectContaining({
          Authorization: expect.any(String),
        }),
      }),
    )
  })

  it('login persiste o access_token retornado', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: 'token-login',
          token_type: 'bearer',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    vi.stubGlobal('fetch', fetchMock)

    const token = await loginUser({
      email: 'maria@example.com',
      password: 'senha123',
    })

    expect(token.access_token).toBe('token-login')
    expect(getAccessToken()).toBe('token-login')
  })

  it('logout remove o token local', () => {
    setAccessToken('token-temp')
    logoutUser()
    expect(getAccessToken()).toBeNull()
  })
})
