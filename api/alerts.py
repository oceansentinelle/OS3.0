#!/usr/bin/env python3
"""
============================================================================
Ocean Sentinel V3.0 - Système d'Alertes SACS
============================================================================
Description: Vigilance Écologique selon la constitution SACS
Seuils d'alerte:
  - pH < 7.8 : Acidification
  - Oxygène dissous (DOX2) < 150 µmol/kg : Hypoxie
============================================================================
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION SACS
# ============================================================================

class AlertLevel(str, Enum):
    """Niveaux d'alerte SACS"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(str, Enum):
    """Types d'alerte SACS"""
    PH_LOW = "ph_acidification"
    OXYGEN_LOW = "oxygen_hypoxia"

# Seuils d'alerte SACS (Constitution Écologique)
SACS_THRESHOLDS = {
    'ph': {
        'critical': 7.8,
        'warning': 7.9,
        'parameter': 'pH',
        'unit': '',
        'message_critical': 'Acidification détectée - pH < 7.8',
        'message_warning': 'Acidification en approche - pH < 7.9'
    },
    'dissolved_oxygen': {
        'critical': 150.0,
        'warning': 175.0,
        'parameter': 'Oxygène dissous (DOX2)',
        'unit': 'µmol/kg',
        'message_critical': 'Hypoxie détectée - O₂ < 150 µmol/kg',
        'message_warning': 'Hypoxie en approche - O₂ < 175 µmol/kg'
    }
}

# ============================================================================
# MODÈLES D'ALERTE
# ============================================================================

class Alert:
    """Modèle d'alerte SACS"""
    
    def __init__(
        self,
        alert_type: AlertType,
        level: AlertLevel,
        value: float,
        threshold: float,
        station_id: str,
        timestamp: datetime,
        message: str
    ):
        self.alert_type = alert_type
        self.level = level
        self.value = value
        self.threshold = threshold
        self.station_id = station_id
        self.timestamp = timestamp
        self.message = message
    
    def to_dict(self) -> Dict:
        """Convertit l'alerte en dictionnaire"""
        return {
            'alert_type': self.alert_type.value,
            'level': self.level.value,
            'value': self.value,
            'threshold': self.threshold,
            'station_id': self.station_id,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'sacs_protocol': True
        }
    
    def log(self):
        """Log l'alerte avec le format SACS"""
        emoji = "🔴" if self.level == AlertLevel.CRITICAL else "⚠️"
        logger.warning(
            f"{emoji} ALERTE SACS [{self.level.value.upper()}] - "
            f"{self.alert_type.value} - Station: {self.station_id} - "
            f"{self.message} (Valeur: {self.value})"
        )

# ============================================================================
# SYSTÈME DE VÉRIFICATION
# ============================================================================

class SACSAlertSystem:
    """Système d'alertes SACS (Vigilance Écologique)"""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.active_alerts: List[Alert] = []
    
    def check_ph_levels(self, station_id: str = None) -> List[Alert]:
        """
        Vérifie les niveaux de pH
        
        Args:
            station_id: ID de la station (None = toutes)
        
        Returns:
            Liste des alertes pH
        """
        alerts = []
        
        try:
            conn = self.db_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            station_id,
                            time,
                            ph
                        FROM barag.sensor_data
                        WHERE ph IS NOT NULL
                          AND quality_flag = 1
                          AND time >= NOW() - INTERVAL '1 hour'
                    """
                    
                    if station_id:
                        query += " AND station_id = %s"
                        cursor.execute(query, (station_id,))
                    else:
                        cursor.execute(query)
                    
                    results = cursor.fetchall()
                    
                    for row in results:
                        sid, timestamp, ph_value = row
                        
                        # Vérifier seuil critique
                        if ph_value < SACS_THRESHOLDS['ph']['critical']:
                            alert = Alert(
                                alert_type=AlertType.PH_LOW,
                                level=AlertLevel.CRITICAL,
                                value=ph_value,
                                threshold=SACS_THRESHOLDS['ph']['critical'],
                                station_id=sid,
                                timestamp=timestamp,
                                message=SACS_THRESHOLDS['ph']['message_critical']
                            )
                            alerts.append(alert)
                            alert.log()
                        
                        # Vérifier seuil warning
                        elif ph_value < SACS_THRESHOLDS['ph']['warning']:
                            alert = Alert(
                                alert_type=AlertType.PH_LOW,
                                level=AlertLevel.WARNING,
                                value=ph_value,
                                threshold=SACS_THRESHOLDS['ph']['warning'],
                                station_id=sid,
                                timestamp=timestamp,
                                message=SACS_THRESHOLDS['ph']['message_warning']
                            )
                            alerts.append(alert)
                            alert.log()
            
            finally:
                self.db_pool.putconn(conn)
        
        except Exception as e:
            logger.error(f"Erreur vérification pH: {e}")
        
        return alerts
    
    def check_oxygen_levels(self, station_id: str = None) -> List[Alert]:
        """
        Vérifie les niveaux d'oxygène dissous
        
        Args:
            station_id: ID de la station (None = toutes)
        
        Returns:
            Liste des alertes oxygène
        """
        alerts = []
        
        try:
            conn = self.db_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            station_id,
                            time,
                            dissolved_oxygen
                        FROM barag.sensor_data
                        WHERE dissolved_oxygen IS NOT NULL
                          AND quality_flag = 1
                          AND time >= NOW() - INTERVAL '1 hour'
                    """
                    
                    if station_id:
                        query += " AND station_id = %s"
                        cursor.execute(query, (station_id,))
                    else:
                        cursor.execute(query)
                    
                    results = cursor.fetchall()
                    
                    for row in results:
                        sid, timestamp, oxygen_value = row
                        
                        # Vérifier seuil critique
                        if oxygen_value < SACS_THRESHOLDS['dissolved_oxygen']['critical']:
                            alert = Alert(
                                alert_type=AlertType.OXYGEN_LOW,
                                level=AlertLevel.CRITICAL,
                                value=oxygen_value,
                                threshold=SACS_THRESHOLDS['dissolved_oxygen']['critical'],
                                station_id=sid,
                                timestamp=timestamp,
                                message=SACS_THRESHOLDS['dissolved_oxygen']['message_critical']
                            )
                            alerts.append(alert)
                            alert.log()
                        
                        # Vérifier seuil warning
                        elif oxygen_value < SACS_THRESHOLDS['dissolved_oxygen']['warning']:
                            alert = Alert(
                                alert_type=AlertType.OXYGEN_LOW,
                                level=AlertLevel.WARNING,
                                value=oxygen_value,
                                threshold=SACS_THRESHOLDS['dissolved_oxygen']['warning'],
                                station_id=sid,
                                timestamp=timestamp,
                                message=SACS_THRESHOLDS['dissolved_oxygen']['message_warning']
                            )
                            alerts.append(alert)
                            alert.log()
            
            finally:
                self.db_pool.putconn(conn)
        
        except Exception as e:
            logger.error(f"Erreur vérification oxygène: {e}")
        
        return alerts
    
    def check_all(self, station_id: str = None) -> Dict[str, List[Alert]]:
        """
        Vérifie tous les paramètres SACS
        
        Args:
            station_id: ID de la station (None = toutes)
        
        Returns:
            Dictionnaire des alertes par type
        """
        logger.info(f"🔍 Vérification SACS pour station: {station_id or 'toutes'}")
        
        ph_alerts = self.check_ph_levels(station_id)
        oxygen_alerts = self.check_oxygen_levels(station_id)
        
        all_alerts = {
            'ph': ph_alerts,
            'oxygen': oxygen_alerts,
            'total': len(ph_alerts) + len(oxygen_alerts)
        }
        
        if all_alerts['total'] > 0:
            logger.warning(
                f"⚠️ {all_alerts['total']} alerte(s) SACS détectée(s) - "
                f"pH: {len(ph_alerts)}, Oxygène: {len(oxygen_alerts)}"
            )
        else:
            logger.info("✅ Aucune alerte SACS - Paramètres écologiques normaux")
        
        return all_alerts
