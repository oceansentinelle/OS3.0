#!/usr/bin/env python3
"""
================================================================================
Seed Sources - Ocean Sentinel V3.0
================================================================================

Script pour initialiser la table `sources` avec toutes les sources configurées.

Sources Phase 1 (MVP):
- erddap_coast_hf
- erddap_somlit
- hubeau
- seanoe
- siba_enki

Sources Phase 2 (Référentiels):
- shom_reference
- insee_geo
- insee_sirene

Usage:
    python scripts/seed_sources.py

================================================================================
"""

import os
import sys
import psycopg2
import psycopg2.extras
from datetime import datetime

# Configuration base de données
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "oceansentinel"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "")
}

# Définition des sources
SOURCES = [
    # Phase 1 - MVP
    {
        "code": "erddap_coast_hf",
        "nom": "ERDDAP COAST-HF Arcachon-Ferret",
        "famille": "erddap",
        "mode_acces": "api",
        "frequence": "hourly",
        "criticite": "high",
        "is_active": True,
        "description": "Données haute fréquence COAST-HF Arcachon-Ferret via ERDDAP Ifremer",
        "metadata": {
            "base_url": "https://erddap.ifremer.fr/erddap",
            "dataset_id": "COAST-HF_Arcachon_Ferret",
            "variables": ["TEMP", "PSAL", "DOX2", "CHLA", "TURB"],
            "phase": "mvp"
        }
    },
    {
        "code": "erddap_somlit",
        "nom": "ERDDAP SOMLIT Arcachon",
        "famille": "erddap",
        "mode_acces": "api",
        "frequence": "6h",
        "criticite": "medium",
        "is_active": True,
        "description": "Suivi long terme SOMLIT Arcachon via ERDDAP Ifremer",
        "metadata": {
            "base_url": "https://erddap.ifremer.fr/erddap",
            "dataset_id": "SOMLIT_Arcachon",
            "variables": ["temperature", "salinity", "chlorophyll"],
            "phase": "mvp"
        }
    },
    {
        "code": "hubeau",
        "nom": "Hub'Eau Qualité Cours d'Eau",
        "famille": "hubeau",
        "mode_acces": "api",
        "frequence": "6h",
        "criticite": "medium",
        "is_active": True,
        "description": "API Qualité des Cours d'Eau Hub'Eau (Bassin d'Arcachon)",
        "metadata": {
            "base_url": "https://hubeau.eaufrance.fr/api/v2/qualite_rivieres",
            "bbox": [-1.30, 44.60, -1.15, 44.75],
            "max_results": 20000,
            "phase": "mvp"
        }
    },
    {
        "code": "seanoe",
        "nom": "SEANOE Historique",
        "famille": "seanoe",
        "mode_acces": "batch",
        "frequence": "daily",
        "criticite": "low",
        "is_active": False,
        "description": "Données historiques SEANOE (COAST-HF, SOMLIT) - batch manuel",
        "metadata": {
            "data_dir": "./data/seanoe",
            "source_type": "historical_reference",
            "phase": "mvp"
        }
    },
    {
        "code": "siba_enki",
        "nom": "SIBA Enki Exports",
        "famille": "siba",
        "mode_acces": "data_drop",
        "frequence": "2h",
        "criticite": "medium",
        "is_active": True,
        "description": "Exports SIBA Enki (qualité eau Bassin d'Arcachon) - data_drop semi-automatisé",
        "metadata": {
            "data_drop_dir": "./data_drop/siba",
            "processed_dir": "./data_drop/siba/processed",
            "phase": "mvp"
        }
    },
    
    # Phase 2 - Référentiels
    {
        "code": "shom_reference",
        "nom": "SHOM Reference (GeoNetwork)",
        "famille": "shom",
        "mode_acces": "api",
        "frequence": "12h",
        "criticite": "low",
        "is_active": True,
        "description": "Métadonnées et référentiels SHOM (Litto3D, bathymétrie, marée) via GeoNetwork",
        "metadata": {
            "base_url": "https://services.data.shom.fr/geonetwork/srv/api",
            "queries": ["Litto3D Nouvelle-Aquitaine", "Arcachon", "bathymetrie", "maree"],
            "max_records": 50,
            "phase": "reference"
        }
    },
    {
        "code": "insee_geo",
        "nom": "INSEE Geo (Référentiel Géographique)",
        "famille": "insee",
        "mode_acces": "api",
        "frequence": "daily",
        "criticite": "low",
        "is_active": True,
        "description": "Référentiel géographique administratif INSEE (départements, communes)",
        "metadata": {
            "base_url": "https://geo.api.gouv.fr",
            "departments": ["33", "17"],
            "phase": "reference"
        }
    },
    {
        "code": "insee_sirene",
        "nom": "INSEE Sirene (Établissements)",
        "famille": "insee",
        "mode_acces": "api",
        "frequence": "daily",
        "criticite": "low",
        "is_active": False,
        "description": "API Sirene INSEE (unités légales et établissements) - nécessite API key",
        "metadata": {
            "base_url": "https://api.insee.fr/api-sirene/3.11",
            "requires_api_key": True,
            "phase": "reference"
        }
    },
]


def create_sources_table_if_not_exists(cursor):
    """Crée la table sources si elle n'existe pas."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id SERIAL PRIMARY KEY,
            code VARCHAR(50) UNIQUE NOT NULL,
            nom VARCHAR(255) NOT NULL,
            famille VARCHAR(50),
            mode_acces VARCHAR(50),
            frequence VARCHAR(50),
            criticite VARCHAR(20),
            is_active BOOLEAN DEFAULT TRUE,
            description TEXT,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sources_code ON sources(code);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sources_famille ON sources(famille);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sources_active ON sources(is_active);
    """)
    
    cursor.execute("""
        COMMENT ON TABLE sources IS 'Sources de données Ocean Sentinel (Phase 1 MVP + Phase 2 Référentiels)';
    """)


def seed_sources():
    """Insère ou met à jour les sources."""
    print("=" * 80)
    print("SEED SOURCES - Ocean Sentinel V3.0")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Créer table si nécessaire
        print("\n📊 Vérification table sources...")
        create_sources_table_if_not_exists(cursor)
        conn.commit()
        print("✅ Table sources prête")
        
        # Insérer/mettre à jour sources
        print(f"\n📝 Insertion {len(SOURCES)} sources...")
        
        inserted = 0
        updated = 0
        
        for source in SOURCES:
            cursor.execute("""
                INSERT INTO sources (
                    code, nom, famille, mode_acces, frequence,
                    criticite, is_active, description, metadata
                ) VALUES (
                    %(code)s, %(nom)s, %(famille)s, %(mode_acces)s, %(frequence)s,
                    %(criticite)s, %(is_active)s, %(description)s, %(metadata)s::jsonb
                )
                ON CONFLICT (code) DO UPDATE SET
                    nom = EXCLUDED.nom,
                    famille = EXCLUDED.famille,
                    mode_acces = EXCLUDED.mode_acces,
                    frequence = EXCLUDED.frequence,
                    criticite = EXCLUDED.criticite,
                    is_active = EXCLUDED.is_active,
                    description = EXCLUDED.description,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
                RETURNING (xmax = 0) AS inserted;
            """, {
                **source,
                'metadata': psycopg2.extras.Json(source['metadata'])
            })
            
            result = cursor.fetchone()
            if result and result[0]:
                inserted += 1
                print(f"   ✅ Inserted: {source['code']}")
            else:
                updated += 1
                print(f"   🔄 Updated: {source['code']}")
        
        conn.commit()
        
        # Résumé
        print("\n" + "=" * 80)
        print(f"✅ SEED TERMINÉ")
        print(f"   Inserted: {inserted}")
        print(f"   Updated: {updated}")
        print(f"   Total: {len(SOURCES)}")
        print("=" * 80)
        
        # Afficher sources actives
        cursor.execute("""
            SELECT code, nom, famille, frequence, criticite
            FROM sources
            WHERE is_active = TRUE
            ORDER BY criticite DESC, famille, code;
        """)
        
        print("\n📋 Sources actives:")
        for row in cursor.fetchall():
            code, nom, famille, freq, crit = row
            print(f"   [{crit:8s}] {code:20s} ({famille:10s}) - {freq}")
        
        cursor.close()
        conn.close()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(seed_sources())
