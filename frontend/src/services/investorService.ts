/** Chamadas HTTP do modulo de investidores. */

import { apiRequest } from './api'
import type { Investor } from '../types/api'

export type InvestorPayload = {
  name: string
  document: string
  email?: string | null
}

export type InvestorUpdatePayload = Partial<InvestorPayload> & {
  is_active?: boolean
}

/** Lista investidores do usuario autenticado. */
export function listInvestors(): Promise<Investor[]> {
  return apiRequest<Investor[]>('/investors')
}

/** Cadastra um investidor. */
export function createInvestor(payload: InvestorPayload): Promise<Investor> {
  return apiRequest<Investor>('/investors', { method: 'POST', body: payload })
}

/** Atualiza um investidor. */
export function updateInvestor(
  investorId: number,
  payload: InvestorUpdatePayload,
): Promise<Investor> {
  return apiRequest<Investor>(`/investors/${investorId}`, {
    method: 'PUT',
    body: payload,
  })
}

/** Desativa um investidor. */
export function deleteInvestor(investorId: number): Promise<Investor> {
  return apiRequest<Investor>(`/investors/${investorId}`, { method: 'DELETE' })
}
