/**
 * Layout Component
 * Structure principale avec Header + Navigation + Content + Bottom Nav
 */

import { ReactNode } from 'react'
import { Header } from './Header'
import { BottomNav } from './BottomNav'
import { Footer } from './Footer'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Header />
      <main className="flex-1 pb-24 md:pb-0">
        {children}
      </main>
      <Footer />
      <BottomNav />
    </div>
  )
}
