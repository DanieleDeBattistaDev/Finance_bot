import type { RiskLevel, SignalResponse, StrategyType, Timeframe } from '../types/signal'

const BASE = '/api/v1'

export async function fetchSignal(
  symbol: string,
  timeframe: Timeframe = 'medium',
  riskLevel: RiskLevel = 'medium',
  strategyType: StrategyType = 'swing',
): Promise<SignalResponse> {
  const params = new URLSearchParams({
    timeframe,
    risk_level: riskLevel,
    strategy_type: strategyType,
  })
  const res = await fetch(`${BASE}/signals/${symbol}?${params}`)
  if (!res.ok) throw new Error(`Signal error: ${res.statusText}`)
  return res.json()
}
