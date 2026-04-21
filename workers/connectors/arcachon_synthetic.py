"""
Connecteur synthétique Arcachon - Ocean Sentinel V3.1
Génère des données océanographiques réalistes pour le Bassin d'Arcachon
basées sur les patterns Copernicus Marine (IBI_ANALYSISFORECAST_PHY_005_001).

Conformité ABACODE 2.0 : Statut 'simulé' avec métadonnées traçables.
"""

import logging
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

# Ajout du chemin pour import dans conteneur Docker
sys.path.insert(0, '/app')
from workers.connectors.base import BaseConnector

logger = logging.getLogger(__name__)


class ArcachonSyntheticConnector(BaseConnector):
    """
    Générateur de données océanographiques synthétiques pour Arcachon.
    
    Variables simulées :
    - uo_detided : Courant Est-Ouest (m/s)
    - vo_detided : Courant Nord-Sud (m/s)
    - temperature : Température surface (°C)
    - salinity : Salinité (PSU)
    
    Résolution : 0.027° (~3 km) conforme Copernicus
    Zone : [44.4°N, 44.8°N] x [-1.5°W, -1.1°W]
    """
    
    SOURCE_NAME = "OceanSentinel-SynthNode-Arcachon"
    METHOD = "Interpolation-Climatologique-Copernicus-Pattern"
    STATUS = "simulé"
    UNCERTAINTY = 0.15  # ±15% par rapport moyennes historiques
    
    # Grille conforme Copernicus
    LAT_MIN, LAT_MAX = 44.4, 44.8
    LON_MIN, LON_MAX = -1.5, -1.1
    RESOLUTION = 0.027
    
    # Paramètres physiques réalistes Arcachon
    TIDAL_AMPLITUDE_U = 0.5  # m/s (marée semi-diurne)
    TIDAL_AMPLITUDE_V = 0.3  # m/s
    TIDAL_PERIOD = 12.42  # heures (M2)
    
    TEMP_MEAN = 15.0  # °C (moyenne annuelle)
    TEMP_AMPLITUDE = 8.0  # °C (variation saisonnière)
    
    SALINITY_MEAN = 32.0  # PSU
    SALINITY_AMPLITUDE = 3.0  # PSU (influence fluviale)
    
    def __init__(self, config: dict):
        super().__init__(source_code='ARCACHON_SYNTHETIC', config=config)
        self.center_lat = config.get('center_lat', 44.6)
        self.center_lon = config.get('center_lon', -1.2)
        logger.info(f"🌊 Connecteur synthétique Arcachon initialisé | center=({self.center_lat}, {self.center_lon})")
    
    def fetch_data(self, start_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Génère une mesure océanographique synthétique.
        
        Args:
            start_time: Timestamp ISO8601 (optionnel, défaut=now)
        
        Returns:
            Dict avec timestamp, u, v, temperature, salinity, qc_flag
        """
        try:
            # Timestamp
            if start_time:
                timestamp = pd.to_datetime(start_time)
            else:
                timestamp = datetime.now(timezone.utc)
            
            # Calcul composantes marée (cycle semi-diurne M2)
            hours_since_epoch = (timestamp - datetime(2024, 1, 1, tzinfo=timezone.utc)).total_seconds() / 3600
            tidal_phase = 2 * np.pi * hours_since_epoch / self.TIDAL_PERIOD
            
            # Courants (marée + bruit réaliste)
            u_tidal = self.TIDAL_AMPLITUDE_U * np.sin(tidal_phase)
            v_tidal = self.TIDAL_AMPLITUDE_V * np.cos(tidal_phase)
            
            u_noise = np.random.normal(0, 0.05)
            v_noise = np.random.normal(0, 0.05)
            
            u = u_tidal + u_noise
            v = v_tidal + v_noise
            
            # Température (cycle annuel + variation diurne)
            day_of_year = timestamp.timetuple().tm_yday
            seasonal_phase = 2 * np.pi * day_of_year / 365.25
            temp_seasonal = self.TEMP_MEAN + self.TEMP_AMPLITUDE * np.sin(seasonal_phase - np.pi/2)
            
            hour_of_day = timestamp.hour
            temp_diurnal = 1.5 * np.sin(2 * np.pi * hour_of_day / 24 - np.pi/2)
            
            temperature = temp_seasonal + temp_diurnal + np.random.normal(0, 0.3)
            
            # Salinité (influence marée + apports fluviaux)
            salinity_tidal = self.SALINITY_AMPLITUDE * np.sin(tidal_phase + np.pi/4)
            salinity = self.SALINITY_MEAN + salinity_tidal + np.random.normal(0, 0.5)
            
            # QC flag (1=bon, 4=manquant)
            qc_flag = 1 if np.random.random() > 0.05 else 4
            
            measurement = {
                "timestamp": timestamp.isoformat(),
                "latitude": self.center_lat,
                "longitude": self.center_lon,
                "u": round(float(u), 4) if qc_flag == 1 else None,
                "v": round(float(v), 4) if qc_flag == 1 else None,
                "temperature": round(float(temperature), 2) if qc_flag == 1 else None,
                "salinity": round(float(salinity), 2) if qc_flag == 1 else None,
                "qc_flag": qc_flag,
                "source": self.SOURCE_NAME,
                "method": self.METHOD,
                "status": self.STATUS,
                "uncertainty": self.UNCERTAINTY
            }
            
            logger.info(
                f"✅ Mesure synthétique générée | "
                f"timestamp={measurement['timestamp']} | "
                f"u={measurement['u']} m/s | "
                f"v={measurement['v']} m/s | "
                f"temp={measurement['temperature']}°C | "
                f"sal={measurement['salinity']} PSU"
            )
            
            return measurement
            
        except Exception as e:
            logger.error(f"❌ Erreur génération données synthétiques: {e}", exc_info=True)
            return None
    
    def generate_timeseries(self, start_date: str, days: int = 30, freq: str = 'H') -> list:
        """
        Génère une série temporelle de mesures synthétiques.
        
        Args:
            start_date: Date début ISO8601
            days: Nombre de jours
            freq: Fréquence ('H'=horaire, '10T'=10min)
        
        Returns:
            Liste de mesures
        """
        timestamps = pd.date_range(start=start_date, periods=days*24, freq=freq, tz='UTC')
        measurements = []
        
        for ts in timestamps:
            measurement = self.fetch_data(start_time=ts.isoformat())
            if measurement:
                measurements.append(measurement)
        
        logger.info(f"📊 Série temporelle générée | {len(measurements)} mesures | {days} jours")
        return measurements


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
    
    # Test génération mesure unique
    connector = ArcachonSyntheticConnector(config={
        'center_lat': 44.6,
        'center_lon': -1.2
    })
    
    measurement = connector.fetch_data()
    print("\n🌊 Mesure synthétique Arcachon:")
    print(f"Timestamp: {measurement['timestamp']}")
    print(f"Courant U (E-W): {measurement['u']} m/s")
    print(f"Courant V (N-S): {measurement['v']} m/s")
    print(f"Température: {measurement['temperature']}°C")
    print(f"Salinité: {measurement['salinity']} PSU")
    print(f"QC Flag: {measurement['qc_flag']}")
    print(f"Statut: {measurement['status']}")
    
    # Test série temporelle (7 jours, horaire)
    print("\n📊 Génération série temporelle 7 jours...")
    timeseries = connector.generate_timeseries(
        start_date="2026-04-14T00:00:00Z",
        days=7,
        freq='H'
    )
    print(f"✅ {len(timeseries)} mesures générées")
