/** Tela de resumo consolidado de uma carteira. */

import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ErrorBanner } from '../components/ErrorBanner'
import { getPortfolioSummary } from '../services/portfolioService'
import type { PortfolioSummary } from '../types/api'

/** Consulta e exibe o resumo de uma carteira. */
export function PortfolioSummaryPage() {
  const { portfolioId } = useParams()
  const [summary, setSummary] = useState<PortfolioSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!portfolioId) {
      return
    }

    let cancelled = false

    getPortfolioSummary(Number(portfolioId))
      .then((data) => {
        if (!cancelled) {
          setSummary(data)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Erro ao carregar resumo.')
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
  }, [portfolioId])

  return (
    <section className="page">
      <Link to="/portfolios" className="back-link">
        Voltar para carteiras
      </Link>
      <h1>Resumo da carteira</h1>
      <ErrorBanner message={error} />
      {!portfolioId && <ErrorBanner message="Carteira invalida." />}

      {loading && <p className="muted">Carregando...</p>}

      {summary && (
        <>
          <div className="stats">
            <div>
              <p className="muted">Carteira</p>
              <strong>{summary.portfolio_name}</strong>
            </div>
            <div>
              <p className="muted">Total investido</p>
              <strong>{summary.total_invested}</strong>
            </div>
            <div>
              <p className="muted">Taxas</p>
              <strong>{summary.total_fees}</strong>
            </div>
            <div>
              <p className="muted">Fluxo de caixa</p>
              <strong>{summary.cash_flow}</strong>
            </div>
            <div>
              <p className="muted">Transacoes</p>
              <strong>{summary.transactions_count}</strong>
            </div>
          </div>

          <div className="panel">
            <h2>Posicoes</h2>
            {summary.positions.length === 0 ? (
              <p className="muted">Nenhuma posicao aberta.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Simbolo</th>
                    <th>Nome</th>
                    <th>Quantidade</th>
                    <th>Preco medio</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.positions.map((position) => (
                    <tr key={position.asset_id}>
                      <td>{position.symbol}</td>
                      <td>{position.name}</td>
                      <td>{position.quantity}</td>
                      <td>{position.average_price}</td>
                      <td>{position.total_invested}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </section>
  )
}
