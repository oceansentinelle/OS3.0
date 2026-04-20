#!/usr/bin/env python3
"""
Connecteur EUSKOOS HFR (v3.1)
Intégration via EMODnet Physics (Miroir EU HFR Node)
"""
import logging
import json
import requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Configuration du logging structuré (AZTRM-D compliant)
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(module)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("euskoos_hfr")

class ArcachonHFRConnector:
    """Connecteur pour les courants de surface via ERDDAP griddap."""
    
    BASE_URL = "https://erddap.hfrnode.eu/erddap/griddap"
    DATASET_ID = "EUHFR_NRTcurrent_HFR-CALYPSO-LICA_v3"  # Dataset test Méditerranée

    def fetch_data(self, lat: float = 43.2, lon: float = 9.5) -> Optional[Dict[str, Any]]:
        """
        Récupère les vecteurs de courant (u, v) au point GPS spécifié.
        Coordonnées par défaut: Méditerranée (CALYPSO-LICA)
        """
        # Format griddap : dimension[indice_start:stride:indice_stop]
        # On cible le dernier temps (last) et la surface (depth=0.0)
        query = (
            f"{self.DATASET_ID}.json"
            f"?EWCT[(last)][(0.0):1:(0.0)][({lat}):1:({lat})][({lon}):1:({lon})],"
            f"NSCT[(last)][(0.0):1:(0.0)][({lat}):1:({lat})][({lon}):1:({lon})],"
            f"QCflag[(last)][(0.0):1:(0.0)][({lat}):1:({lat})][({lon}):1:({lon})]"
        )
        url = f"{self.BASE_URL}/{query}"

        try:
            logger.info(f"Initiating request to EMODnet: {self.DATASET_ID}")
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            
            # Extraction des données de la structure JSON ERDDAP
            table = response.json().get('table', {})
            rows = table.get('rows', [])
            
            if not rows:
                logger.warning(f"No rows found for coordinates {lat}, {lon}")
                return None

            data = rows[0]  # Contient [time, depth, lat, lon, u, v, qc]
            return {
                "timestamp": data[0],
                "u": round(data[4], 3) if data[4] is not None else None,
                "v": round(data[5], 3) if data[5] is not None else None,
                "qc": int(data[6]) if data[6] is not None else 0
            }
        except Exception as e:
            logger.error(f"Ingestion Error | {type(e).__name__}: {str(e)}")
            return None

    def save_to_db(self, record: Dict[str, Any]):
        """Simulation de l'appel à l'API interne ou stockage direct en base."""
        payload = {
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "source": self.DATASET_ID,
            "station": "Bouee_13_Virtual",
            "measurements": record
        }
        
        # Log pour validation DevOps
        logger.info(f"STORE_CMD | data={json.dumps(payload)}")
        # Note: En production, on utilise ici le client SQLAlchemy ou httpx vers l'API
        print(f"✅ SUCCESS | Timestamp: {record['timestamp']} | U: {record['u']} m/s | V: {record['v']} m/s")

if __name__ == "__main__":
    # Coordonnées test Méditerranée (CALYPSO-LICA)
    connector = ArcachonHFRConnector()
    result = connector.fetch_data()  # Utilise coordonnées par défaut
    if result:
        connector.save_to_db(result)
    else:
        logger.critical("Data fetch failed. Check network or Dataset ID.")
