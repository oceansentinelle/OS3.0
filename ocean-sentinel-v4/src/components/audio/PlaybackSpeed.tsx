/**
 * PlaybackSpeed - Sélecteur vitesse de lecture
 */

import { Gauge } from 'lucide-react'
import { useState } from 'react'

interface PlaybackSpeedProps {
  playbackRate: number
  onChange: (rate: number) => void
  className?: string
}

const SPEED_OPTIONS = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]

export function PlaybackSpeed({ playbackRate, onChange, className = '' }: PlaybackSpeedProps) {
  const [isOpen, setIsOpen] = useState(false)
  
  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-primary/10 transition-colors"
        aria-label="Vitesse de lecture"
        aria-expanded={isOpen}
      >
        <Gauge className="w-5 h-5 text-foreground" />
        <span className="text-sm font-semibold">{playbackRate}x</span>
      </button>
      
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute bottom-full right-0 mb-2 bg-card border-2 border-primary/40 rounded-lg shadow-xl z-50 overflow-hidden">
            <div className="p-2 space-y-1">
              {SPEED_OPTIONS.map(speed => (
                <button
                  key={speed}
                  onClick={() => {
                    onChange(speed)
                    setIsOpen(false)
                  }}
                  className={`w-full px-4 py-2 text-sm rounded-lg text-left transition-colors ${
                    playbackRate === speed
                      ? 'bg-primary text-primary-foreground font-semibold'
                      : 'hover:bg-primary/10'
                  }`}
                >
                  {speed}x {speed === 1 && '(Normal)'}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
