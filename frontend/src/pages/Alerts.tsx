import { useTranslation } from 'react-i18next'
import { useMarketStore } from '../store/marketStore'
import SignalCard from '../components/signals/SignalCard'

const ACTION_DOT: Record<string, string> = {
  buy: 'bg-green-500', sell: 'bg-red-500', hold: 'bg-gray-500',
}

export default function Alerts() {
  const { t } = useTranslation()
  const { alertHistory } = useMarketStore()

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">{t('alerts.title')}</h1>
        <span className="text-xs text-gray-500">{t('alerts.count', { count: alertHistory.length })}</span>
      </div>

      {alertHistory.length === 0 ? (
        <div className="bg-gray-900 rounded-xl p-8 text-center text-gray-500 text-sm">
          {t('alerts.empty')}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {alertHistory.map((signal, i) => (
            <div key={i} className="relative">
              <div className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full ${ACTION_DOT[signal.action]}`} />
              <SignalCard signal={signal} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
