/** Chamadas HTTP do modulo de ativos financeiros. */

import { apiRequest } from './api'
import type { Asset } from '../types/api'

export type AssetPayload = {
  symbol: string
  name: string
  asset_type: string
}

export type AssetUpdatePayload = Partial<AssetPayload> & {
  is_active?: boolean
}

/** Lista ativos cadastrados. */
export function listAssets(): Promise<Asset[]> {
  return apiRequest<Asset[]>('/assets')
}

/** Cadastra um ativo. */
export function createAsset(payload: AssetPayload): Promise<Asset> {
  return apiRequest<Asset>('/assets', { method: 'POST', body: payload })
}

/** Atualiza um ativo. */
export function updateAsset(
  assetId: number,
  payload: AssetUpdatePayload,
): Promise<Asset> {
  return apiRequest<Asset>(`/assets/${assetId}`, {
    method: 'PUT',
    body: payload,
  })
}

/** Desativa um ativo. */
export function deleteAsset(assetId: number): Promise<Asset> {
  return apiRequest<Asset>(`/assets/${assetId}`, { method: 'DELETE' })
}
