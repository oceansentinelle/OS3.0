#!/usr/bin/env python3
"""
Pipeline d'ingestion - Stockage PostgreSQL
"""
import logging
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

def get_db_connection():
    """Créer une connexion PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "oceansentinel"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin")
    )

def insert_hfr_measurement(measurement: Dict[str, Any], source: str = "HFR_CALYPSO") -> bool:
    """
    Insère une mesure HFR dans raw_ingestion_log.
    
    Args:
        measurement: Dictionnaire avec timestamp, u, v, qc
        source: Nom de la source de données
    
    Returns:
        True si succès, False sinon
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Sauvegarder le payload en JSON dans /tmp
        payload = {
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "station": "HFR_Virtual",
            "measurements": measurement
        }
        
        payload_filename = f"/tmp/hfr_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(payload_filename, 'w') as f:
            json.dump(payload, f)
        
        # Insérer dans raw_ingestion_log
        cursor.execute("""
            INSERT INTO raw_ingestion_log (
                source_name,
                fetched_at,
                status,
                records_fetched,
                records_rejected,
                payload_path,
                execution_time_ms
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            source,
            datetime.now(timezone.utc),
            'success',
            1 if measurement.get('u') is not None else 0,
            0 if measurement.get('u') is not None else 1,
            payload_filename,
            100
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Mesure HFR stockée | source={source} | timestamp={measurement.get('timestamp')}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur stockage PostgreSQL: {e}")
        return False

def insert_measurements_batch(measurements: List[Dict[str, Any]], source: str) -> int:
    """
    Insère un batch de mesures.
    
    Args:
        measurements: Liste de mesures
        source: Nom de la source
    
    Returns:
        Nombre de mesures insérées
    """
    if not measurements:
        return 0
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Préparer les données pour insertion batch
        values = [
            (
                source,
                datetime.now(timezone.utc),
                json.dumps(m),
                1
            )
            for m in measurements
        ]
        
        # Insertion batch
        execute_values(
            cursor,
            """
            INSERT INTO raw_ingestion_log (
                source_name,
                fetched_at,
                raw_data,
                record_count
            ) VALUES %s
            """,
            values
        )
        
        conn.commit()
        count = cursor.rowcount
        cursor.close()
        conn.close()
        
        logger.info(f"✅ {count} mesures stockées | source={source}")
        return count
        
    except Exception as e:
        logger.error(f"❌ Erreur stockage batch: {e}")
        return 0
