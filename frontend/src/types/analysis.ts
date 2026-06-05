export interface MACDPoint {
  macd: number | null
  signal: number | null
  histogram: number | null
}

export interface BollingerPoint {
  upper: number | null
  middle: number | null
  lower: number | null
}

export interface IndicatorPoint {
  timestamp: string
  close: number
  rsi: number | null
  macd: MACDPoint
  bollinger: BollingerPoint
  sma_20: number | null
  sma_50: number | null
  sma_200: number | null
  ema_12: number | null
  ema_26: number | null
  atr: number | null
}

export interface TechnicalAnalysisResponse {
  symbol: string
  interval: string
  series: IndicatorPoint[]
  support_levels: number[]
  resistance_levels: number[]
}

export interface NewsItem {
  title: string
  source: string
  url: string
  published_at: string | null
  sentiment_score: number
  sentiment_label: 'positive' | 'neutral' | 'negative'
}

export interface FundamentalAnalysisResponse {
  symbol: string
  sentiment_score: number
  news_impact: number
  key_events: string[]
  news_items: NewsItem[]
  analyzed_at: string
}
