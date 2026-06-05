import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/ui/Sidebar'
import Navbar from './components/ui/Navbar'
import Toast from './components/ui/Toast'
import Dashboard from './pages/Dashboard'
import Analysis from './pages/Analysis'
import Settings from './pages/Settings'
import Alerts from './pages/Alerts'
import { useSettingsStore } from './store/settingsStore'
import { useMarketStream } from './hooks/useMarketStream'

function StreamProvider() {
  const symbol = useSettingsStore((s) => s.symbol)
  useMarketStream(symbol)
  return null
}

export default function App() {
  return (
    <BrowserRouter>
      <StreamProvider />
      <Toast />
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <Navbar />
          <main className="flex-1 overflow-auto p-4">
            <Routes>
              <Route path="/"         element={<Dashboard />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/alerts"   element={<Alerts />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
