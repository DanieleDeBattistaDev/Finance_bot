import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { RiskLevel, StrategyType, Timeframe } from '../types/signal'

interface SettingsState {
  symbol: string
  timeframe: Timeframe
  riskLevel: RiskLevel
  strategyType: StrategyType
  setSymbol: (s: string) => void
  setTimeframe: (t: Timeframe) => void
  setRiskLevel: (r: RiskLevel) => void
  setStrategyType: (s: StrategyType) => void
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      symbol: 'AAPL',
      timeframe: 'medium',
      riskLevel: 'medium',
      strategyType: 'swing',
      setSymbol: (symbol) => set({ symbol }),
      setTimeframe: (timeframe) => set({ timeframe }),
      setRiskLevel: (riskLevel) => set({ riskLevel }),
      setStrategyType: (strategyType) => set({ strategyType }),
    }),
    { name: 'financebot-settings' },
  ),
)
