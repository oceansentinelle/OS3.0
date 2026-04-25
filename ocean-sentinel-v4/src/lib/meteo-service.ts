/**
 * Service Météo Marine
 * Intégration NOAA WaveWatch 3 + Météo-France
 */

import { API_ENDPOINTS, fetchWithRetry } from './api-config'

export interface MeteoMarineData {
  wind_speed: number // km/h
  wind_direction: string // N, NE, E, SE, S, SO, O, NO
  wave_height: number // mètres
  wave_period: number // secondes
  air_temp: number // °C
  humidity: number // %
  pressure: number // hPa
  last_update: string // ISO timestamp
  source: string
}

/**
 * Convertit un angle en direction cardinale
 */
function angleToDirection(angle: number): string {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
  const index = Math.round(angle / 45) % 8
  return directions[index]
}

/**
 * Récupère les données météo depuis NOAA WaveWatch 3
 * Documentation : https://polar.ncep.noaa.gov/waves/
 */
async function fetchNOAAWaveData(): Promise<Partial<MeteoMarineData>> {
  try {
    // NOAA WaveWatch 3 - Modèle global de houle
    // Note: L'API NOAA nécessite une requête GRIB2, nous utilisons un proxy simplifié
    const { LAT, LON } = API_ENDPOINTS.NOAA_WAVEWATCH.PARAMS
    
    // Endpoint simplifié (à adapter selon l'API réelle disponible)
    const url = `${API_ENDPOINTS.NOAA_WAVEWATCH.BASE_URL}?lat=${LAT}&lon=${LON}`
    
    const response = await fetchWithRetry(url)
    const data = await response.json()
    
    return {
      wave_height: data.HTSGW || 0, // Significant Wave Height
      wave_period: data.PERPW || 0, // Peak Wave Period
      wind_speed: data.WIND ? data.WIND * 3.6 : 0, // m/s → km/h
      wind_direction: angleToDirection(data.DIRPW || 0),
      source: 'NOAA WaveWatch 3',
    }
  } catch (error) {
    console.error('Erreur NOAA WaveWatch:', error)
    return {}
  }
}

/**
 * Récupère les données atmosphériques depuis Météo-France
 * Documentation : https://portail-api.meteofrance.fr/
 */
async function fetchMeteoFranceData(): Promise<Partial<MeteoMarineData>> {
  try {
    const { BASE_URL, ENDPOINTS, STATION_ID } = API_ENDPOINTS.METEO_FRANCE
    
    // Requête observations 6 minutes (infrahoraire)
    const url = `${BASE_URL}${ENDPOINTS.OBSERVATIONS}?id-station=${STATION_ID}`
    
    const response = await fetchWithRetry(url, {
      headers: {
        'Accept': 'application/json',
        // 'apikey': API_KEYS.METEO_FRANCE, // À décommenter avec vraie clé
      },
    })
    
    const data = await response.json()
    const latest = data[0] // Dernière observation
    
    return {
      air_temp: latest.t || 0, // Température (°C)
      humidity: latest.u || 0, // Humidité relative (%)
      pressure: latest.pres || 0, // Pression (hPa)
      wind_speed: latest.ff ? latest.ff * 3.6 : 0, // m/s → km/h
      wind_direction: angleToDirection(latest.dd || 0),
      last_update: latest.validity_time,
      source: 'Météo-France',
    }
  } catch (error) {
    console.error('Erreur Météo-France:', error)
    return {}
  }
}

/**
 * Récupère les données météo marines complètes
 * Fusionne NOAA (houle) + Météo-France (atmosphère)
 */
export async function fetchMeteoMarine(): Promise<MeteoMarineData> {
  try {
    // Requêtes parallèles pour optimiser le temps de réponse
    const [noaaData, meteoData] = await Promise.all([
      fetchNOAAWaveData(),
      fetchMeteoFranceData(),
    ])
    
    // Fusion des données (priorité à Météo-France pour le vent)
    return {
      wind_speed: meteoData.wind_speed || noaaData.wind_speed || 0,
      wind_direction: meteoData.wind_direction || noaaData.wind_direction || 'N',
      wave_height: noaaData.wave_height || 0,
      wave_period: noaaData.wave_period || 0,
      air_temp: meteoData.air_temp || 0,
      humidity: meteoData.humidity || 0,
      pressure: meteoData.pressure || 1013,
      last_update: meteoData.last_update || new Date().toISOString(),
      source: 'NOAA WaveWatch 3 + Météo-France',
    }
  } catch (error) {
    console.error('Erreur fetchMeteoMarine:', error)
    
    // Fallback sur données mockées en cas d'erreur
    return {
      wind_speed: 12.5,
      wind_direction: 'NO',
      wave_height: 1.2,
      wave_period: 6.5,
      air_temp: 16.8,
      humidity: 78,
      pressure: 1015,
      last_update: new Date().toISOString(),
      source: 'Données de démonstration',
    }
  }
}

/**
 * Hook React pour les données météo avec cache
 * À implémenter avec useState/useEffect si besoin
 */
export function useMeteoMarine() {
  // Pour l'instant, retourne une fonction de fetch
  return fetchMeteoMarine
}
