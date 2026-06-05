import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchSignal } from '../api/signalsApi'
import { useSettingsStore } from '../store/settingsStore'
import { useMarketStore } from '../store/marketStore'

export function useSignal() {
  const { symbol, timeframe, riskLevel, strategyType } = useSettingsStore()
  const addAlert = useMarketStore((s) => s.addAlert)

  const query = useQuery({
    queryKey: ['signal', symbol, timeframe, riskLevel, strategyType],
    queryFn: () => fetchSignal(symbol, timeframe, riskLevel, strategyType),
    staleTime: 60_000,
    retry: 1,
  })

  useEffect(() => {
    if (query.data) addAlert(query.data)
  }, [query.data, addAlert])

  return query
}
