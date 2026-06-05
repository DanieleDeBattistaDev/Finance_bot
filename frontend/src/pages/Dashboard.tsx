import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import CandlestickChart from '../components/charts/CandlestickChart'
import IndicatorsOverlay from '../components/charts/IndicatorsOverlay'
import SignalCard from '../components/signals/SignalCard'
import { fetchHistory } from '../api/marketApi'
import { fetchTechnical, fetchFundamental } from '../api/analysisApi'
import { useSignal } from '../hooks/useSignals'
import { useSettingsStore } from '../store/settingsStore'

const PERIODS = ['1mo', '3mo', '6mo', '1y', '2y'] as const

export default function Dashboard() {
  const { t } = useTranslation()
  const symbol = useSettingsStore((s) => s.symbol)
  const [period, setPeriod] = useState<string>('6mo')
  const [indicators, setIndicators] = useState({ rsi: true, macd: true })

  const { data: market, isLoading: mLoading } = useQuery({
    queryKey: ['market', symbol, period],
    queryFn: () => fetchHistory(symbol, period),
  })

  const { data: technical } = useQuery({
    queryKey: ['technical', symbol, period],
    queryFn: () => fetchTechnical(symbol, period),
  })

  const { data: fundamental } = useQuery({
    queryKey: ['fundamental', symbol],
    queryFn: () => fetchFundamental(symbol),
    staleTime: 300_000,
  })

  const { data: signal, isLoading: sLoading } = useSignal()

  const sentimentColor =
    (fundamental?.sentiment_score ?? 0) > 0.1 ? 'text-green-400' :
    (fundamental?.sentiment_score ?? 0) < -0.1 ? 'text-red-400' : 'text-gray-400'

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{symbol}</h1>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                period === p ? 'bg-brand text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Chart */}
        <div className="xl:col-span-2 space-y-3">
          <div className="bg-gray-900 rounded-xl p-3">
            {mLoading ? (
              <div className="h-96 flex items-center justify-center text-gray-500">
                {t('dashboard.loading_chart')}
              </div>
            ) : (
              <CandlestickChart candles={market?.candles ?? []} />
            )}
          </div>

          <div className="flex gap-2">
            {(['rsi', 'macd'] as const).map((ind) => (
              <button
                key={ind}
                onClick={() => setIndicators((prev) => ({ ...prev, [ind]: !prev[ind] }))}
                className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                  indicators[ind]
                    ? 'border-brand bg-brand/20 text-brand'
                    : 'border-gray-700 text-gray-500'
                }`}
              >
                {ind.toUpperCase()}
              </button>
            ))}
          </div>

          {technical && <IndicatorsOverlay series={technical.series} show={indicators} />}
        </div>

        {/* Right column */}
        <div className="space-y-4">
          {sLoading ? (
            <div className="bg-gray-900 rounded-xl p-4 text-gray-500 text-sm">
              {t('dashboard.generating_signal')}
            </div>
          ) : signal ? (
            <SignalCard signal={signal} />
          ) : null}

          {fundamental && (
            <div className="bg-gray-900 rounded-xl p-4 space-y-3">
              <h3 className="text-sm font-semibold text-gray-300">{t('dashboard.sentiment')}</h3>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">{t('dashboard.score')}</span>
                <span className={`font-semibold ${sentimentColor}`}>
                  {fundamental.sentiment_score >= 0 ? '+' : ''}
                  {fundamental.sentiment_score.toFixed(3)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">{t('dashboard.news_impact')}</span>
                <span className="font-semibold">{fundamental.news_impact.toFixed(0)}/100</span>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">{t('dashboard.key_events')}</p>
                <ul className="space-y-1">
                  {fundamental.key_events.slice(0, 3).map((e, i) => (
                    <li key={i} className="text-xs text-gray-400 leading-relaxed">• {e}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {technical && (
            <div className="bg-gray-900 rounded-xl p-4 space-y-2">
              <h3 className="text-sm font-semibold text-gray-300">{t('dashboard.levels')}</h3>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-xs text-green-500 mb-1">{t('dashboard.support')}</p>
                  {technical.support_levels.slice(-3).reverse().map((l) => (
                    <p key={l} className="text-xs text-gray-300">${l.toFixed(2)}</p>
                  ))}
                </div>
                <div>
                  <p className="text-xs text-red-500 mb-1">{t('dashboard.resistance')}</p>
                  {technical.resistance_levels.slice(-3).reverse().map((l) => (
                    <p key={l} className="text-xs text-gray-300">${l.toFixed(2)}</p>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
