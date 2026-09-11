/** Tela de gerenciamento de carteiras. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { ErrorBanner } from '../components/ErrorBanner'
import { listInvestors } from '../services/investorService'
import {
  createPortfolio,
  deletePortfolio,
  listPortfolios,
} from '../services/portfolioService'
import type { Investor, Portfolio } from '../types/api'

/** Lista, cria e desativa carteiras. */
export function PortfoliosPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [investors, setInvestors] = useState<Investor[]>([])
  const [investorId, setInvestorId] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    Promise.all([listPortfolios(), listInvestors()])
      .then(([portfolioData, investorData]) => {
        if (!cancelled) {
          setPortfolios(portfolioData)
          setInvestors(investorData.filter((item) => item.is_active))
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
    const [portfolioData, investorData] = await Promise.all([
      listPortfolios(),
      listInvestors(),
    ])
    setPortfolios(portfolioData)
    setInvestors(investorData.filter((item) => item.is_active))
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await createPortfolio({
        investor_id: Number(investorId),
        name,
        description: description || null,
      })
      setName('')
      setDescription('')
      setInvestorId('')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar carteira.')
    }
  }

  async function handleDeactivate(id: number) {
    setError(null)
    try {
      await deletePortfolio(id)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao desativar.')
    }
  }

  return (
    <section className="page">
      <h1>Carteiras</h1>
      <ErrorBanner message={error} />

      <form className="panel form-grid" onSubmit={handleSubmit}>
        <h2>Nova carteira</h2>
        <label>
          Investidor
          <select
            value={investorId}
            onChange={(e) => setInvestorId(e.target.value)}
            required
          >
            <option value="">Selecione</option>
            {investors.map((investor) => (
              <option key={investor.id} value={investor.id}>
                {investor.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Nome
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Descricao
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
        <button type="submit" className="button">
          Criar
        </button>
      </form>

      <div className="panel">
        <h2>Lista</h2>
        {loading ? (
          <p className="muted">Carregando...</p>
        ) : portfolios.length === 0 ? (
          <p className="muted">Nenhuma carteira cadastrada.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Investidor</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {portfolios.map((portfolio) => (
                <tr key={portfolio.id}>
                  <td>{portfolio.name}</td>
                  <td>{portfolio.investor_id}</td>
                  <td>{portfolio.is_active ? 'Ativa' : 'Inativa'}</td>
                  <td className="row-actions">
                    <Link to={`/portfolios/${portfolio.id}/summary`}>Resumo</Link>
                    {portfolio.is_active && (
                      <button
                        type="button"
                        className="button ghost"
                        onClick={() => void handleDeactivate(portfolio.id)}
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
