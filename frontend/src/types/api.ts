/** Tipos compartilhados alinhados ao contrato da API. */

export type User = {
  id: number
  name: string
  email: string
  created_at: string
  updated_at: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
}

export type Investor = {
  id: number
  user_id: number
  name: string
  document: string
  email: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type Portfolio = {
  id: number
  investor_id: number
  name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type Asset = {
  id: number
  symbol: string
  name: string
  asset_type: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type Transaction = {
  id: number
  portfolio_id: number
  asset_id: number | null
  transaction_type: string
  quantity: string
  unit_price: string
  transaction_date: string
  fees: string
  notes: string | null
  created_at: string
  updated_at: string
}

export type PortfolioPosition = {
  asset_id: number
  symbol: string
  name: string
  quantity: string
  average_price: string
  total_invested: string
}

export type PortfolioSummary = {
  portfolio_id: number
  portfolio_name: string
  total_invested: string
  total_fees: string
  cash_flow: string
  positions: PortfolioPosition[]
  transactions_count: number
}

export type ApiError = {
  detail: string
}
