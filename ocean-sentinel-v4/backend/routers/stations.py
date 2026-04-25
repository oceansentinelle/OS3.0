"""
Routes API stations
Endpoints pour récupération données océanographiques
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

from models.station import StationData
from services.coast_hf import coast_hf_client
from services.hub_eau import hub_eau_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["stations"])


# Configuration stations
STATION_CONFIG: Dict[str, Dict] = {
    "BARAG_PROXY": {
        "api": "coast-hf",
        "station_code": "BARAG",
        "source": "COAST-HF Ifremer",
        "description": "Bouée COAST-HF Bassin d'Arcachon"
    },
    "ARCACHON_EYRAC": {
        "api": "hub-eau",
        "station_code": "06455X0001",
        "source": "Hub'Eau BRGM",
        "description": "Station Arcachon Eyrac"
    }
}


@router.get(
    "/station/{station_id}/latest",
    response_model=StationData,
    summary="Dernières données station",
    description="Récupère les dernières mesures océanographiques d'une station"
)
async def get_station_latest(station_id: str) -> StationData:
    """
    Récupère les dernières données d'une station
    
    Args:
        station_id: Identifiant station (BARAG_PROXY, ARCACHON_EYRAC)
    
    Returns:
        StationData avec paramètres TEMP, PSAL, DOX2, PH_TOTAL
    
    Raises:
        HTTPException 404: Station non trouvée
        HTTPException 500: Erreur API externe
    """
    
    # Vérifier station existe
    if station_id not in STATION_CONFIG:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' non trouvée. Stations disponibles: {list(STATION_CONFIG.keys())}"
        )
    
    config = STATION_CONFIG[station_id]
    
    try:
        # Fetch selon l'API
        if config["api"] == "coast-hf":
            logger.info(f"Fetching COAST-HF data for {station_id}")
            raw_data = await coast_hf_client.fetch_station_latest(config["station_code"])
            transformed_data = coast_hf_client.transform_to_ocean_sentinel(raw_data, station_id)
            
        elif config["api"] == "hub-eau":
            logger.info(f"Fetching Hub'Eau data for {station_id}")
            raw_data = await hub_eau_client.fetch_station_latest(config["station_code"])
            transformed_data = hub_eau_client.transform_to_ocean_sentinel(raw_data, station_id)
            
        else:
            raise HTTPException(
                status_code=500,
                detail=f"API '{config['api']}' non supportée"
            )
        
        # Valider avec Pydantic
        station_data = StationData(**transformed_data)
        
        logger.info(f"Successfully returned data for {station_id}")
        return station_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching station {station_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération données: {str(e)}"
        )


@router.get(
    "/stations",
    summary="Liste stations",
    description="Retourne la liste des stations disponibles"
)
async def list_stations() -> Dict:
    """Liste toutes les stations disponibles"""
    return {
        "count": len(STATION_CONFIG),
        "stations": [
            {
                "id": station_id,
                "source": config["source"],
                "description": config["description"]
            }
            for station_id, config in STATION_CONFIG.items()
        ]
    }
