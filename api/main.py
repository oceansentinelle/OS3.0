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

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

# Système d'alertes SACS
from alerts import SACSAlertSystem

# Routes
from api.routes import health as health_routes

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'timescaledb'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'oceansentinelle'),
    'user': os.getenv('DB_USER', 'oceansentinel'),
    'password': os.getenv('DB_PASSWORD', ''),
}

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
    logger.info(f"Connexion à {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    try:
        # Pool minimal pour économiser la RAM (2 connexions max)
        db_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=2,
            **DB_CONFIG
        )
        logger.info("✅ Pool de connexions créé (1-2 connexions)")
        
        # Initialiser le système d'alertes SACS
        sacs_alert_system = SACSAlertSystem(db_pool)
        logger.info("✅ Système d'alertes SACS initialisé")
        
    except Exception as e:
        logger.error(f"❌ Erreur création pool: {e}")
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
    description="API REST pour accès aux données océanographiques COAST-HF",
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

@app.get("/api/v1/alerts/sacs", tags=["SACS Alerts"])
async def check_sacs_alerts(station_id: Optional[str] = None):
    """
    Vérifie les alertes SACS (Vigilance Écologique)
    
    Seuils d'alerte:
    - pH < 7.8 : Acidification (CRITICAL)
    - pH < 7.9 : Acidification en approche (WARNING)
    - Oxygène dissous < 150 µmol/kg : Hypoxie (CRITICAL)
    - Oxygène dissous < 175 µmol/kg : Hypoxie en approche (WARNING)
    
    Args:
        station_id: ID de la station (optionnel, défaut: toutes)
    
    Returns:
        Dictionnaire des alertes actives
    """
    try:
        alerts = sacs_alert_system.check_all(station_id)
        
        return {
            "status": "checked",
            "station_id": station_id or "all",
            "timestamp": datetime.utcnow().isoformat(),
            "total_alerts": alerts['total'],
            "alerts": {
                "ph": [alert.to_dict() for alert in alerts['ph']],
                "oxygen": [alert.to_dict() for alert in alerts['oxygen']]
            },
            "sacs_protocol": True
        }
    except Exception as e:
        logger.error(f"Error checking SACS alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
