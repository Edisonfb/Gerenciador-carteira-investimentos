/** Tela de cadastro de usuario. */

import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { ErrorBanner } from '../components/ErrorBanner'
import { useAuth } from '../hooks/useAuth'

/** Permite cadastrar e autenticar um novo usuario. */
export function RegisterPage() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await register({ name, email, password })
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha no cadastro.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Criar conta</h1>
        <p className="muted">Cadastre-se para gerenciar carteiras.</p>
        <ErrorBanner message={error} />
        <label>
          Nome
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            minLength={2}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={6}
            required
          />
        </label>
        <button type="submit" className="button" disabled={submitting}>
          {submitting ? 'Cadastrando...' : 'Cadastrar'}
        </button>
        <p className="muted">
          Ja tem conta? <Link to="/login">Entrar</Link>
        </p>
      </form>
    </div>
  )
}
