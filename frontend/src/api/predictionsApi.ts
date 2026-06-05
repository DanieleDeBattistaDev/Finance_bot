import type { PredictionResponse } from '../types/prediction'

const BASE = '/api/v1'

export async function fetchPrediction(
  symbol: string,
  includeSentiment = true,
): Promise<PredictionResponse> {
  const res = await fetch(`${BASE}/predictions/${symbol}?include_sentiment=${includeSentiment}`)
  if (!res.ok) throw new Error(`Prediction error: ${res.statusText}`)
  return res.json()
}

export async function triggerTraining(symbol: string): Promise<{ message: string }> {
  const res = await fetch(`${BASE}/predictions/${symbol}/train`, { method: 'POST' })
  if (!res.ok) throw new Error(`Training error: ${res.statusText}`)
  return res.json()
}
