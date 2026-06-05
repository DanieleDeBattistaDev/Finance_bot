import { useTranslation } from 'react-i18next'
import { useSettingsStore } from '../store/settingsStore'
import type { RiskLevel, StrategyType, Timeframe } from '../types/signal'

function Group({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="bg-gray-900 rounded-xl p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-3">{label}</h3>
      {children}
    </div>
  )
}

function Pills<T extends string>({
  options, value, onChange,
}: { options: T[]; value: T; onChange: (v: T) => void }) {
  return (
    <div className="flex gap-2 flex-wrap">
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className={`px-4 py-1.5 rounded-full text-sm transition-colors border ${
            value === opt
              ? 'border-brand bg-brand/20 text-brand'
              : 'border-gray-700 text-gray-400 hover:border-gray-500'
          }`}
        >
          {opt.replace('_', ' ')}
        </button>
      ))}
    </div>
  )
}

const LANGUAGES = [
  { code: 'it', label: '🇮🇹 Italiano' },
  { code: 'en', label: '🇬🇧 English' },
]

export default function Settings() {
  const { t, i18n } = useTranslation()
  const {
    symbol, setSymbol,
    timeframe, setTimeframe,
    riskLevel, setRiskLevel,
    strategyType, setStrategyType,
  } = useSettingsStore()

  const handleLanguage = (code: string) => {
    i18n.changeLanguage(code)
    localStorage.setItem('financebot-lang', code)
  }

  return (
    <div className="max-w-xl space-y-4">
      <h1 className="text-xl font-bold">{t('settings.title')}</h1>

      <Group label={t('settings.language')}>
        <div className="flex gap-2">
          {LANGUAGES.map(({ code, label }) => (
            <button
              key={code}
              onClick={() => handleLanguage(code)}
              className={`px-4 py-1.5 rounded-full text-sm transition-colors border ${
                i18n.language === code
                  ? 'border-brand bg-brand/20 text-brand'
                  : 'border-gray-700 text-gray-400 hover:border-gray-500'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </Group>

      <Group label={t('settings.symbol')}>
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          className="w-40 bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-brand"
          placeholder="e.g. AAPL"
        />
      </Group>

      <Group label={t('settings.timeframe')}>
        <Pills<Timeframe>
          options={['short', 'medium', 'long']}
          value={timeframe}
          onChange={setTimeframe}
        />
        <p className="text-xs text-gray-500 mt-2">{t('settings.timeframe_hint')}</p>
      </Group>

      <Group label={t('settings.risk_level')}>
        <Pills<RiskLevel>
          options={['low', 'medium', 'high']}
          value={riskLevel}
          onChange={setRiskLevel}
        />
        <p className="text-xs text-gray-500 mt-2">{t('settings.risk_hint')}</p>
      </Group>

      <Group label={t('settings.strategy_type')}>
        <Pills<StrategyType>
          options={['scalping', 'swing', 'long_term']}
          value={strategyType}
          onChange={setStrategyType}
        />
        <p className="text-xs text-gray-500 mt-2">{t('settings.strategy_hint')}</p>
      </Group>

      <div className="bg-gray-900 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-2">{t('settings.notifications')}</h3>
        <p className="text-xs text-gray-500">
          {t('settings.notifications_hint')}
        </p>
      </div>
    </div>
  )
}
