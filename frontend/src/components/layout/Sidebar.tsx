import { Link, useLocation } from 'react-router-dom'
import { Activity, BarChart3, Calculator, FileText, Settings, LayoutDashboard, TrendingUp } from 'lucide-react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/trade', icon: TrendingUp, label: 'Operação' },
  { to: '/setups', icon: FileText, label: 'Setups' },
  { to: '/patterns', icon: BarChart3, label: 'Análise' },
  { to: '/calculator', icon: Calculator, label: 'Calculadora' },
  { to: '/settings', icon: Settings, label: 'Config' },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-56 bg-zeek-bg-secondary border-r border-zeek-border flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-zeek-border">
        <div className="font-mono text-xs text-zeek-accent leading-tight">
          ███████╗███████╗███████╗██╗  ██╗
          <br />
          ╚══███╔╝██╔════╝██╔════╝██║ ██╔╝
          <br />
          ███╔╝ █████╗  █████╗  █████╔╝
          <br />
          ███╔╝  ██╔══╝  ██╔══╝  ██╔═██╗
          <br />
          ███████╗███████╗██║  ██║
          <br />
          ╚══════╝╚══════╝╚═╝  ╚═╝
        </div>
        <div className="text-xs text-zeek-text-muted mt-1">v1.0 — Web</div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-2 space-y-1">
        {navItems.map(item => {
          const isActive = location.pathname === item.to
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors
                ${isActive
                  ? 'bg-zeek-accent/10 text-zeek-accent'
                  : 'text-zeek-text-secondary hover:bg-zeek-bg-tertiary hover:text-zeek-text'
                }`}
            >
              <item.icon size={18} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Status */}
      <div className="p-4 border-t border-zeek-border">
        <div className="flex items-center gap-2 text-xs text-zeek-text-muted">
          <span className="w-2 h-2 rounded-full bg-zeek-profit animate-pulse" />
          Desconectado
        </div>
      </div>
    </aside>
  )
}
