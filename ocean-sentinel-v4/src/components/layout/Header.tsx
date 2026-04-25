/**
 * Header Component
 * Navigation principale avec onglets desktop
 */

import { Link, useLocation } from 'react-router-dom'
import { Home, BarChart3, BookOpen, Zap, Mic } from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { path: '/', label: 'Accueil', icon: Home },
  { path: '/dashboard', label: 'Données en direct', icon: BarChart3 },
  { path: '/about', label: 'Le Projet', icon: BookOpen },
  { path: '/api', label: 'API REST', icon: Zap },
  { path: '/podcast', label: 'Podcast', icon: Mic },
]

export function Header() {
  const location = useLocation()
  
  return (
    <header className="sticky top-0 z-40 bg-ocean-950 backdrop-blur-sm border-b-2 border-primary">
      <div className="max-w-7xl mx-auto px-4">
        {/* Logo */}
        <div className="flex items-center justify-between py-4">
          <Link to="/" className="flex items-center gap-2 text-white hover:text-primary transition-colors">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground font-bold">
              🌊
            </div>
            <span className="text-lg font-bold">Ocean Sentinel</span>
          </Link>
        </div>
        
        {/* Navigation Desktop */}
        <nav className="hidden md:block">
          <ul className="flex gap-2 border-b border-border">
            {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
              const isActive = location.pathname === path
              
              return (
                <li key={path}>
                  <Link
                    to={path}
                    className={cn(
                      'flex items-center gap-2 px-4 py-3 text-sm font-semibold',
                      'border-b-3 transition-all',
                      isActive
                        ? 'text-white border-primary bg-primary/20'
                        : 'text-white/70 border-transparent hover:text-white hover:border-primary/50 hover:bg-primary/10'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{label}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
      </div>
    </header>
  )
}
