import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Home, BarChart3, TestTube, Settings, Upload } from 'lucide-react'

export default function Sidebar() {
  const navItems = [
    { to: '/', icon: Home, label: 'Command Center' },
    { to: '/pressure', icon: BarChart3, label: 'Pressure Analysis' },
    { to: '/backtest', icon: TestTube, label: 'Backtest Studio' },
    { to: '/ingest', icon: Upload, label: 'Data Ingest' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <aside className="hidden md:block w-64 border-r border-border bg-background p-4">
      <nav className="flex flex-col gap-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={cn(
              "flex items-center gap-3 rounded-md p-3 text-sm font-medium transition-colors",
              "hover:bg-accent hover:text-accent-foreground",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            )}
            activeClassName="bg-accent text-accent-foreground"
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}