/**
 * Ocean Sentinel API Client
 * Logique métier préservée depuis dashboard-dynamic.js
 * Architecture DB-First via MCP TimescaleDB
 */

import type { StationData } from './types'

// Configuration API Backend
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://oceansentinelle.fr/api/v1'
  : '/api/v1'

// Données mockées pour démonstration (fallback si API échoue)
const MOCK_DATA: Record<string, StationData> = {
  BARAG_PROXY: {
    station_id: 'BARAG_PROXY',
    timestamp: new Date().toISOString(),
    parameters: [
      {
        name: 'TEMP',
        value: 18.5,
        unit: '°C',
        status: 'measured',
        source: 'COAST-HF Ifremer',
        timestamp: new Date().toISOString(),
        quality_score: 0.95,
        is_critical: false,
      },
      {
        name: 'PSAL',
        value: 32.8,
        unit: 'PSU',
        status: 'measured',
        source: 'COAST-HF Ifremer',
        timestamp: new Date().toISOString(),
        quality_score: 0.92,
        is_critical: false,
      },
      {
        name: 'DOX2',
        value: 135.0,
        unit: 'µmol/kg',
        status: 'measured',
        source: 'COAST-HF Ifremer',
        timestamp: new Date().toISOString(),
        quality_score: 0.88,
        is_critical: true,
      },
      {
        name: 'PH_TOTAL',
        value: 7.65,
        unit: '',
        status: 'inferred',
        source: 'Sentinel-3 OLCI',
        timestamp: new Date().toISOString(),
        quality_score: 0.75,
        is_critical: true,
      },
    ],
  },
  ARCACHON_EYRAC: {
    station_id: 'ARCACHON_EYRAC',
    timestamp: new Date().toISOString(),
    parameters: [
      {
        name: 'TEMP',
        value: 19.2,
        unit: '°C',
        status: 'measured',
        source: 'Hub\'Eau BRGM',
        timestamp: new Date().toISOString(),
        quality_score: 0.98,
        is_critical: false,
      },
      {
        name: 'PSAL',
        value: 16.5,
        unit: 'PSU',
        status: 'measured',
        source: 'Hub\'Eau BRGM',
        timestamp: new Date().toISOString(),
        quality_score: 0.96,
        is_critical: false,
      },
      {
        name: 'DOX2',
        value: 185.0,
        unit: 'µmol/kg',
        status: 'simulated',
        source: 'MARS3D Ifremer',
        timestamp: new Date().toISOString(),
        quality_score: 0.65,
        is_critical: false,
      },
      {
        name: 'PH_TOTAL',
        value: 7.92,
        unit: '',
        status: 'measured',
        source: 'Hub\'Eau BRGM',
        timestamp: new Date().toISOString(),
        quality_score: 0.94,
        is_critical: false,
      },
    ],
  },
}

/**
 * Récupère les dernières données d'une station
 * Stations supportées: BARAG_PROXY, ARCACHON_EYRAC
 * Paramètres: TEMP, PSAL, DOX2, PH_TOTAL
 */
export async function fetchStationData(stationId: string): Promise<StationData> {
  // API RÉELLE - Connectée au backend FastAPI
  try {
    const response = await fetch(`${API_BASE_URL}/station/${stationId}/latest`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    return data as StationData
  } catch (error) {
    console.error(`Erreur fetch ${stationId}:`, error)
    
    // Fallback sur données mockées en cas d'erreur
    console.warn(`Utilisation des données mockées pour ${stationId}`)
    return MOCK_DATA[stationId] || MOCK_DATA.BARAG_PROXY
  }
}

/**
 * Récupère les alertes critiques SACS actives
 */
export async function fetchCriticalAlerts(): Promise<StationData[]> {
  try {
    const [barag, eyrac] = await Promise.all([
      fetchStationData('BARAG_PROXY'),
      fetchStationData('ARCACHON_EYRAC'),
    ])
    
    // Filtrer uniquement les stations avec alertes critiques
    const alerts: StationData[] = []
    
    if (barag.parameters.some((p: any) => p.is_critical)) {
      alerts.push(barag)
    }
    
    if (eyrac.parameters.some((p: any) => p.is_critical)) {
      alerts.push(eyrac)
    }
    
    return alerts
  } catch (error) {
    console.error('Erreur fetch alertes critiques:', error)
    throw error
  }
}

/**
 * Hook personnalisé pour le polling automatique
 * Rafraîchit les données toutes les 5 minutes
 */
export function useAutoRefresh(
  callback: () => void,
  interval: number = 5 * 60 * 1000
): (() => void) | undefined {
  if (typeof window === 'undefined') return
  
  const timer = setInterval(callback, interval)
  
  // Cleanup
  return () => clearInterval(timer)
}
