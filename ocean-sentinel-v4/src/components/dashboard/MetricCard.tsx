/**
 * Metric Card Component
 * 
 * Affiche une métrique océanographique avec:
 * - Badge de vérité SACS
 * - Valeur et unité
 * - Seuil critique (si applicable)
 * - Source et timestamp
 */

import { cn } from '@/lib/utils'
import { formatRelativeTime } from '@/lib/utils'
import { TruthBadge } from '@/components/badges/TruthBadge'
import type { Parameter } from '@/lib/types'
import { CRITICAL_THRESHOLDS, VARIABLE_LABELS } from '@/lib/types'

interface MetricCardProps {
  parameter: Parameter
  className?: string
}

export function MetricCard({ parameter, className }: MetricCardProps) {
  const label = VARIABLE_LABELS[parameter.name] || parameter.name
  const threshold = CRITICAL_THRESHOLDS[parameter.name]
  const isCritical = parameter.is_critical
  
  return (
    <div
      className={cn(
        'metric-card rounded-xl border-2',
        'bg-card text-card-foreground',
        isCritical
          ? 'border-l-4 border-l-critical bg-gradient-to-br from-card to-red-950/20'
          : 'border-l-4 border-l-success',
        className
      )}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          {label}
        </div>
        <TruthBadge status={parameter.status} />
      </div>
      
      {/* Value */}
      <div className={cn('text-5xl font-bold leading-none mb-2', isCritical && 'text-white/95')}>
        {parameter.value}
        <span className="text-2xl text-white/70 ml-1">{parameter.unit}</span>
      </div>
      
      {/* Threshold */}
      {threshold && (
        <div
          className={cn(
            'text-sm mb-3',
            isCritical ? 'text-white/90 font-semibold' : 'text-muted-foreground'
          )}
        >
          {isCritical && '⚠️ '}
          Seuil : {threshold.operator} {threshold.value}{threshold.unit}
          {isCritical && ` • ${threshold.label}`}
        </div>
      )}
      
      {/* Footer */}
      <div className="border-t border-border pt-3 space-y-2">
        <div className="text-xs text-white/80">{parameter.source}</div>
        <div className="text-xs text-white/70">
          {formatRelativeTime(parameter.timestamp)}
        </div>
      </div>
    </div>
  )
}

/**
 * Skeleton Loader pour MetricCard
 * Affiche un état de chargement avec animation shimmer
 */
export function MetricCardSkeleton() {
  return (
    <div className="metric-card rounded-xl border-2 border-border bg-card">
      <div className="flex justify-between items-start mb-3">
        <div className="h-4 w-24 bg-muted rounded animate-shimmer" />
        <div className="h-6 w-20 bg-muted rounded animate-shimmer" />
      </div>
      <div className="h-12 w-32 bg-muted rounded animate-shimmer mb-2" />
      <div className="h-4 w-full bg-muted rounded animate-shimmer mb-3" />
      <div className="border-t border-border pt-3 space-y-2">
        <div className="h-3 w-40 bg-muted rounded animate-shimmer" />
        <div className="h-3 w-24 bg-muted rounded animate-shimmer" />
      </div>
    </div>
  )
}
