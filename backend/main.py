#!/usr/bin/env python3
"""
============================================================================
Ocean Sentinel V3.0 - API REST
============================================================================
Description: API FastAPI légère pour accès en lecture seule à TimescaleDB
Contrainte: Optimisée pour VPS 512 Mo RAM
Routes:
  - GET /api/v1/station/barag/latest
  - GET /api/v1/station/barag/history
============================================================================
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

# Système d'alertes SACS
# from alerts import SACSAlertSystem  # TODO: Implémenter plus tard

# Routes
try:
    from routes import health as health_routes
except ImportError:
    # Routes in same directory for local testing
    from . import routes as health_routes

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Mode test local (sans base de données)
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() in ('true', '1', 'yes')

if not TEST_MODE:
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'timescaledb'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'oceansentinelle'),
        'user': os.getenv('DB_USER', 'oceansentinel'),
        'password': os.getenv('DB_PASSWORD', ''),
    }
else:
    # Mode test : pas de connexion à la base de données
    DB_CONFIG = None

# Pool de connexions (optimisé RAM)
db_pool = None

# Système d'alertes SACS
sacs_alert_system = None

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class SensorMeasurement(BaseModel):
    """Modèle pour une mesure de capteur"""
    time: datetime = Field(..., description="Timestamp de la mesure (UTC)")
    station_id: str = Field(..., description="Identifiant de la station")
    temperature_water: Optional[float] = Field(None, description="Température de l'eau (°C)")
    salinity: Optional[float] = Field(None, description="Salinité pratique (PSU)")
    conductivity: Optional[float] = Field(None, description="Conductivité (S/m)")
    pressure_water: Optional[float] = Field(None, description="Pression (dbar)")
    depth: Optional[float] = Field(None, description="Profondeur (m)")
    dissolved_oxygen: Optional[float] = Field(None, description="Oxygène dissous (µmol/kg)")
    ph: Optional[float] = Field(None, description="pH")
    turbidity: Optional[float] = Field(None, description="Turbidité (NTU)")
    chlorophyll_a: Optional[float] = Field(None, description="Chlorophylle-a (µg/L)")
    quality_flag: int = Field(..., description="Flag de qualité (1=bon)")
    data_source: str = Field(..., description="Source des données")

    class Config:
        json_schema_extra = {
            "example": {
                "time": "2026-04-17T00:00:00Z",
                "station_id": "BARAG",
                "temperature_water": 15.5,
                "salinity": 35.2,
                "dissolved_oxygen": 250.0,
                "ph": 8.1,
                "quality_flag": 1,
                "data_source": "ERDDAP:https://erddap.ifremer.fr"
            }
        }

class HistoryResponse(BaseModel):
    """Réponse pour l'historique"""
    station_id: str
    start_date: datetime
    end_date: datetime
    count: int
    measurements: List[SensorMeasurement]

class HealthResponse(BaseModel):
    """Réponse pour le health check"""
    status: str
    database: str
    timestamp: datetime
    total_records: int

# ============================================================================
# GESTION DU POOL DE CONNEXIONS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global db_pool, sacs_alert_system
    
    # Startup
    logger.info("="*80)
    logger.info("OCEAN SENTINEL V3.0 - API REST")
    logger.info("="*80)
    
    if TEST_MODE:
        logger.info("🧪 MODE TEST LOCAL - Sans base de données")
    else:
        logger.info(f"Connexion à {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    try:
        if not TEST_MODE:
            # Pool minimal pour économiser la RAM (2 connexions max)
            db_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=2,
                **DB_CONFIG
            )
            logger.info("✅ Pool de connexions créé (1-2 connexions)")
            
            # Initialiser le système d'alertes SACS
            # sacs_alert_system = SACSAlertSystem(db_pool)  # TODO: Implémenter plus tard
            # logger.info("✅ Système d'alertes SACS initialisé")
        
    except Exception as e:
        logger.error(f"❌ Erreur création pool: {e}")
        if not TEST_MODE:
            raise
    
    yield
    
    # Shutdown
    if db_pool:
        db_pool.closeall()
        logger.info("🛑 Pool de connexions fermé")

# ============================================================================
# APPLICATION FASTAPI
# ============================================================================

app = FastAPI(
    title="Ocean Sentinel API",
    description="""
    API REST pour accès aux données océanographiques COAST-HF
    
    **🏠 [Retour à la page d'accueil](/)** | **📖 [Le Projet](/about.html)**
    
    ## Sources de données
    - ERDDAP COAST-HF (Ifremer)
    - Hub'Eau (BRGM)
    
    ## Stations disponibles
    - BARAG (Bassin d'Arcachon)
    """,
    version="3.0.0",
    lifespan=lifespan
)

# CORS (pour Grafana et autres clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(health_routes.router, prefix="/api/v1", tags=["Health"])

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Page d'accueil de l'API"""
    return {
        "name": "Ocean Sentinel API",
        "version": "3.0.0",
        "description": "API REST pour données océanographiques COAST-HF",
        "endpoints": {
            "health": "/health",
            "latest": "/api/v1/station/{station_id}/latest",
            "history": "/api/v1/station/{station_id}/history",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Vérification de santé de l'API et de la base de données"""
    if TEST_MODE:
        # Mode test local - retourne statut OK sans base de données
        return HealthResponse(
            status="healthy",
            database="test_mode",
            timestamp=datetime.utcnow(),
            total_records=0
        )
    
    try:
        conn = db_pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM barag.sensor_data;")
                result = cursor.fetchone()
                
                return HealthResponse(
                    status="healthy",
                    database="connected",
                    timestamp=datetime.utcnow(),
                    total_records=result['total']
                )
        finally:
            db_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

@app.head("/health", tags=["Health"])
async def health_check_head():
    """Health check HEAD method pour monitoring"""
    return Response(status_code=200)

@app.get(
    "/api/v1/station/{station_id}/latest",
    response_model=SensorMeasurement,
    tags=["Measurements"]
)
async def get_latest_measurement(station_id: str):
    """
    Récupère la dernière mesure environnementale pour une station
    
    Args:
        station_id: Identifiant de la station (ex: BARAG, VPS_PROD)
    
    Returns:
        SensorMeasurement: Dernière mesure disponible
    """
    if TEST_MODE:
        # Mode test local - retourne données mock
        mock_data = {
            "time": datetime.utcnow(),
            "station_id": station_id,
            "temperature_water": 15.5,
            "salinity": 35.2,
            "conductivity": 5.4,
            "pressure_water": 10.1,
            "depth": 2.0,
            "dissolved_oxygen": 250.0,
            "ph": 8.1,
            "turbidity": 2.3,
            "chlorophyll_a": 1.2,
            "quality_flag": 1,
            "data_source": "TEST_MODE"
        }
        return SensorMeasurement(**mock_data)
    
    try:
        conn = db_pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        time,
                        station_id,
                        temperature_water,
                        salinity,
                        conductivity,
                        pressure_water,
                        depth,
                        dissolved_oxygen,
                        ph,
                        turbidity,
                        chlorophyll_a,
                        quality_flag,
                        data_source
                    FROM barag.sensor_data
                    WHERE station_id = %s
                    ORDER BY time DESC
                    LIMIT 1;
                """, (station_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No data found for station {station_id}"
                    )
                
                return SensorMeasurement(**dict(result))
        finally:
            db_pool.putconn(conn)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest measurement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/api/v1/station/{station_id}/history",
    response_model=HistoryResponse,
    tags=["Measurements"]
)
async def get_measurement_history(
    station_id: str,
    start_date: Optional[datetime] = Query(
        None,
        description="Date de début (UTC, ISO 8601)"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Date de fin (UTC, ISO 8601)"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Nombre maximum de résultats (1-1000)"
    )
):
    """
    Récupère l'historique des mesures pour une station
    
    Args:
        station_id: Identifiant de la station
        start_date: Date de début (défaut: 24h avant maintenant)
        end_date: Date de fin (défaut: maintenant)
        limit: Nombre max de résultats (défaut: 100, max: 1000)
    
    Returns:
        HistoryResponse: Historique des mesures
    """
    # Valeurs par défaut
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=1)
    
    try:
        conn = db_pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        time,
                        station_id,
                        temperature_water,
                        salinity,
                        conductivity,
                        pressure_water,
                        depth,
                        dissolved_oxygen,
                        ph,
                        turbidity,
                        chlorophyll_a,
                        quality_flag,
                        data_source
                    FROM barag.sensor_data
                    WHERE station_id = %s
                      AND time >= %s
                      AND time <= %s
                    ORDER BY time DESC
                    LIMIT %s;
                """, (station_id, start_date, end_date, limit))
                
                results = cursor.fetchall()
                
                measurements = [SensorMeasurement(**dict(row)) for row in results]
                
                return HistoryResponse(
                    station_id=station_id,
                    start_date=start_date,
                    end_date=end_date,
                    count=len(measurements),
                    measurements=measurements
                )
        finally:
            db_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stations", tags=["Stations"])
async def list_stations():
    """Liste des stations disponibles pour les tests Newman"""
    if TEST_MODE:
        stations = [
            {
                "id": "BARAG",
                "name": "BARAG",
                "location": "Bassin d'Arcachon",
                "source": "COAST-HF Ifremer"
            },
            {
                "id": "ARCACHON_EYRAC",
                "name": "EYRAC",
                "location": "Bassin d'Arcachon",
                "source": "Hub'Eau BRGM"
            }
        ]
        return {"count": len(stations), "stations": stations}
    
    # Mode production - requête base de données
    try:
        conn = db_pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT station_id, 
                           'COAST-HF' as source
                    FROM barag.sensor_data
                    ORDER BY station_id;
                """)
                results = cursor.fetchall()
                stations = [
                    {
                        "id": row['station_id'],
                        "name": row['station_id'],
                        "location": "Bassin d'Arcachon",
                        "source": row['source']
                    }
                    for row in results
                ]
                return {"count": len(stations), "stations": stations}
        finally:
            db_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Error fetching stations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/meteo/arcachon", tags=["Meteo"])
async def get_meteo_arcachon():
    """Données météo pour la zone d'Arcachon (source Météo-France)"""
    if TEST_MODE:
        # Mode test local - données simulées réalistes
        import random
        
        meteo_data = {
            "wind_speed": round(random.uniform(5, 25), 1),
            "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SO", "O", "NO"]),
            "wave_height": round(random.uniform(0.5, 3.0), 1),
            "wave_period": round(random.uniform(4, 12), 1),
            "air_temp": round(random.uniform(10, 30), 1),
            "humidity": random.randint(40, 90),
            "pressure": random.randint(980, 1030),
            "last_update": datetime.utcnow().isoformat(),
            "source": "TEST_MODE",
            "location": "Arcachon, Bassin d'Arcachon"
        }
        return meteo_data
    
    # Mode production - requête à Météo-France API
    import httpx
    
    # Coordonnées approximatives pour Arcachon
    ARCACHON_LAT = 44.65
    ARCACHON_LON = -1.15
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Météo-France API - observations récentes
            # Note: En production, ajouter une vraie clé API Météo-France
            obs_url = f"https://api.meteofrance.com/v2/observations?lat={ARCACHON_LAT}&lon={ARCACHON_LON}"
            
            response = await client.get(obs_url)
            if response.status_code == 200:
                data = response.json()
                
                # Extraire la station la plus proche
                if data.get('observations') and len(data['observations']) > 0:
                    obs = data['observations'][0]
                    
                    meteo_data = {
                        "wind_speed": obs.get('wind_speed', 0),
                        "wind_direction": obs.get('wind_direction', 'N'),
                        "wave_height": obs.get('wave_height', 0),
                        "wave_period": obs.get('wave_period', 0),
                        "air_temp": obs.get('temperature', 20),
                        "humidity": obs.get('humidity', 50),
                        "pressure": obs.get('pressure', 1013),
                        "last_update": obs.get('timestamp', datetime.utcnow().isoformat()),
                        "source": "METEO_FRANCE_API",
                        "location": "Arcachon, Bassin d'Arcachon",
                        "station_id": obs.get('station_id', 'unknown')
                    }
                    return meteo_data
            
            # Si Météo-France n'est pas disponible, utiliser OpenWeatherMap comme fallback
            logger.warning("Météo-France API unavailable, using fallback")
            return await _get_meteo_openweather_fallback()
            
    except Exception as e:
        logger.error(f"Error fetching meteo data from Météo-France: {e}")
        # Fallback vers données simulées en cas d'erreur
        return await _get_meteo_simulated_fallback()

async def _get_meteo_openweather_fallback():
    """Fallback OpenWeatherMap si Météo-France indisponible"""
    import httpx
    import os
    
    # En production, ajouter OPENWEATHER_API_KEY dans .env
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        logger.warning("OpenWeatherMap API key not configured, using simulated data")
        return await _get_meteo_simulated_fallback()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Coordonnées Arcachon
            lat, lon = 44.65, -1.15
            
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                meteo_data = {
                    "wind_speed": data.get('wind', {}).get('speed', 0),
                    "wind_direction": _degrees_to_direction(data.get('wind', {}).get('deg', 0)),
                    "wave_height": 0,  # OpenWeatherMap ne fournit pas de vagues
                    "wave_period": 0,
                    "air_temp": data.get('main', {}).get('temp', 20),
                    "humidity": data.get('main', {}).get('humidity', 50),
                    "pressure": data.get('main', {}).get('pressure', 1013),
                    "last_update": datetime.utcnow().isoformat(),
                    "source": "OPENWEATHER_API",
                    "location": "Arcachon, Bassin d'Arcachon"
                }
                return meteo_data
                
    except Exception as e:
        logger.error(f"Error fetching meteo data from OpenWeatherMap: {e}")
    
    # Fallback final
    return await _get_meteo_simulated_fallback()

async def _get_meteo_simulated_fallback():
    """Fallback simulé si toutes les APIs échouent"""
    import random
    
    meteo_data = {
        "wind_speed": round(random.uniform(5, 25), 1),
        "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SO", "O", "NO"]),
        "wave_height": round(random.uniform(0.5, 3.0), 1),
        "wave_period": round(random.uniform(4, 12), 1),
        "air_temp": round(random.uniform(10, 30), 1),
        "humidity": random.randint(40, 90),
        "pressure": random.randint(980, 1030),
        "last_update": datetime.utcnow().isoformat(),
        "source": "SIMULATED_FALLBACK",
        "location": "Arcachon, Bassin d'Arcachon"
    }
    return meteo_data

def _degrees_to_direction(degrees: float) -> str:
    """Convertit les degrés en direction cardinale"""
    directions = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    index = round(degrees / 45) % 8
    return directions[index]

# @app.get("/api/v1/alerts/sacs", tags=["SACS Alerts"])
# async def check_sacs_alerts(station_id: Optional[str] = None):
#     """
#     Vérifie les alertes SACS (Vigilance Écologique)
#     TODO: Implémenter plus tard
#     """
#     return {"status": "not_implemented", "message": "SACS alerts not yet implemented"}

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "8000")),
        log_level="info",
        access_log=True
    )
