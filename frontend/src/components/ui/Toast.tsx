import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useMarketStore } from '../../store/marketStore'
import type { SignalResponse } from '../../types/signal'

const ACTION_STYLE: Record<string, string> = {
  buy:  'border-green-500 bg-green-500/10',
  sell: 'border-red-500 bg-red-500/10',
  hold: 'border-gray-600 bg-gray-800',
}

export default function Toast() {
  const { t } = useTranslation()
  const alertHistory = useMarketStore((s) => s.alertHistory)
  const [visible, setVisible] = useState(false)
  const [current, setCurrent] = useState<SignalResponse | null>(null)
  const lastSeenAt = useRef<string | null>(null)

  useEffect(() => {
    const latest = alertHistory[0]
    if (!latest) return
    if (latest.generated_at === lastSeenAt.current) return

    lastSeenAt.current = latest.generated_at
    setCurrent(latest)
    setVisible(true)

    const id = setTimeout(() => setVisible(false), 6000)
    return () => clearTimeout(id)
  }, [alertHistory])

  if (!visible || !current) return null

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 w-72 border rounded-xl p-4 shadow-2xl
        backdrop-blur-sm transition-all duration-300 ${ACTION_STYLE[current.action]}`}
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <span className="font-bold text-sm">{t(`toast.${current.action}`)}</span>
          <span className="text-xs text-gray-400 ml-2">{current.symbol}</span>
        </div>
        <button
          onClick={() => setVisible(false)}
          className="text-gray-500 hover:text-gray-300 text-lg leading-none ml-2"
        >
          ×
        </button>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <div className="flex-1 bg-gray-700 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full ${current.action === 'buy' ? 'bg-green-500' : current.action === 'sell' ? 'bg-red-500' : 'bg-gray-500'}`}
            style={{ width: `${current.confidence}%` }}
          />
        </div>
        <span className="text-xs font-semibold text-gray-300">{current.confidence.toFixed(0)}%</span>
      </div>

      {current.reasoning.slice(0, 2).map((r, i) => (
        <p key={i} className="text-xs text-gray-400 leading-relaxed">• {r}</p>
      ))}

      <p className="text-xs text-gray-600 mt-2">
        {new Date(current.generated_at).toLocaleTimeString()}
      </p>
    </div>
  )
}
