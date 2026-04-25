/**
 * Truth Badge Component - Règle de Vérité SACS
 * 
 * 3 niveaux de fiabilité:
 * - MESURÉ (measured): Badge vert - Capteur direct (fiabilité 100%)
 * - INFÉRÉ (inferred): Badge orange - Proxy satellitaire (fiabilité 70-90%)
 * - SIMULÉ (simulated): Badge gris - Modèle numérique (fiabilité 50-70%)
 */

import { cn } from '@/lib/utils'
import type { DataStatus } from '@/lib/types'

interface TruthBadgeProps {
  status: DataStatus
  className?: string
}

const STATUS_CONFIG = {
  measured: {
    label: 'MESURÉ',
    icon: '●', // Cercle plein
    className: 'bg-truth-measured-dark text-truth-measured-contrast border-2 border-truth-measured shadow-lg shadow-truth-measured/50',
    description: 'Capteur direct - Fiabilité 100%',
  },
  inferred: {
    label: 'INFÉRÉ',
    icon: '◐', // Demi-cercle
    className: 'bg-truth-inferred-dark text-truth-inferred-contrast border-2 border-truth-inferred shadow-lg shadow-truth-inferred/50',
    description: 'Proxy satellitaire - Fiabilité 70-90%',
  },
  simulated: {
    label: 'SIMULÉ',
    icon: '○', // Cercle vide
    className: 'bg-truth-simulated-dark text-truth-simulated-contrast border-2 border-truth-simulated shadow-lg shadow-truth-simulated/50',
    description: 'Modèle numérique - Fiabilité 50-70%',
  },
} as const

export function TruthBadge({ status, className }: TruthBadgeProps) {
  const config = STATUS_CONFIG[status]
  
  return (
    <div
      className={cn(
        'inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold uppercase tracking-wide border-2',
        config.className,
        className
      )}
      role="status"
      aria-label={`Statut de la donnée: ${config.label}`}
    >
      <span className="text-sm" aria-hidden="true">
        {config.icon}
      </span>
      <span>{config.label}</span>
    </div>
  )
}
