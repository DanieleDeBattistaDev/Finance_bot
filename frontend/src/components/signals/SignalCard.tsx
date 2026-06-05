import { useTranslation } from 'react-i18next'
import type { SignalResponse } from '../../types/signal'

interface Props { signal: SignalResponse }

const STYLES = {
  buy:  'border-green-500/50 bg-green-500/10 text-green-400',
  sell: 'border-red-500/50   bg-red-500/10   text-red-400',
  hold: 'border-gray-600     bg-gray-800     text-gray-400',
}

const ICON = { buy: '▲', sell: '▼', hold: '◆' }

export default function SignalCard({ signal }: Props) {
  const { t } = useTranslation()

  return (
    <div className={`border rounded-xl p-4 ${STYLES[signal.action]}`}>
      <div className="flex justify-between items-start mb-3">
        <div>
          <span className="text-2xl font-bold mr-2">{ICON[signal.action]}</span>
          <span className="text-xl font-bold">{t(`signal.${signal.action}`)}</span>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold">{signal.confidence.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">{t('signal.confidence')}</div>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap mb-3">
        {[signal.strategy_type, signal.timeframe, `${signal.risk_level} risk`].map((tag) => (
          <span key={tag} className="text-xs bg-gray-800 px-2 py-0.5 rounded-full text-gray-400">
            {tag}
          </span>
        ))}
      </div>

      <ul className="space-y-1">
        {signal.reasoning.slice(1, 5).map((r, i) => (
          <li key={i} className="text-xs text-gray-400 leading-relaxed">• {r}</li>
        ))}
      </ul>

      <p className="text-xs text-gray-600 mt-3">
        {new Date(signal.generated_at).toLocaleTimeString()}
      </p>
    </div>
  )
}
