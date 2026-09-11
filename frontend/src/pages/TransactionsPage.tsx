/** Tela de gerenciamento de transacoes. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { ErrorBanner } from '../components/ErrorBanner'
import { listAssets } from '../services/assetService'
import { listPortfolios } from '../services/portfolioService'
import {
  createTransaction,
  deleteTransaction,
  listTransactions,
} from '../services/transactionService'
import type { Asset, Portfolio, Transaction } from '../types/api'

const TRANSACTION_TYPES = [
  'compra',
  'venda',
  'deposito',
  'retirada',
  'rendimento',
  'taxa',
]

const ASSET_REQUIRED = new Set(['compra', 'venda', 'rendimento'])

/** Lista, registra e remove transacoes. */
export function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [assets, setAssets] = useState<Asset[]>([])
  const [portfolioId, setPortfolioId] = useState('')
  const [assetId, setAssetId] = useState('')
  const [transactionType, setTransactionType] = useState('compra')
  const [quantity, setQuantity] = useState('1')
  const [unitPrice, setUnitPrice] = useState('0')
  const [fees, setFees] = useState('0')
  const [transactionDate, setTransactionDate] = useState(
    new Date().toISOString().slice(0, 16),
  )
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    Promise.all([listTransactions(), listPortfolios(), listAssets()])
      .then(([txData, portfolioData, assetData]) => {
        if (!cancelled) {
          setTransactions(txData)
          setPortfolios(portfolioData.filter((item) => item.is_active))
          setAssets(assetData.filter((item) => item.is_active))
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
    const [txData, portfolioData, assetData] = await Promise.all([
      listTransactions(),
      listPortfolios(),
      listAssets(),
    ])
    setTransactions(txData)
    setPortfolios(portfolioData.filter((item) => item.is_active))
    setAssets(assetData.filter((item) => item.is_active))
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await createTransaction({
        portfolio_id: Number(portfolioId),
        asset_id: ASSET_REQUIRED.has(transactionType)
          ? Number(assetId)
          : assetId
            ? Number(assetId)
            : null,
        transaction_type: transactionType,
        quantity,
        unit_price: unitPrice,
        fees,
        transaction_date: new Date(transactionDate).toISOString(),
        notes: notes || null,
      })
      setQuantity('1')
      setUnitPrice('0')
      setFees('0')
      setNotes('')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao registrar.')
    }
  }

  async function handleDelete(id: number) {
    setError(null)
    try {
      await deleteTransaction(id)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao remover.')
    }
  }

  return (
    <section className="page">
      <h1>Transacoes</h1>
      <ErrorBanner message={error} />

      <form className="panel form-grid" onSubmit={handleSubmit}>
        <h2>Nova transacao</h2>
        <label>
          Carteira
          <select
            value={portfolioId}
            onChange={(e) => setPortfolioId(e.target.value)}
            required
          >
            <option value="">Selecione</option>
            {portfolios.map((portfolio) => (
              <option key={portfolio.id} value={portfolio.id}>
                {portfolio.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Tipo
          <select
            value={transactionType}
            onChange={(e) => setTransactionType(e.target.value)}
          >
            {TRANSACTION_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>
        <label>
          Ativo
          <select
            value={assetId}
            onChange={(e) => setAssetId(e.target.value)}
            required={ASSET_REQUIRED.has(transactionType)}
          >
            <option value="">Selecione</option>
            {assets.map((asset) => (
              <option key={asset.id} value={asset.id}>
                {asset.symbol} - {asset.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Quantidade
          <input
            type="number"
            min="0"
            step="any"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            required
          />
        </label>
        <label>
          Preco unitario
          <input
            type="number"
            min="0"
            step="any"
            value={unitPrice}
            onChange={(e) => setUnitPrice(e.target.value)}
            required
          />
        </label>
        <label>
          Taxas
          <input
            type="number"
            min="0"
            step="any"
            value={fees}
            onChange={(e) => setFees(e.target.value)}
          />
        </label>
        <label>
          Data
          <input
            type="datetime-local"
            value={transactionDate}
            onChange={(e) => setTransactionDate(e.target.value)}
            required
          />
        </label>
        <label>
          Observacoes
          <input value={notes} onChange={(e) => setNotes(e.target.value)} />
        </label>
        <button type="submit" className="button">
          Registrar
        </button>
      </form>

      <div className="panel">
        <h2>Historico</h2>
        {loading ? (
          <p className="muted">Carregando...</p>
        ) : transactions.length === 0 ? (
          <p className="muted">Nenhuma transacao registrada.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Carteira</th>
                <th>Tipo</th>
                <th>Ativo</th>
                <th>Qtd</th>
                <th>Preco</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id}>
                  <td>{new Date(tx.transaction_date).toLocaleString()}</td>
                  <td>{tx.portfolio_id}</td>
                  <td>{tx.transaction_type}</td>
                  <td>{tx.asset_id ?? '-'}</td>
                  <td>{tx.quantity}</td>
                  <td>{tx.unit_price}</td>
                  <td>
                    <button
                      type="button"
                      className="button ghost"
                      onClick={() => void handleDelete(tx.id)}
                    >
                      Remover
                    </button>
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
