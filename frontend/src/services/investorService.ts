/** Chamadas HTTP do modulo de investidores. */

import { apiRequest } from './api'
import type { Investor, InvestorAccess } from '../types/api'

export type InvestorPayload = {
  first_name: string
  last_name: string
  rg: string
  document: string
  email: string
  phone: string
  address: string
}

export type InvestorUpdatePayload = Partial<InvestorPayload> & {
  is_active?: boolean
}

/** Lista investidores acessiveis ao usuario autenticado. */
export function listInvestors(): Promise<Investor[]> {
  return apiRequest<Investor[]>('/investors')
}

/** Pre-cadastra cliente e retorna senha temporaria. */
export function createInvestor(payload: InvestorPayload): Promise<InvestorAccess> {
  return apiRequest<InvestorAccess>('/investors', { method: 'POST', body: payload })
}

/** Reemite senha temporaria do cliente. */
export function regenerateInvestorAccess(
  investorId: number,
): Promise<InvestorAccess> {
  return apiRequest<InvestorAccess>(`/investors/${investorId}/regenerate-access`, {
    method: 'POST',
  })
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
