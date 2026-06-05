export interface ModelOutput {
  direction: 'up' | 'down'
  probability: number
}

export interface PredictionResponse {
  symbol: string
  prediction: 'up' | 'down'
  confidence: number
  expected_return: number
  xgboost: ModelOutput
  lstm: ModelOutput
}
