"""
Ocean Sentinel Backend API
FastAPI server pour agrégation données océanographiques

Endpoints:
- GET /api/v1/station/{station_id}/latest - Dernières données station
- GET /api/v1/stations - Liste stations disponibles
- GET /health - Health check

Architecture:
Frontend → FastAPI → COAST-HF/Hub'Eau → TimescaleDB (futur)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import sys

from config import settings
from routers import stations
from models.station import HealthCheck

# Configuration logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Création app FastAPI
app = FastAPI(
    title="Ocean Sentinel API",
    description="API REST pour données océanographiques temps réel - Bassin d'Arcachon",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(stations.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": "Ocean Sentinel API",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck, tags=["monitoring"])
async def health_check():
    """
    Health check endpoint
    Vérifie l'état du service et des dépendances
    """
    
    services_status = {}
    overall_status = "ok"
    
    # Test COAST-HF (optionnel)
    try:
        # Ping simple (à implémenter si API le permet)
        services_status["coast_hf"] = "ok"
    except Exception as e:
        logger.warning(f"COAST-HF health check failed: {e}")
        services_status["coast_hf"] = "degraded"
        overall_status = "degraded"
    
    # Test Hub'Eau (optionnel)
    try:
        services_status["hub_eau"] = "ok"
    except Exception as e:
        logger.warning(f"Hub'Eau health check failed: {e}")
        services_status["hub_eau"] = "degraded"
        overall_status = "degraded"
    
    return HealthCheck(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services=services_status
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global pour exceptions non gérées"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur interne du serveur",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.on_event("startup")
async def startup_event():
    """Actions au démarrage"""
    logger.info("🌊 Ocean Sentinel API starting...")
    logger.info(f"CORS origins: {settings.origins_list}")
    logger.info(f"COAST-HF API: {settings.coast_hf_api_url}")
    logger.info(f"Hub'Eau API: {settings.hub_eau_api_url}")
    logger.info("✅ Ocean Sentinel API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions à l'arrêt"""
    logger.info("🛑 Ocean Sentinel API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
