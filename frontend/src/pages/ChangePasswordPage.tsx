/** Tela de troca de senha obrigatoria ou voluntaria. */

import { useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { ErrorBanner } from '../components/ErrorBanner'
import { useAuth } from '../hooks/useAuth'

/** Permite o usuario definir uma nova senha. */
export function ChangePasswordPage() {
  const { user, changePassword, logout } = useAuth()
  const navigate = useNavigate()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (!user) {
    return <Navigate to="/login" replace />
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao trocar senha.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Trocar senha</h1>
        <p className="muted">
          {user.must_change_password
            ? 'Acesse com a senha temporaria e defina uma nova senha para continuar.'
            : 'Atualize sua senha de acesso.'}
        </p>
        <ErrorBanner message={error} />
        <label>
          Senha atual
          <input
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            minLength={6}
            required
          />
        </label>
        <label>
          Nova senha
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            minLength={6}
            required
          />
        </label>
        <button type="submit" className="button" disabled={submitting}>
          {submitting ? 'Salvando...' : 'Salvar senha'}
        </button>
        <button type="button" className="button ghost" onClick={logout}>
          Sair
        </button>
      </form>
    </div>
  )
}
