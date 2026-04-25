/**
 * Configuration des API externes
 * Ocean Sentinel - Sources de données réelles
 */

export const API_ENDPOINTS = {
  // API Ocean Sentinel (Backend FastAPI)
  OCEAN_SENTINEL: {
    BASE_URL: 'https://oceansentinelle.fr/api/v1',
    ENDPOINTS: {
      STATION_LATEST: '/station/{station_id}/latest',
      STATION_TIMESERIES: '/station/{station_id}/timeseries',
      ALERTS_CRITICAL: '/alerts/critical',
      HEALTH: '/health',
    },
  },

  // NOAA WaveWatch 3 (Houle et Vent)
  NOAA_WAVEWATCH: {
    BASE_URL: 'https://nomads.ncep.noaa.gov/cgi-bin/filter_wave_multi.pl',
    PARAMS: {
      // Coordonnées Bassin d'Arcachon
      LAT: 44.6667,
      LON: -1.1667,
      // Variables : HTSGW (hauteur vagues), DIRPW (direction), PERPW (période)
      VARS: ['HTSGW', 'DIRPW', 'PERPW', 'WIND'],
    },
  },

  // Météo-France API (Données atmosphériques)
  METEO_FRANCE: {
    BASE_URL: 'https://public-api.meteofrance.fr/public/DPObs/v1',
    ENDPOINTS: {
      OBSERVATIONS: '/station/infrahoraire-6m',
      FORECAST: '/forecast',
    },
    // Station Météo-France la plus proche : Cap Ferret (33)
    STATION_ID: '33122001',
  },

  // Copernicus Marine Service (CMEMS) - Données satellitaires
  COPERNICUS_MARINE: {
    BASE_URL: 'https://nrt.cmems-du.eu/motu-web/Motu',
    PRODUCT_ID: 'GLOBAL_ANALYSISFORECAST_PHY_001_024',
    DATASET_ID: 'cmems_mod_glo_phy_anfc_0.083deg_P1D-m',
    // Variables : thetao (temp), so (salinité), zos (niveau mer)
    VARS: ['thetao', 'so', 'zos'],
  },

  // Hub'Eau (Données qualité des eaux)
  HUBEAU: {
    BASE_URL: 'https://hubeau.eaufrance.fr/api/v1',
    ENDPOINTS: {
      QUALITE_EAU: '/qualite_eau_potable/resultats_dis',
      TEMPERATURE: '/temperature/chronique',
    },
    // Code station Arcachon
    STATION_CODE: '05054001',
  },

  // COAST-HF Ifremer (Données in-situ haute fréquence)
  COAST_HF: {
    BASE_URL: 'https://www.coast-hf.fr/data',
    ENDPOINTS: {
      BARAG: '/barag/latest',
      EYRAC: '/eyrac/latest',
    },
  },
}

// Clés API gérées côté backend uniquement (sécurité)
// Le frontend ne doit jamais exposer de clés API sensibles

// Configuration des timeouts et retry
export const API_CONFIG = {
  TIMEOUT: 10000, // 10 secondes
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 seconde
  CACHE_TTL: 300000, // 5 minutes (300 000 ms)
}

// Helper pour construire les URLs
export function buildUrl(base: string, endpoint: string, params?: Record<string, any>): string {
  let url = `${base}${endpoint}`
  
  if (params) {
    const queryString = Object.entries(params)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&')
    url += `?${queryString}`
  }
  
  return url
}

// Helper pour les requêtes avec retry
export async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  attempts: number = API_CONFIG.RETRY_ATTEMPTS
): Promise<Response> {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT)
    
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })
    
    clearTimeout(timeoutId)
    
    if (!response.ok && attempts > 1) {
      await new Promise(resolve => setTimeout(resolve, API_CONFIG.RETRY_DELAY))
      return fetchWithRetry(url, options, attempts - 1)
    }
    
    return response
  } catch (error) {
    if (attempts > 1) {
      await new Promise(resolve => setTimeout(resolve, API_CONFIG.RETRY_DELAY))
      return fetchWithRetry(url, options, attempts - 1)
    }
    throw error
  }
}
