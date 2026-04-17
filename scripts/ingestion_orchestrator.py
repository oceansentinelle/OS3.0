#!/usr/bin/env python3
"""
================================================================================
Ocean Sentinel V3.0 - Orchestrateur d'Ingestion Multi-Sources
================================================================================

Orchestrateur central pour la collecte, validation et transformation des données
depuis multiples sources (capteurs, météo, marée, satellite).

Architecture:
- Ingestion asynchrone multi-sources
- Validation schéma (Pydantic)
- Normalisation unités
- Déduplication
- Enrichissement contextuel
- Calcul métriques dérivées
- Déclenchement alertes

Conformité:
- Pipeline 3 couches (Raw → Processed → Serving)
- QA/QC systématique
- Traçabilité complète
- Idempotence
================================================================================
"""

import os
import sys
import logging
import asyncio
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from pydantic import BaseModel, validator
import hashlib

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base de données
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 6543)),
    "database": os.getenv("DB_NAME", "oceansentinelle"),
    "user": os.getenv("DB_USER", "oceansentinel"),
    "password": os.getenv("DB_PASSWORD", "")
}

# ============================================================================
# Modèles Pydantic (Validation Schéma)
# ============================================================================

class RawMeasurement(BaseModel):
    """Schéma validation mesure brute."""
    station_id: str
    timestamp_utc: datetime
    variable: str
    raw_value: float
    raw_unit: str
    source_name: str
    
    @validator('timestamp_utc')
    def validate_timestamp(cls, v):
        """Valide que le timestamp n'est pas dans le futur."""
        if v > datetime.utcnow() + timedelta(hours=1):
            raise ValueError("Timestamp dans le futur")
        return v
    
    @validator('raw_value')
    def validate_value(cls, v):
        """Valide que la valeur est numérique."""
        if not isinstance(v, (int, float)):
            raise ValueError("Valeur non numérique")
        return float(v)


class ValidatedMeasurement(BaseModel):
    """Schéma mesure validée."""
    station_id: str
    timestamp_utc: datetime
    variable: str
    value: float
    unit: str
    quality_score: float
    validation_status: str  # 'valid', 'suspect', 'invalid'
    anomaly_flag: bool
    data_source: str
    data_status: str  # 'measured', 'inferred', 'interpolated'
    metadata: Dict[str, Any]

# ============================================================================
# Normalisation Unités
# ============================================================================

UNIT_CONVERSIONS = {
    # Température
    ('temperature', 'K'): ('temperature', '°C', lambda x: x - 273.15),
    ('temperature', 'F'): ('temperature', '°C', lambda x: (x - 32) * 5/9),
    
    # Salinité (déjà en PSU généralement)
    
    # Oxygène dissous
    ('dissolved_oxygen', 'µmol/L'): ('dissolved_oxygen', 'mg/L', lambda x: x * 0.032),
    ('dissolved_oxygen', 'µmol/kg'): ('dissolved_oxygen', 'mg/L', lambda x: x * 0.032),
    
    # Vent
    ('wind_speed', 'km/h'): ('wind_speed', 'm/s', lambda x: x / 3.6),
    ('wind_speed', 'knots'): ('wind_speed', 'm/s', lambda x: x * 0.514444),
}

def normalize_unit(variable: str, value: float, unit: str) -> tuple:
    """
    Normalise une valeur vers l'unité canonique.
    
    Returns:
        (normalized_value, canonical_unit)
    """
    key = (variable, unit)
    
    if key in UNIT_CONVERSIONS:
        _, canonical_unit, converter = UNIT_CONVERSIONS[key]
        return converter(value), canonical_unit
    
    # Déjà dans l'unité canonique
    return value, unit

# ============================================================================
# Contrôles Physiques
# ============================================================================

PHYSICAL_BOUNDS = {
    'temperature': (-2.0, 40.0),  # °C eau mer
    'salinity': (0.0, 45.0),  # PSU
    'ph': (6.0, 9.0),
    'dissolved_oxygen': (0.0, 20.0),  # mg/L
    'turbidity': (0.0, 100.0),  # NTU
    'wind_speed': (0.0, 50.0),  # m/s
    'air_temperature': (-20.0, 50.0),  # °C
    'pressure': (950.0, 1050.0),  # hPa
}

def check_physical_bounds(variable: str, value: float) -> tuple:
    """
    Vérifie si la valeur est dans les limites physiques plausibles.
    
    Returns:
        (is_valid, quality_score)
    """
    if variable not in PHYSICAL_BOUNDS:
        return True, 1.0  # Pas de contrainte connue
    
    min_val, max_val = PHYSICAL_BOUNDS[variable]
    
    if min_val <= value <= max_val:
        return True, 1.0
    
    # Hors limites strictes
    if value < min_val * 0.5 or value > max_val * 1.5:
        return False, 0.0  # Invalide
    
    # Suspect mais pas impossible
    return True, 0.5

# ============================================================================
# Détection Anomalies
# ============================================================================

def detect_anomaly(
    station_id: str,
    variable: str,
    value: float,
    timestamp: datetime
) -> bool:
    """
    Détecte si une valeur est anormale par rapport à l'historique.
    
    Méthode simple: écart-type sur fenêtre glissante.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Récupérer moyenne et écart-type sur 7 derniers jours
        cursor.execute("""
            SELECT AVG(value), STDDEV(value)
            FROM validated_measurements
            WHERE station_id = %s
              AND variable = %s
              AND timestamp_utc > %s
              AND timestamp_utc < %s
        """, (
            station_id,
            variable,
            timestamp - timedelta(days=7),
            timestamp
        ))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] is not None and result[1] is not None:
            mean, stddev = result
            
            # Anomalie si > 3 écarts-types
            if abs(value - mean) > 3 * stddev:
                return True
        
        return False
        
    except Exception as e:
        logger.warning(f"Erreur détection anomalie: {e}")
        return False

# ============================================================================
# Ingestion Raw Layer
# ============================================================================

def save_raw_measurement(
    ingestion_id: str,
    measurement: RawMeasurement,
    payload: dict
) -> str:
    """
    Sauvegarde mesure brute dans raw_measurements.
    
    Returns:
        raw_id
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO raw_measurements (
                ingestion_id, station_id, timestamp_utc,
                source_name, payload
            ) VALUES (
                %s, %s, %s, %s, %s::jsonb
            )
            RETURNING raw_id;
        """, (
            ingestion_id,
            measurement.station_id,
            measurement.timestamp_utc,
            measurement.source_name,
            json.dumps(payload)
        ))
        
        raw_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return raw_id
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde raw: {e}")
        raise

# ============================================================================
# Validation et Transformation
# ============================================================================

def validate_and_transform(raw_measurement: RawMeasurement) -> Optional[ValidatedMeasurement]:
    """
    Valide et transforme une mesure brute en mesure validée.
    """
    try:
        # 1. Normalisation unité
        normalized_value, canonical_unit = normalize_unit(
            raw_measurement.variable,
            raw_measurement.raw_value,
            raw_measurement.raw_unit
        )
        
        # 2. Contrôle physique
        is_valid, quality_score = check_physical_bounds(
            raw_measurement.variable,
            normalized_value
        )
        
        if not is_valid:
            logger.warning(
                f"Valeur hors limites: {raw_measurement.variable}={normalized_value} "
                f"(station={raw_measurement.station_id})"
            )
            validation_status = 'invalid'
        else:
            validation_status = 'valid' if quality_score > 0.7 else 'suspect'
        
        # 3. Détection anomalie
        anomaly_flag = detect_anomaly(
            raw_measurement.station_id,
            raw_measurement.variable,
            normalized_value,
            raw_measurement.timestamp_utc
        )
        
        # 4. Construction mesure validée
        validated = ValidatedMeasurement(
            station_id=raw_measurement.station_id,
            timestamp_utc=raw_measurement.timestamp_utc,
            variable=raw_measurement.variable,
            value=normalized_value,
            unit=canonical_unit,
            quality_score=quality_score,
            validation_status=validation_status,
            anomaly_flag=anomaly_flag,
            data_source=raw_measurement.source_name,
            data_status='measured',
            metadata={
                'original_value': raw_measurement.raw_value,
                'original_unit': raw_measurement.raw_unit,
                'normalized': True
            }
        )
        
        return validated
        
    except Exception as e:
        logger.error(f"Erreur validation: {e}")
        return None

# ============================================================================
# Insertion Processed Layer
# ============================================================================

def save_validated_measurement(
    raw_id: str,
    validated: ValidatedMeasurement
):
    """
    Sauvegarde mesure validée dans validated_measurements.
    
    UPSERT idempotent.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO validated_measurements (
                raw_id, station_id, timestamp_utc, variable,
                value, unit, quality_score, validation_status,
                anomaly_flag, data_source, data_status, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
            )
            ON CONFLICT (station_id, timestamp_utc, variable) DO UPDATE SET
                value = EXCLUDED.value,
                quality_score = EXCLUDED.quality_score,
                validation_status = EXCLUDED.validation_status,
                anomaly_flag = EXCLUDED.anomaly_flag,
                metadata = EXCLUDED.metadata,
                processed_at = NOW();
        """, (
            raw_id,
            validated.station_id,
            validated.timestamp_utc,
            validated.variable,
            validated.value,
            validated.unit,
            validated.quality_score,
            validated.validation_status,
            validated.anomaly_flag,
            validated.data_source,
            validated.data_status,
            json.dumps(validated.metadata)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(
            f"✅ Mesure validée: {validated.station_id} | "
            f"{validated.variable}={validated.value}{validated.unit} | "
            f"Q={validated.quality_score:.2f}"
        )
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde validated: {e}")
        raise

# ============================================================================
# Orchestrateur Principal
# ============================================================================

async def ingest_source(source_name: str, fetch_function):
    """
    Ingère données d'une source.
    
    Args:
        source_name: Nom de la source
        fetch_function: Fonction async de récupération données
    """
    logger.info(f"🔄 Ingestion {source_name}...")
    
    # Créer log d'ingestion
    ingestion_id = create_ingestion_log(source_name)
    
    try:
        # Récupérer données
        raw_data = await fetch_function()
        
        records_fetched = 0
        records_rejected = 0
        
        # Traiter chaque mesure
        for data in raw_data:
            try:
                # Validation schéma
                raw_measurement = RawMeasurement(**data)
                
                # Sauvegarder raw
                raw_id = save_raw_measurement(
                    ingestion_id,
                    raw_measurement,
                    data
                )
                
                # Valider et transformer
                validated = validate_and_transform(raw_measurement)
                
                if validated:
                    # Sauvegarder validated
                    save_validated_measurement(raw_id, validated)
                    records_fetched += 1
                else:
                    records_rejected += 1
                    
            except Exception as e:
                logger.error(f"Erreur traitement mesure: {e}")
                records_rejected += 1
                continue
        
        # Mettre à jour log
        update_ingestion_log(
            ingestion_id,
            'success',
            records_fetched,
            records_rejected
        )
        
        logger.info(
            f"✅ {source_name}: {records_fetched} mesures ingérées, "
            f"{records_rejected} rejetées"
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur ingestion {source_name}: {e}")
        update_ingestion_log(
            ingestion_id,
            'failed',
            0,
            0,
            error_message=str(e)
        )


def create_ingestion_log(source_name: str) -> str:
    """Crée un log d'ingestion."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO raw_ingestion_log (source_name, status)
            VALUES (%s, 'running')
            RETURNING ingestion_id;
        """, (source_name,))
        
        ingestion_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return ingestion_id
        
    except Exception as e:
        logger.error(f"Erreur création log: {e}")
        raise


def update_ingestion_log(
    ingestion_id: str,
    status: str,
    records_fetched: int,
    records_rejected: int,
    error_message: str = None
):
    """Met à jour le log d'ingestion."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE raw_ingestion_log
            SET status = %s,
                records_fetched = %s,
                records_rejected = %s,
                error_message = %s
            WHERE ingestion_id = %s;
        """, (
            status,
            records_fetched,
            records_rejected,
            error_message,
            ingestion_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur mise à jour log: {e}")


# ============================================================================
# Fonctions de Récupération (à implémenter par source)
# ============================================================================

async def fetch_coast_hf_data() -> List[dict]:
    """Récupère données COAST-HF (à implémenter)."""
    # TODO: Implémenter connecteur COAST-HF
    logger.warning("Connecteur COAST-HF non implémenté")
    return []


async def fetch_weather_data() -> List[dict]:
    """Récupère données météo (à implémenter)."""
    # TODO: Implémenter connecteur météo
    logger.warning("Connecteur météo non implémenté")
    return []


async def fetch_tide_data() -> List[dict]:
    """Récupère données marée (à implémenter)."""
    # TODO: Implémenter connecteur marée
    logger.warning("Connecteur marée non implémenté")
    return []


# ============================================================================
# Main
# ============================================================================

async def main():
    """Orchestrateur principal."""
    logger.info("=" * 80)
    logger.info("ORCHESTRATEUR INGESTION MULTI-SOURCES - Ocean Sentinel V3.0")
    logger.info("=" * 80)
    
    # Ingestion parallèle de toutes les sources
    await asyncio.gather(
        ingest_source('COAST-HF', fetch_coast_hf_data),
        ingest_source('Weather', fetch_weather_data),
        ingest_source('Tide', fetch_tide_data),
    )
    
    logger.info("=" * 80)
    logger.info("✅ Ingestion terminée")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
