/** Tela de pre-cadastro e gestao de clientes pelo analista. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { ErrorBanner } from '../components/ErrorBanner'
import {
  createInvestor,
  deleteInvestor,
  listInvestors,
  regenerateInvestorAccess,
} from '../services/investorService'
import type { Investor } from '../types/api'

const emptyForm = {
  first_name: '',
  last_name: '',
  rg: '',
  document: '',
  email: '',
  phone: '',
  address: '',
}

/** Lista, pre-cadastra e reemite acesso de clientes. */
export function InvestorsPage() {
  const [investors, setInvestors] = useState<Investor[]>([])
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [generatedPassword, setGeneratedPassword] = useState<string | null>(null)
  const [generatedEmail, setGeneratedEmail] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    listInvestors()
      .then((data) => {
        if (!cancelled) {
          setInvestors(data)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Erro ao carregar.')
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

  async function refresh() {
    setError(null)
    setInvestors(await listInvestors())
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setGeneratedPassword(null)
    try {
      const created = await createInvestor(form)
      setGeneratedPassword(created.temporary_password)
      setGeneratedEmail(created.email)
      setForm(emptyForm)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao cadastrar.')
    }
  }

  async function handleDeactivate(id: number) {
    setError(null)
    try {
      await deleteInvestor(id)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao desativar.')
    }
  }

  async function handleRegenerate(id: number) {
    setError(null)
    setGeneratedPassword(null)
    try {
      const access = await regenerateInvestorAccess(id)
      setGeneratedPassword(access.temporary_password)
      setGeneratedEmail(access.email)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao reemitir acesso.')
    }
  }

  return (
    <section className="page">
      <h1>Clientes</h1>
      <p className="muted">
        Pre-cadastre clientes e libere acesso com senha temporaria.
      </p>
      <ErrorBanner message={error} />

      {generatedPassword && (
        <div className="panel">
          <h2>Acesso gerado</h2>
          <p>
            Email: <strong>{generatedEmail}</strong>
          </p>
          <p>
            Senha temporaria: <strong>{generatedPassword}</strong>
          </p>
          <p className="muted">
            Guarde agora: a senha nao sera exibida novamente. O cliente deve
            troca-la no primeiro login.
          </p>
        </div>
      )}

      <form className="panel form-grid" onSubmit={handleSubmit}>
        <h2>Novo cliente</h2>
        <label>
          Nome
          <input
            value={form.first_name}
            onChange={(e) => setForm({ ...form, first_name: e.target.value })}
            required
          />
        </label>
        <label>
          Sobrenome
          <input
            value={form.last_name}
            onChange={(e) => setForm({ ...form, last_name: e.target.value })}
            required
          />
        </label>
        <label>
          RG
          <input
            value={form.rg}
            onChange={(e) => setForm({ ...form, rg: e.target.value })}
            required
          />
        </label>
        <label>
          CPF
          <input
            value={form.document}
            onChange={(e) => setForm({ ...form, document: e.target.value })}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
        </label>
        <label>
          Celular
          <input
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
            required
          />
        </label>
        <label>
          Endereco completo
          <input
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
            required
          />
        </label>
        <button type="submit" className="button">
          Pre-cadastrar e gerar acesso
        </button>
      </form>

      <div className="panel">
        <h2>Lista</h2>
        {loading ? (
          <p className="muted">Carregando...</p>
        ) : investors.length === 0 ? (
          <p className="muted">Nenhum cliente cadastrado.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>CPF</th>
                <th>Email</th>
                <th>Celular</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {investors.map((investor) => (
                <tr key={investor.id}>
                  <td>{investor.name}</td>
                  <td>{investor.document}</td>
                  <td>{investor.email}</td>
                  <td>{investor.phone}</td>
                  <td>{investor.is_active ? 'Ativo' : 'Inativo'}</td>
                  <td>
                    {investor.is_active && (
                      <>
                        <button
                          type="button"
                          className="button ghost"
                          onClick={() => void handleRegenerate(investor.id)}
                        >
                          Reemitir senha
                        </button>
                        <button
                          type="button"
                          className="button ghost"
                          onClick={() => void handleDeactivate(investor.id)}
                        >
                          Desativar
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}
