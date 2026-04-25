#!/usr/bin/env python3
"""
================================================================================
Health Checks - Ocean Sentinel V3.0
================================================================================

Endpoints de santé pour monitoring et smoke tests.

Endpoints:
- GET /api/v1/health - Health check basique
- GET /api/v1/pipeline/status - Statut pipeline complet

================================================================================
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import psycopg2
import os

router = APIRouter()

# Configuration base de données
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "oceansentinel"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "")
}


@router.get("/health")
async def health_check():
    """
    Health check basique.
    
    Vérifie:
    - API responsive
    - Timestamp UTC
    
    Returns:
        Status healthy avec timestamp
    """
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "ocean_sentinel_api"
    }


@router.get("/pipeline/status")
async def pipeline_status():
    """
    Statut complet du pipeline.
    
    Vérifie:
    - Connexion base de données
    - Dernières ingestions par source
    - Nombre de mesures récentes
    - Sources actives
    
    Returns:
        Statut détaillé du pipeline
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Vérifier connexion DB
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        
        # Compter sources actives
        cursor.execute("""
            SELECT COUNT(*) FROM sources WHERE is_active = TRUE;
        """)
        active_sources = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
        
        # Dernières ingestions
        cursor.execute("""
            SELECT 
                source_name,
                MAX(fetched_at) as last_fetch,
                COUNT(*) as total_ingestions
            FROM raw_ingestion_log
            WHERE fetched_at > NOW() - INTERVAL '24 hours'
            GROUP BY source_name
            ORDER BY last_fetch DESC
            LIMIT 10;
        """)
        
        recent_ingestions = []
        for row in cursor.fetchall():
            recent_ingestions.append({
                "source": row[0],
                "last_fetch": row[1].isoformat() if row[1] else None,
                "count_24h": row[2]
            })
        
        # Compter mesures validées récentes
        cursor.execute("""
            SELECT COUNT(*) 
            FROM validated_measurements
            WHERE timestamp_utc > NOW() - INTERVAL '24 hours';
        """)
        recent_measurements = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
        
        # Compter alertes actives
        cursor.execute("""
            SELECT COUNT(*) 
            FROM alerts
            WHERE status = 'active';
        """)
        active_alerts = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
        
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {
                "connected": True,
                "version": db_version.split()[0:2]  # PostgreSQL version
            },
            "sources": {
                "active": active_sources,
                "recent_ingestions": recent_ingestions
            },
            "measurements": {
                "validated_24h": recent_measurements
            },
            "alerts": {
                "active": active_alerts
            }
        }
        
    except psycopg2.Error as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": "database_connection_failed",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": "internal_error",
                "message": str(e)
            }
        )
