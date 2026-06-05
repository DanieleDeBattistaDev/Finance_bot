import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ReferenceLine, ResponsiveContainer, BarChart, Bar, Cell,
} from 'recharts'
import type { IndicatorPoint } from '../../types/analysis'

interface Props {
  series: IndicatorPoint[]
  show: { rsi: boolean; macd: boolean }
}

const fmt = (v: unknown) => typeof v === 'number' ? v.toFixed(2) : '—'

export default function IndicatorsOverlay({ series, show }: Props) {
  const data = series.slice(-120)  // last 120 bars

  return (
    <div className="space-y-3">
      {show.rsi && (
        <div className="bg-gray-900 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-2">RSI (14)</p>
          <ResponsiveContainer width="100%" height={100}>
            <LineChart data={data}>
              <XAxis dataKey="timestamp" hide />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#6b7280' }} width={28} />
              <Tooltip
                contentStyle={{ background: '#111827', border: '1px solid #1f2937', fontSize: 11 }}
                formatter={fmt}
              />
              <ReferenceLine y={70} stroke="#dc2626" strokeDasharray="3 3" />
              <ReferenceLine y={30} stroke="#16a34a" strokeDasharray="3 3" />
              <Line type="monotone" dataKey="rsi" stroke="#818cf8" dot={false} strokeWidth={1.5} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {show.macd && (
        <div className="bg-gray-900 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-2">MACD (12/26/9)</p>
          <ResponsiveContainer width="100%" height={100}>
            <BarChart data={data}>
              <XAxis dataKey="timestamp" hide />
              <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} width={28} />
              <Tooltip
                contentStyle={{ background: '#111827', border: '1px solid #1f2937', fontSize: 11 }}
                formatter={fmt}
              />
              <Bar dataKey="macd.histogram" name="Histogram">
                {data.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={(entry.macd.histogram ?? 0) >= 0 ? '#16a34a' : '#dc2626'}
                  />
                ))}
              </Bar>
              <Line type="monotone" dataKey="macd.macd" stroke="#818cf8" dot={false} strokeWidth={1} />
              <Line type="monotone" dataKey="macd.signal" stroke="#f59e0b" dot={false} strokeWidth={1} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
