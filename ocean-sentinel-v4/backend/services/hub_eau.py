"""
Client API Hub'Eau (BRGM)
Récupération données qualité eau littoral
"""

import httpx
from typing import Dict
from datetime import datetime
import logging

from config import settings

logger = logging.getLogger(__name__)


class HubEauClient:
    """Client HTTP pour API Hub'Eau"""
    
    def __init__(self):
        self.base_url = settings.hub_eau_api_url
        self.api_key = settings.hub_eau_api_key
        self.timeout = settings.http_timeout
    
    async def fetch_station_latest(self, station_code: str) -> Dict:
        """
        Récupère les dernières données d'une station Hub'Eau
        
        Args:
            station_code: Code station (ex: 06455X0001)
        
        Returns:
            Dict avec données brutes API
        """
        url = f"{self.base_url}/station"
        
        params = {
            "code_station": station_code,
            "size": 1,
            "sort": "desc"
        }
        
        headers = {
            "Accept": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"Fetching Hub'Eau data for station {station_code}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Successfully fetched Hub'Eau data for {station_code}")
                return data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching Hub'Eau {station_code}: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error fetching Hub'Eau {station_code}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error fetching Hub'Eau {station_code}: {e}")
                raise
    
    def transform_to_ocean_sentinel(
        self, 
        raw_data: Dict, 
        station_id: str
    ) -> Dict:
        """
        Transforme données Hub'Eau → format Ocean Sentinel
        
        Args:
            raw_data: Données brutes API Hub'Eau
            station_id: ID station Ocean Sentinel
        
        Returns:
            Dict format Ocean Sentinel
        """
        parameters = []
        
        # Hub'Eau retourne généralement un tableau "data"
        if "data" in raw_data and len(raw_data["data"]) > 0:
            station_data = raw_data["data"][0]
        else:
            station_data = raw_data
        
        # TEMP
        if "temperature" in station_data:
            temp_value = station_data["temperature"]
            parameters.append({
                "name": "TEMP",
                "value": float(temp_value),
                "unit": "°C",
                "status": "measured",
                "source": "Hub'Eau BRGM",
                "timestamp": station_data.get("date_mesure", datetime.utcnow().isoformat()),
                "quality_score": 0.98,
                "is_critical": float(temp_value) > 25.0
            })
        
        # PSAL
        if "salinite" in station_data or "salinity" in station_data:
            psal_value = station_data.get("salinite") or station_data.get("salinity")
            parameters.append({
                "name": "PSAL",
                "value": float(psal_value),
                "unit": "PSU",
                "status": "measured",
                "source": "Hub'Eau BRGM",
                "timestamp": station_data.get("date_mesure", datetime.utcnow().isoformat()),
                "quality_score": 0.96,
                "is_critical": False
            })
        
        # DOX2
        if "oxygene_dissous" in station_data or "dissolved_oxygen" in station_data:
            dox2_value = station_data.get("oxygene_dissous") or station_data.get("dissolved_oxygen")
            parameters.append({
                "name": "DOX2",
                "value": float(dox2_value),
                "unit": "µmol/kg",
                "status": "measured",
                "source": "Hub'Eau BRGM",
                "timestamp": station_data.get("date_mesure", datetime.utcnow().isoformat()),
                "quality_score": 0.90,
                "is_critical": float(dox2_value) < 150.0
            })
        
        # PH
        if "ph" in station_data:
            ph_value = station_data["ph"]
            parameters.append({
                "name": "PH_TOTAL",
                "value": float(ph_value),
                "unit": "",
                "status": "measured",
                "source": "Hub'Eau BRGM",
                "timestamp": station_data.get("date_mesure", datetime.utcnow().isoformat()),
                "quality_score": 0.94,
                "is_critical": float(ph_value) < 7.80
            })
        
        return {
            "station_id": station_id,
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": parameters
        }


# Instance globale
hub_eau_client = HubEauClient()
