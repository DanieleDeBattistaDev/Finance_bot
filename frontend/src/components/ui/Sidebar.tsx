import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function Sidebar() {
  const { t } = useTranslation()

  const links = [
    { to: '/',          icon: '▦', label: t('nav.dashboard') },
    { to: '/analysis',  icon: '◈', label: t('nav.analysis')  },
    { to: '/settings',  icon: '⚙', label: t('nav.settings')  },
    { to: '/alerts',    icon: '⚑', label: t('nav.alerts')    },
  ]

  return (
    <aside className="w-16 lg:w-52 flex flex-col bg-gray-900 border-r border-gray-800 shrink-0">
      <div className="px-4 py-5 border-b border-gray-800">
        <span className="hidden lg:block text-brand font-bold text-lg tracking-tight">FinanceBot</span>
        <span className="lg:hidden text-brand font-bold text-xl">F</span>
      </div>
      <nav className="flex-1 py-4 space-y-1 px-2">
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-brand/20 text-brand'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-100'
              }`
            }
          >
            <span className="text-lg">{icon}</span>
            <span className="hidden lg:block">{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
