import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useMarketStore } from '../../store/marketStore'
import { useSettingsStore } from '../../store/settingsStore'

export default function Navbar() {
  const { t } = useTranslation()
  const { symbol, setSymbol } = useSettingsStore()
  const { livePrice, wsConnected } = useMarketStore()
  const [draft, setDraft] = useState(symbol)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const s = draft.trim().toUpperCase()
    if (s) setSymbol(s)
  }

  const changeColor =
    livePrice && livePrice.change_pct >= 0 ? 'text-green-400' : 'text-red-400'

  return (
    <header className="h-14 flex items-center gap-4 px-4 bg-gray-900 border-b border-gray-800 shrink-0">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value.toUpperCase())}
          className="w-28 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm focus:outline-none focus:border-brand"
          placeholder="Symbol"
        />
        <button
          type="submit"
          className="px-3 py-1 bg-brand hover:bg-brand-dark rounded text-sm font-medium transition-colors"
        >
          {t('navbar.go')}
        </button>
      </form>

      {livePrice && livePrice.symbol === symbol && (
        <div className="flex items-center gap-3 ml-2">
          <span className="font-semibold">${livePrice.close.toFixed(2)}</span>
          <span className={`text-sm ${changeColor}`}>
            {livePrice.change_pct >= 0 ? '+' : ''}{livePrice.change_pct.toFixed(2)}%
          </span>
        </div>
      )}

      <div className="ml-auto flex items-center gap-2 text-xs text-gray-500">
        <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-gray-600'}`} />
        {wsConnected ? t('navbar.live') : t('navbar.disconnected')}
      </div>
    </header>
  )
}
