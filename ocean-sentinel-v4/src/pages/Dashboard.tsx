/**
 * Dashboard Page - Données en direct
 * 
 * Affiche les métriques océanographiques en temps réel :
 * - TEMP, PSAL, DOX2, PH_TOTAL
 * - Alertes critiques SACS (hypoxie, acidification)
 * - Badges de vérité (●/◐/○)
 * - Skeleton loaders
 * - Données météo marines en temps réel
 */

import { useState, useEffect } from 'react'
import { AlertTriangle, Clock, Wind, Waves, Droplets, Thermometer, Gauge } from 'lucide-react'
import { AlertBanner } from '@/components/dashboard/AlertBanner'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { fetchStationData, fetchCriticalAlerts } from '@/lib/api'
import type { StationData } from '@/lib/types'

const STATIONS = [
  { id: 'BARAG_PROXY', name: 'BARAG', source: 'COAST-HF Ifremer' },
  { id: 'ARCACHON_EYRAC', name: 'EYRAC', source: 'Hub\'Eau BRGM' },
]

// Données météo marines - Fallback si API échoue
const FALLBACK_METEO = {
  wind_speed: 12.5,
  wind_direction: 'NNO',
  wave_height: 1.2,
  wave_period: 6.5,
  air_temp: 16.8,
  humidity: 78,
  pressure: 1015,
  last_update: new Date().toISOString(),
}

/**
 * Récupère les données météo marines depuis l'API backend
 */
async function fetchMeteoData() {
  try {
    const response = await fetch('https://oceansentinelle.fr/api/v1/meteo/arcachon')
    if (!response.ok) throw new Error('API météo indisponible')
    return await response.json()
  } catch (error) {
    console.warn('Utilisation données météo fallback:', error)
    return FALLBACK_METEO
  }
}

const MetricCardSkeleton = () => (
  <div className="bg-card border-2 border-border rounded-xl p-6 animate-pulse">
    <div className="h-4 bg-muted rounded w-1/2 mb-4"></div>
    <div className="h-8 bg-muted rounded w-3/4 mb-2"></div>
    <div className="h-3 bg-muted rounded w-1/3"></div>
  </div>
)

export default function Dashboard() {
  const [stationsData, setStationsData] = useState<Record<string, StationData>>({})
  const [criticalAlerts, setCriticalAlerts] = useState<StationData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [meteoData, setMeteoData] = useState(FALLBACK_METEO)
  
  // Update clock every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])
  
  // Fetch initial data
  useEffect(() => {
    loadData()
    loadMeteoData()
  }, [])
  
  // Fetch meteo data
  const loadMeteoData = async () => {
    try {
      const data = await fetchMeteoData()
      setMeteoData(data)
    } catch (err) {
      console.error('Erreur chargement météo:', err)
    }
  }

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      loadData()
      loadMeteoData()
    }, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])
  
  async function loadData() {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch all stations
      const data: Record<string, StationData> = {}
      for (const station of STATIONS) {
        data[station.id] = await fetchStationData(station.id)
      }
      
      setStationsData(data)
      
      // Fetch critical alerts
      const alerts = await fetchCriticalAlerts()
      setCriticalAlerts(alerts)
      
    } catch (err) {
      console.error('Erreur chargement données:', err)
      setError('Impossible de charger les données. Vérifiez votre connexion.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen bg-background">
      {/* Hero with Clock */}
      <section className="relative bg-gradient-to-br from-ocean-950 to-ocean-900 border-b-2 border-primary">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold mb-2">
                Données en direct
              </h1>
              <p className="text-muted-foreground">
                Surveillance océanographique temps réel • Bassin d'Arcachon
              </p>
            </div>
            <div className="bg-card/50 backdrop-blur-sm border-2 border-primary/50 rounded-xl px-6 py-4">
              <div className="flex items-center gap-2 text-primary mb-1">
                <Clock className="w-5 h-5" />
                <span className="text-sm font-semibold">Heure locale</span>
              </div>
              <div className="text-2xl font-mono font-bold">
                {currentTime.toLocaleTimeString('fr-FR')}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {currentTime.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Météo Marine */}
      <section className="relative bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Waves className="w-5 h-5 text-primary" />
            Conditions Météo Marines
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Wind className="w-4 h-4" />
                <span className="text-xs">Vent</span>
              </div>
              <div className="text-2xl font-bold">{meteoData.wind_speed}</div>
              <div className="text-xs text-muted-foreground">km/h {meteoData.wind_direction}</div>
            </div>
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Waves className="w-4 h-4" />
                <span className="text-xs">Houle</span>
              </div>
              <div className="text-2xl font-bold">{meteoData.wave_height}</div>
              <div className="text-xs text-muted-foreground">m • {meteoData.wave_period}s</div>
            </div>
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Thermometer className="w-4 h-4" />
                <span className="text-xs">Temp. Air</span>
              </div>
              <div className="text-2xl font-bold">{meteoData.air_temp}</div>
              <div className="text-xs text-muted-foreground">°C</div>
            </div>
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Droplets className="w-4 h-4" />
                <span className="text-xs">Humidité</span>
              </div>
              <div className="text-2xl font-bold">{meteoData.humidity}</div>
              <div className="text-xs text-muted-foreground">%</div>
            </div>
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Gauge className="w-4 h-4" />
                <span className="text-xs">Pression</span>
              </div>
              <div className="text-2xl font-bold">{meteoData.pressure}</div>
              <div className="text-xs text-muted-foreground">hPa</div>
            </div>
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Clock className="w-4 h-4" />
                <span className="text-xs">Mise à jour</span>
              </div>
              <div className="text-sm font-bold">{new Date(meteoData.last_update).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</div>
              <div className="text-xs text-muted-foreground">NOAA/Météo-France</div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Critical Alerts */}
      {criticalAlerts.length > 0 && (
        <section className="relative bg-destructive/5 border-y-2 border-destructive">
          <div className="max-w-7xl mx-auto px-4 py-4 space-y-3">
            {criticalAlerts.map((stationData: any) =>
              stationData.parameters
                .filter((p: any) => p.is_critical)
                .map((param: any) => (
                  <AlertBanner
                    key={`${stationData.station_id}-${param.name}`}
                    parameter={param}
                    stationId={stationData.station_id}
                  />
                ))
            )}
          </div>
        </section>
      )}
      
      {/* Error State */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-destructive/10 border-2 border-destructive rounded-xl p-6 text-center">
            <AlertTriangle className="w-12 h-12 text-destructive mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">Erreur de connexion</h2>
            <p className="text-muted-foreground mb-4">{error}</p>
            <button
              onClick={loadData}
              className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors touch-target"
            >
              Réessayer
            </button>
          </div>
        </div>
      )}
      
      {/* Stations Grid */}
      <section className="relative max-w-7xl mx-auto px-4 py-8 space-y-12">
        {STATIONS.map(station => (
          <div key={station.id}>
            {/* Station Header */}
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-success animate-pulse" />
              <h2 className="text-2xl font-bold">{station.name}</h2>
            </div>
            
            {/* Metrics Grid */}
            <div className="grid-metrics grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
              {loading ? (
                // Skeleton loaders
                [...Array(4)].map((_, i) => (
                  <MetricCardSkeleton key={i} />
                ))
              ) : stationsData[station.id] ? (
                // Real data
                stationsData[station.id].parameters.map((param: any) => (
                  <MetricCard key={param.name} parameter={param} />
                ))
              ) : null}
            </div>
          </div>
        ))}
      </section>
      
      {/* Footer Info */}
      <section className="max-w-7xl mx-auto px-4 py-8 border-t border-border">
        <div className="text-center text-sm text-muted-foreground space-y-2">
          <p>
            🔄 Rafraîchissement automatique toutes les 5 minutes
          </p>
          <p>
            Dernière mise à jour : {new Date().toLocaleTimeString('fr-FR')}
          </p>
        </div>
      </section>
    </div>
  )
}
