/**
 * Alert Banner Component - Alertes Critiques SACS
 * 
 * Affiche les alertes critiques avec animation pulse-border
 * Seuils critiques:
 * - DOX2 < 150 µmol/kg → HYPOXIE
 * - PH_TOTAL < 7.80 → ACIDIFICATION
 * - TEMP > 25°C → TEMPÉRATURE ÉLEVÉE
 */

import { X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TruthBadge } from '@/components/badges/TruthBadge'
import type { Parameter } from '@/lib/types'
import { CRITICAL_THRESHOLDS, VARIABLE_LABELS } from '@/lib/types'

interface AlertBannerProps {
  parameter: Parameter
  stationId: string
  onDismiss?: () => void
}

export function AlertBanner({ parameter, stationId, onDismiss }: AlertBannerProps) {
  const threshold = CRITICAL_THRESHOLDS[parameter.name]
  
  if (!threshold) return null
  
  return (
    <div
      className={cn(
        'flex items-start gap-4 p-4 rounded-xl',
        'bg-gradient-to-br from-critical-bg via-critical-dark to-critical-bg',
        'border-4 border-critical shadow-2xl shadow-critical/50',
        'animate-pulse-border',
        'backdrop-blur-sm'
      )}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      {/* Icon */}
      <div className="text-3xl flex-shrink-0" aria-hidden="true">
        ⚠️
      </div>
      
      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <span className="text-xs font-bold uppercase tracking-wide text-white/95">
            🔴 CRITICAL
          </span>
          <h2 className="text-lg font-bold uppercase text-white/95">
            {threshold.label}
          </h2>
        </div>
        
        {/* Value */}
        <div className="text-xl font-bold text-white/95 mb-2">
          {VARIABLE_LABELS[parameter.name]} {parameter.value}{parameter.unit}{' '}
          {threshold.operator} {threshold.value}{threshold.unit}
        </div>
        
        {/* Meta */}
        <div className="flex items-center gap-3 flex-wrap text-sm text-white/90">
          <TruthBadge status={parameter.status} />
          <span className="text-white/90">Station {stationId}</span>
          <span className="text-white/85">• {threshold.action}</span>
        </div>
      </div>
      
      {/* Dismiss button */}
      {onDismiss && (
        <button
          onClick={onDismiss}
          className={cn(
            'touch-target flex items-center justify-center',
            'bg-white/10 border-2 border-white/30 rounded-lg',
            'text-white hover:bg-white/20 transition-colors'
          )}
          aria-label="Masquer l'alerte"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  )
}
