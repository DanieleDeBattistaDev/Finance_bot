import { useEffect } from 'react'
import { useMarketStore } from '../store/marketStore'
import type { SignalResponse } from '../types/signal'

const WS_BASE = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`

export function useMarketStream(symbol: string) {
  const { setLivePrice, setWsConnected, addAlert } = useMarketStore()

  useEffect(() => {
    if (!symbol) return

    const ws = new WebSocket(`${WS_BASE}/ws/live/${symbol}`)

    ws.onopen = () => setWsConnected(true)
    ws.onclose = () => setWsConnected(false)
    ws.onerror = () => setWsConnected(false)

    ws.onmessage = (event: MessageEvent) => {
      const msg = JSON.parse(event.data as string) as Record<string, unknown>

      if (msg.type === 'price_update') {
        setLivePrice({
          symbol: msg.symbol as string,
          close: msg.close as number,
          change_pct: msg.change_pct as number,
          timestamp: msg.timestamp as string,
        })
      } else if (msg.type === 'signal') {
        addAlert({
          symbol: msg.symbol as string,
          action: msg.action as SignalResponse['action'],
          confidence: msg.confidence as number,
          reasoning: msg.reasoning as string[],
          sources: [],
          timeframe: 'medium',
          risk_level: 'medium',
          strategy_type: 'swing',
          generated_at: msg.generated_at as string,
        })
      }
    }

    const pingId = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send('ping')
    }, 25_000)

    return () => {
      clearInterval(pingId)
      ws.close()
    }
  }, [symbol, setLivePrice, setWsConnected, addAlert])
}
