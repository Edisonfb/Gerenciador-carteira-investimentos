/** Chamadas HTTP do modulo de carteiras. */

import { apiRequest } from './api'
import type { Portfolio, PortfolioSummary } from '../types/api'

export type PortfolioPayload = {
  investor_id: number
  name: string
  description?: string | null
}

export type PortfolioUpdatePayload = {
  name?: string
  description?: string | null
  is_active?: boolean
}

/** Lista carteiras do usuario autenticado. */
export function listPortfolios(): Promise<Portfolio[]> {
  return apiRequest<Portfolio[]>('/portfolios')
}

/** Cria uma carteira. */
export function createPortfolio(payload: PortfolioPayload): Promise<Portfolio> {
  return apiRequest<Portfolio>('/portfolios', { method: 'POST', body: payload })
}

/** Atualiza uma carteira. */
export function updatePortfolio(
  portfolioId: number,
  payload: PortfolioUpdatePayload,
): Promise<Portfolio> {
  return apiRequest<Portfolio>(`/portfolios/${portfolioId}`, {
    method: 'PUT',
    body: payload,
  })
}

/** Desativa uma carteira. */
export function deletePortfolio(portfolioId: number): Promise<Portfolio> {
  return apiRequest<Portfolio>(`/portfolios/${portfolioId}`, {
    method: 'DELETE',
  })
}

/** Consulta o resumo consolidado de uma carteira. */
export function getPortfolioSummary(portfolioId: number): Promise<PortfolioSummary> {
  return apiRequest<PortfolioSummary>(`/portfolios/${portfolioId}/summary`)
}
