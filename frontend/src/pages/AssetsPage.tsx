/** Tela de gerenciamento de ativos financeiros. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { ErrorBanner } from '../components/ErrorBanner'
import {
  createAsset,
  deleteAsset,
  listAssets,
} from '../services/assetService'
import type { Asset } from '../types/api'

const ASSET_TYPES = [
  'acao',
  'fundo_imobiliario',
  'renda_fixa',
  'etf',
  'cripto',
  'outro',
]

/** Lista, cria e desativa ativos. */
export function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [symbol, setSymbol] = useState('')
  const [name, setName] = useState('')
  const [assetType, setAssetType] = useState('acao')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    listAssets()
      .then((data) => {
        if (!cancelled) {
          setAssets(data)
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
    setAssets(await listAssets())
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await createAsset({
        symbol,
        name,
        asset_type: assetType,
      })
      setSymbol('')
      setName('')
      setAssetType('acao')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao cadastrar ativo.')
    }
  }

  async function handleDeactivate(id: number) {
    setError(null)
    try {
      await deleteAsset(id)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao desativar.')
    }
  }

  return (
    <section className="page">
      <h1>Ativos</h1>
      <ErrorBanner message={error} />

      <form className="panel form-grid" onSubmit={handleSubmit}>
        <h2>Novo ativo</h2>
        <label>
          Simbolo
          <input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            required
          />
        </label>
        <label>
          Nome
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Tipo
          <select
            value={assetType}
            onChange={(e) => setAssetType(e.target.value)}
          >
            {ASSET_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className="button">
          Cadastrar
        </button>
      </form>

      <div className="panel">
        <h2>Lista</h2>
        {loading ? (
          <p className="muted">Carregando...</p>
        ) : assets.length === 0 ? (
          <p className="muted">Nenhum ativo cadastrado.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Simbolo</th>
                <th>Nome</th>
                <th>Tipo</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id}>
                  <td>{asset.symbol}</td>
                  <td>{asset.name}</td>
                  <td>{asset.asset_type}</td>
                  <td>{asset.is_active ? 'Ativo' : 'Inativo'}</td>
                  <td>
                    {asset.is_active && (
                      <button
                        type="button"
                        className="button ghost"
                        onClick={() => void handleDeactivate(asset.id)}
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
