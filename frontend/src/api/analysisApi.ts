import type { FundamentalAnalysisResponse, TechnicalAnalysisResponse } from '../types/analysis'

const BASE = '/api/v1'

export async function fetchTechnical(
  symbol: string,
  period = '1y',
  interval = '1d',
): Promise<TechnicalAnalysisResponse> {
  const res = await fetch(`${BASE}/analysis/${symbol}/technical?period=${period}&interval=${interval}`)
  if (!res.ok) throw new Error(`Technical analysis error: ${res.statusText}`)
  return res.json()
}

export async function fetchFundamental(symbol: string): Promise<FundamentalAnalysisResponse> {
  const res = await fetch(`${BASE}/analysis/${symbol}/fundamental`)
  if (!res.ok) throw new Error(`Fundamental analysis error: ${res.statusText}`)
  return res.json()
}
