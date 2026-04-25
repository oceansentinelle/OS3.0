// Ocean Sentinel Types

export type DataStatus = 'measured' | 'inferred' | 'simulated'

export type ValidationStatus = 'valid' | 'suspect' | 'invalid'

export interface Parameter {
  name: string
  value: number
  unit: string
  status: DataStatus
  source: string
  timestamp: string
  quality_score: number
  is_critical: boolean
}

export interface StationData {
  station_id: string
  timestamp: string
  parameters: Parameter[]
}

export interface CriticalThreshold {
  operator: '<' | '>'
  value: number
  unit: string
  label: string
  action: string
}

export const CRITICAL_THRESHOLDS: Record<string, CriticalThreshold> = {
  DOX2: {
    operator: '<',
    value: 150,
    unit: 'µmol/kg',
    label: 'HYPOXIE',
    action: 'Risque mortalité huîtres',
  },
  PH_TOTAL: {
    operator: '<',
    value: 7.80,
    unit: '',
    label: 'ACIDIFICATION',
    action: 'Risque fragilisation coquilles',
  },
  TEMP: {
    operator: '>',
    value: 25,
    unit: '°C',
    label: 'TEMPÉRATURE ÉLEVÉE',
    action: 'Surveiller évolution',
  },
}

export const VARIABLE_LABELS: Record<string, string> = {
  TEMP: 'Température',
  PSAL: 'Salinité',
  DOX2: 'Oxygène dissous',
  PH_TOTAL: 'pH Total',
}
