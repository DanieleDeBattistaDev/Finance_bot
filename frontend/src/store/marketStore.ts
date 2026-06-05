import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { SignalResponse } from '../types/signal'

interface LivePrice {
  symbol: string
  close: number
  change_pct: number
  timestamp: string
}

interface MarketState {
  livePrice: LivePrice | null
  wsConnected: boolean
  alertHistory: SignalResponse[]
  setLivePrice: (p: LivePrice) => void
  setWsConnected: (c: boolean) => void
  addAlert: (s: SignalResponse) => void
}

export const useMarketStore = create<MarketState>()(
  persist(
    (set) => ({
      livePrice: null,
      wsConnected: false,
      alertHistory: [],
      setLivePrice: (livePrice) => set({ livePrice }),
      setWsConnected: (wsConnected) => set({ wsConnected }),
      addAlert: (signal) =>
        set((state) => ({
          alertHistory: [signal, ...state.alertHistory].slice(0, 100),
        })),
    }),
    { name: 'financebot-market', partialize: (s) => ({ alertHistory: s.alertHistory }) },
  ),
)
