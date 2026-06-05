export type Action = 'buy' | 'sell' | 'hold'
export type Timeframe = 'short' | 'medium' | 'long'
export type RiskLevel = 'low' | 'medium' | 'high'
export type StrategyType = 'scalping' | 'swing' | 'long_term'

export interface SignalSource {
  name: string
  vote: 'bullish' | 'bearish' | 'neutral'
  weight: number
  reason: string
}

export interface SignalResponse {
  symbol: string
  action: Action
  confidence: number
  reasoning: string[]
  sources: SignalSource[]
  timeframe: Timeframe
  risk_level: RiskLevel
  strategy_type: StrategyType
  generated_at: string
}
