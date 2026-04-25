/**
 * VolumeControl - Contrôle volume avec slider et mute
 */

import { Volume2, VolumeX } from 'lucide-react'
import { useState } from 'react'

interface VolumeControlProps {
  volume: number
  onChange: (volume: number) => void
  className?: string
}

export function VolumeControl({ volume, onChange, className = '' }: VolumeControlProps) {
  const [isMuted, setIsMuted] = useState(false)
  const [previousVolume, setPreviousVolume] = useState(volume)
  
  const toggleMute = () => {
    if (isMuted) {
      onChange(previousVolume)
      setIsMuted(false)
    } else {
      setPreviousVolume(volume)
      onChange(0)
      setIsMuted(true)
    }
  }
  
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value)
    onChange(newVolume)
    
    if (newVolume === 0) {
      setIsMuted(true)
    } else if (isMuted) {
      setIsMuted(false)
    }
  }
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <button
        onClick={toggleMute}
        className="p-2 rounded-lg hover:bg-primary/10 transition-colors"
        aria-label={isMuted ? 'Activer le son' : 'Couper le son'}
      >
        {isMuted || volume === 0 ? (
          <VolumeX className="w-5 h-5 text-muted-foreground" />
        ) : (
          <Volume2 className="w-5 h-5 text-foreground" />
        )}
      </button>
      
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={volume}
        onChange={handleVolumeChange}
        className="w-24 h-2 bg-muted rounded-full appearance-none cursor-pointer
          [&::-webkit-slider-thumb]:appearance-none
          [&::-webkit-slider-thumb]:w-3
          [&::-webkit-slider-thumb]:h-3
          [&::-webkit-slider-thumb]:rounded-full
          [&::-webkit-slider-thumb]:bg-primary
          [&::-webkit-slider-thumb]:cursor-pointer
          [&::-moz-range-thumb]:w-3
          [&::-moz-range-thumb]:h-3
          [&::-moz-range-thumb]:rounded-full
          [&::-moz-range-thumb]:bg-primary
          [&::-moz-range-thumb]:border-0
          [&::-moz-range-thumb]:cursor-pointer"
        aria-label="Volume"
        aria-valuemin={0}
        aria-valuemax={1}
        aria-valuenow={volume}
        aria-valuetext={`Volume: ${Math.round(volume * 100)}%`}
      />
      
      <span className="text-xs text-muted-foreground w-8 text-right">
        {Math.round(volume * 100)}%
      </span>
    </div>
  )
}
