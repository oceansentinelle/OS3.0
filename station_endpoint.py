"""
Endpoint API pour récupérer les dernières mesures d'une station
Compatible avec la Règle de Vérité SACS
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os

router = APIRouter()

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class Parameter(BaseModel):
    """Paramètre océanographique avec Règle de Vérité SACS"""
    name: str = Field(..., description="Nom du paramètre (TEMP, PSAL, DOX2, PH_TOTAL)")
    value: float = Field(..., description="Valeur mesurée")
    unit: str = Field(..., description="Unité de mesure")
    status: Literal["measured", "inferred", "simulated"] = Field(
        ..., 
        description="Statut de fiabilité (Règle de Vérité SACS)"
    )
    source: str = Field(..., description="Source de la donnée")
    timestamp: datetime = Field(..., description="Timestamp de la mesure (UTC)")
    quality_score: float = Field(..., description="Score de qualité (0-1)")
    is_critical: bool = Field(default=False, description="Alerte critique déclenchée")

class StationLatestResponse(BaseModel):
    """Réponse pour les dernières mesures d'une station"""
    station_id: str = Field(..., description="Identifiant de la station")
    timestamp: datetime = Field(..., description="Timestamp de la dernière mise à jour")
    parameters: List[Parameter] = Field(..., description="Liste des paramètres")

# ============================================================================
# SEUILS CRITIQUES SACS
# ============================================================================

CRITICAL_THRESHOLDS = {
    'DOX2': {'operator': '<', 'value': 150, 'alert_type': 'HYPOXIE'},
    'PH_TOTAL': {'operator': '<', 'value': 7.80, 'alert_type': 'ACIDIFICATION'},
    'TEMP': {'operator': '>', 'value': 25, 'alert_type': 'TEMPÉRATURE ÉLEVÉE'},
}

def check_critical(variable: str, value: float) -> bool:
    """Vérifie si une valeur dépasse un seuil critique"""
    if variable not in CRITICAL_THRESHOLDS:
        return False
    
    threshold = CRITICAL_THRESHOLDS[variable]
    if threshold['operator'] == '<':
        return value < threshold['value']
    elif threshold['operator'] == '>':
        return value > threshold['value']
    return False

# ============================================================================
# ENDPOINT
# ============================================================================

@router.get(
    "/api/v1/station/{station_id}/latest",
    response_model=StationLatestResponse,
    summary="Dernières mesures d'une station",
    description="Récupère les 4 paramètres principaux (TEMP, PSAL, DOX2, PH_TOTAL) avec badges de vérité"
)
async def get_station_latest(station_id: str):
    """
    Récupère les dernières mesures validées d'une station.
    
    **Règle de Vérité SACS** :
    - `measured` : Donnée capteur direct (fiabilité 100%)
    - `inferred` : Proxy satellitaire (fiabilité 70-90%)
    - `simulated` : Modèle numérique (fiabilité 50-70%)
    
    **Seuils critiques** :
    - DOX2 < 150 µmol/kg → HYPOXIE
    - PH_TOTAL < 7.80 → ACIDIFICATION
    - TEMP > 25°C → TEMPÉRATURE ÉLEVÉE
    """
    
    # Connexion DB
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'postgres'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'oceansentinel'),
            user=os.getenv('DB_USER', 'admin'),
            password=os.getenv('DB_PASSWORD', ''),
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Requête optimisée : dernière mesure de chaque variable
        query = """
        WITH latest_per_variable AS (
            SELECT DISTINCT ON (variable)
                variable,
                value,
                unit,
                data_status,
                data_source,
                timestamp_utc,
                quality_score
            FROM validated_measurements
            WHERE station_id = %s
              AND variable IN ('TEMP', 'PSAL', 'DOX2', 'PH_TOTAL')
            ORDER BY variable, timestamp_utc DESC
        )
        SELECT * FROM latest_per_variable
        ORDER BY variable;
        """
        
        cursor.execute(query, (station_id,))
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune donnée trouvée pour la station {station_id}"
            )
        
        # Construction de la réponse
        parameters = []
        latest_timestamp = None
        
        for row in rows:
            # Vérifier seuil critique
            is_critical = check_critical(row['variable'], row['value'])
            
            param = Parameter(
                name=row['variable'],
                value=row['value'],
                unit=row['unit'],
                status=row['data_status'],
                source=row['data_source'],
                timestamp=row['timestamp_utc'],
                quality_score=row['quality_score'],
                is_critical=is_critical
            )
            parameters.append(param)
            
            # Garder le timestamp le plus récent
            if latest_timestamp is None or row['timestamp_utc'] > latest_timestamp:
                latest_timestamp = row['timestamp_utc']
        
        cursor.close()
        conn.close()
        
        return StationLatestResponse(
            station_id=station_id,
            timestamp=latest_timestamp,
            parameters=parameters
        )
        
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur base de données: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )
