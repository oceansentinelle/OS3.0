"""
Client API COAST-HF (Ifremer)
Récupération données océanographiques temps réel
"""

import httpx
from typing import Dict, Optional
from datetime import datetime
import logging

from config import settings

logger = logging.getLogger(__name__)


class CoastHFClient:
    """Client HTTP pour API COAST-HF"""
    
    def __init__(self):
        self.base_url = settings.coast_hf_api_url
        self.api_key = settings.coast_hf_api_key
        self.timeout = settings.http_timeout
    
    async def fetch_station_latest(self, station_code: str) -> Dict:
        """
        Récupère les dernières données d'une station COAST-HF
        
        Args:
            station_code: Code station (ex: BARAG)
        
        Returns:
            Dict avec données brutes API
        
        Raises:
            httpx.HTTPError: Si erreur HTTP
        """
        url = f"{self.base_url}/stations/{station_code}/latest"
        
        headers = {
            "Accept": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"Fetching COAST-HF data for station {station_code}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Successfully fetched COAST-HF data for {station_code}")
                return data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching COAST-HF {station_code}: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error fetching COAST-HF {station_code}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error fetching COAST-HF {station_code}: {e}")
                raise
    
    def transform_to_ocean_sentinel(
        self, 
        raw_data: Dict, 
        station_id: str
    ) -> Dict:
        """
        Transforme données COAST-HF → format Ocean Sentinel
        
        Args:
            raw_data: Données brutes API COAST-HF
            station_id: ID station Ocean Sentinel
        
        Returns:
            Dict format Ocean Sentinel
        """
        parameters = []
        
        # Mapping COAST-HF → Ocean Sentinel
        # À adapter selon le format réel de l'API COAST-HF
        
        # TEMP (Température)
        if "temperature" in raw_data or "TEMP" in raw_data:
            temp_value = raw_data.get("temperature") or raw_data.get("TEMP")
            parameters.append({
                "name": "TEMP",
                "value": float(temp_value),
                "unit": "°C",
                "status": "measured",
                "source": "COAST-HF Ifremer",
                "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
                "quality_score": raw_data.get("quality", 0.95),
                "is_critical": float(temp_value) > 25.0
            })
        
        # PSAL (Salinité)
        if "salinity" in raw_data or "PSAL" in raw_data:
            psal_value = raw_data.get("salinity") or raw_data.get("PSAL")
            parameters.append({
                "name": "PSAL",
                "value": float(psal_value),
                "unit": "PSU",
                "status": "measured",
                "source": "COAST-HF Ifremer",
                "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
                "quality_score": raw_data.get("quality", 0.92),
                "is_critical": False
            })
        
        # DOX2 (Oxygène dissous)
        if "dissolved_oxygen" in raw_data or "DOX2" in raw_data:
            dox2_value = raw_data.get("dissolved_oxygen") or raw_data.get("DOX2")
            parameters.append({
                "name": "DOX2",
                "value": float(dox2_value),
                "unit": "µmol/kg",
                "status": "measured",
                "source": "COAST-HF Ifremer",
                "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
                "quality_score": raw_data.get("quality", 0.88),
                "is_critical": float(dox2_value) < 150.0
            })
        
        # PH_TOTAL
        if "ph" in raw_data or "PH_TOTAL" in raw_data:
            ph_value = raw_data.get("ph") or raw_data.get("PH_TOTAL")
            parameters.append({
                "name": "PH_TOTAL",
                "value": float(ph_value),
                "unit": "",
                "status": "measured",
                "source": "COAST-HF Ifremer",
                "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
                "quality_score": raw_data.get("quality", 0.90),
                "is_critical": float(ph_value) < 7.80
            })
        
        return {
            "station_id": station_id,
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": parameters
        }


# Instance globale
coast_hf_client = CoastHFClient()
