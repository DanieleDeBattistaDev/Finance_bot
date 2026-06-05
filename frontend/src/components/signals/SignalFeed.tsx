import SignalCard from './SignalCard'
import type { SignalResponse } from '../../types/signal'

interface Props {
  signals: SignalResponse[]
  loading?: boolean
}

export default function SignalFeed({ signals, loading }: Props) {
  if (loading) return <div className="text-gray-500 text-sm p-4">Loading signals…</div>
  if (!signals.length) return <div className="text-gray-500 text-sm p-4">No signals yet.</div>

  return (
    <div className="space-y-3">
      {signals.map((s, i) => <SignalCard key={i} signal={s} />)}
    </div>
  )
}
