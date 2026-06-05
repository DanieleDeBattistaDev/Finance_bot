export interface Candle {
  symbol: string
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface MarketDataResponse {
  symbol: string
  source: string
  interval: string
  candles: Candle[]
}
