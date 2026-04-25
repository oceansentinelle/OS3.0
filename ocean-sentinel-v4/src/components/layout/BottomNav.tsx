/**
 * Bottom Navigation Component
 * Navigation mobile (visible uniquement < 768px)
 */

import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { path: '/', label: 'Accueil' },
  { path: '/dashboard', label: 'Données' },
  { path: '/podcast', label: 'Podcast' },
  { path: '/about', label: 'Projet' },
]

export function BottomNav() {
  const location = useLocation()
  
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-card border-t-2 border-primary shadow-2xl shadow-primary/20">
      <ul className="flex justify-around">
        {NAV_ITEMS.map(({ path, label }) => {
          const isActive = location.pathname === path
          
          return (
            <li key={path} className="flex-1">
              <Link
                to={path}
                className={cn(
                  'flex items-center justify-center py-4 touch-target transition-colors',
                  isActive
                    ? 'text-foreground bg-primary/10'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                <span className="text-sm font-semibold">{label}</span>
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
