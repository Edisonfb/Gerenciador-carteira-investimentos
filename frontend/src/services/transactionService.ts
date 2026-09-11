/** Chamadas HTTP do modulo de transacoes. */

import { apiRequest } from './api'
import type { Transaction } from '../types/api'

export type TransactionPayload = {
  portfolio_id: number
  asset_id?: number | null
  transaction_type: string
  quantity: number | string
  unit_price: number | string
  transaction_date: string
  fees?: number | string
  notes?: string | null
}

export type TransactionUpdatePayload = Partial<
  Omit<TransactionPayload, 'portfolio_id'>
>

/** Lista transacoes do usuario autenticado. */
export function listTransactions(): Promise<Transaction[]> {
  return apiRequest<Transaction[]>('/transactions')
}

/** Registra uma transacao. */
export function createTransaction(
  payload: TransactionPayload,
): Promise<Transaction> {
  return apiRequest<Transaction>('/transactions', {
    method: 'POST',
    body: payload,
  })
}

/** Atualiza uma transacao. */
export function updateTransaction(
  transactionId: number,
  payload: TransactionUpdatePayload,
): Promise<Transaction> {
  return apiRequest<Transaction>(`/transactions/${transactionId}`, {
    method: 'PUT',
    body: payload,
  })
}

/** Remove uma transacao. */
export function deleteTransaction(transactionId: number): Promise<void> {
  return apiRequest<void>(`/transactions/${transactionId}`, {
    method: 'DELETE',
  })
}
