import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { fetchTechnical, fetchFundamental } from '../api/analysisApi'
import { fetchPrediction, triggerTraining } from '../api/predictionsApi'
import IndicatorsOverlay from '../components/charts/IndicatorsOverlay'
import { useSettingsStore } from '../store/settingsStore'

const SENTIMENT_LABEL: Record<string, string> = {
  positive: 'text-green-400', neutral: 'text-gray-400', negative: 'text-red-400',
}

export default function Analysis() {
  const { t } = useTranslation()
  const symbol = useSettingsStore((s) => s.symbol)

  const { data: technical, isLoading: taLoading } = useQuery({
    queryKey: ['technical', symbol, '1y'],
    queryFn: () => fetchTechnical(symbol, '1y'),
  })

  const { data: fundamental, isLoading: fundLoading } = useQuery({
    queryKey: ['fundamental', symbol],
    queryFn: () => fetchFundamental(symbol),
    staleTime: 300_000,
  })

  const { data: prediction, isLoading: mlLoading, error: mlError } = useQuery({
    queryKey: ['prediction', symbol],
    queryFn: () => fetchPrediction(symbol),
    retry: false,
  })

  const handleTrain = async () => {
    await triggerTraining(symbol)
    alert(t('analysis.training_started', { symbol }))
  }

  const latest = technical?.series.at(-1)

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold">{t('analysis.title', { symbol })}</h1>

      <div className="bg-gray-900 rounded-xl p-4">
        <h2 className="text-sm font-semibold text-gray-300 mb-3">{t('analysis.technical')}</h2>
        {taLoading ? (
          <p className="text-gray-500 text-sm">{t('analysis.loading')}</p>
        ) : latest ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'RSI (14)',  value: latest.rsi?.toFixed(1) ?? '—' },
              { label: 'MACD',     value: latest.macd.macd?.toFixed(4) ?? '—' },
              { label: 'ATR',      value: latest.atr?.toFixed(2) ?? '—' },
              { label: 'SMA 20',   value: latest.sma_20?.toFixed(2) ?? '—' },
              { label: 'SMA 50',   value: latest.sma_50?.toFixed(2) ?? '—' },
              { label: 'SMA 200',  value: latest.sma_200?.toFixed(2) ?? '—' },
              { label: 'BB Upper', value: latest.bollinger.upper?.toFixed(2) ?? '—' },
              { label: 'BB Lower', value: latest.bollinger.lower?.toFixed(2) ?? '—' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-gray-800 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-1">{label}</p>
                <p className="font-semibold text-sm">{value}</p>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {technical && (
        <IndicatorsOverlay series={technical.series} show={{ rsi: true, macd: true }} />
      )}

      <div className="bg-gray-900 rounded-xl p-4">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-sm font-semibold text-gray-300">{t('analysis.ml_prediction')}</h2>
          <button
            onClick={handleTrain}
            className="text-xs px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            {t('analysis.train_model')}
          </button>
        </div>

        {mlLoading && <p className="text-gray-500 text-sm">{t('analysis.loading')}</p>}
        {mlError && (
          <p className="text-yellow-500 text-sm">{t('analysis.not_trained')}</p>
        )}
        {prediction && (
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: t('analysis.prediction'),     value: prediction.prediction.toUpperCase() },
              { label: t('analysis.confidence'),     value: `${(prediction.confidence * 100).toFixed(1)}%` },
              { label: t('analysis.expected_return'),value: `${prediction.expected_return >= 0 ? '+' : ''}${prediction.expected_return.toFixed(2)}%` },
              { label: 'XGBoost', value: `${prediction.xgboost.direction} (${(prediction.xgboost.probability * 100).toFixed(0)}%)` },
              { label: 'LSTM',    value: `${prediction.lstm.direction} (${(prediction.lstm.probability * 100).toFixed(0)}%)` },
            ].map(({ label, value }) => (
              <div key={label} className="bg-gray-800 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-1">{label}</p>
                <p className="font-semibold text-sm">{value}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-gray-900 rounded-xl p-4">
        <h2 className="text-sm font-semibold text-gray-300 mb-3">{t('analysis.news_sentiment')}</h2>
        {fundLoading && <p className="text-gray-500 text-sm">{t('analysis.loading')}</p>}
        {fundamental && (
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {fundamental.news_items.map((item, i) => (
              <a
                key={i}
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-gray-800 rounded-lg p-3 hover:bg-gray-750 transition-colors"
              >
                <div className="flex justify-between gap-2">
                  <p className="text-sm text-gray-200 leading-snug">{item.title}</p>
                  <span className={`text-xs shrink-0 font-medium ${SENTIMENT_LABEL[item.sentiment_label] ?? 'text-gray-400'}`}>
                    {item.sentiment_score >= 0 ? '+' : ''}{item.sentiment_score.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{item.source}</p>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
