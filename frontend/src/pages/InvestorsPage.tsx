/** Tela de gerenciamento de investidores. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { ErrorBanner } from '../components/ErrorBanner'
import {
  createInvestor,
  deleteInvestor,
  listInvestors,
} from '../services/investorService'
import type { Investor } from '../types/api'

/** Lista, cria e desativa investidores. */
export function InvestorsPage() {
  const [investors, setInvestors] = useState<Investor[]>([])
  const [name, setName] = useState('')
  const [document, setDocument] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

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
    try {
      await createInvestor({
        name,
        document,
        email: email || null,
      })
      setName('')
      setDocument('')
      setEmail('')
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

  return (
    <section className="page">
      <h1>Investidores</h1>
      <ErrorBanner message={error} />

      <form className="panel form-grid" onSubmit={handleSubmit}>
        <h2>Novo investidor</h2>
        <label>
          Nome
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Documento
          <input
            value={document}
            onChange={(e) => setDocument(e.target.value)}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <button type="submit" className="button">
          Cadastrar
        </button>
      </form>

      <div className="panel">
        <h2>Lista</h2>
        {loading ? (
          <p className="muted">Carregando...</p>
        ) : investors.length === 0 ? (
          <p className="muted">Nenhum investidor cadastrado.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Documento</th>
                <th>Email</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {investors.map((investor) => (
                <tr key={investor.id}>
                  <td>{investor.name}</td>
                  <td>{investor.document}</td>
                  <td>{investor.email ?? '-'}</td>
                  <td>{investor.is_active ? 'Ativo' : 'Inativo'}</td>
                  <td>
                    {investor.is_active && (
                      <button
                        type="button"
                        className="button ghost"
                        onClick={() => void handleDeactivate(investor.id)}
                      >
                        Desativar
                      </button>
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
