import type { MarketDataResponse } from '../types/market'

const BASE = '/api/v1'

export async function fetchHistory(
  symbol: string,
  period = '1y',
  interval = '1d',
): Promise<MarketDataResponse> {
  const res = await fetch(`${BASE}/market/${symbol}/history?period=${period}&interval=${interval}`)
  if (!res.ok) throw new Error(`Market history error: ${res.statusText}`)
  return res.json()
}

export async function fetchLatest(symbol: string): Promise<MarketDataResponse> {
  const res = await fetch(`${BASE}/market/${symbol}/latest`)
  if (!res.ok) throw new Error(`Market latest error: ${res.statusText}`)
  return res.json()
}
