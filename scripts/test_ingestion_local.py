#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ocean Sentinel V3.0 - Mission 3: Test d'Ingestion (Version Fichier Local)
==========================================================================
Test de validation avec fichier NetCDF local ou URL ERDDAP

Usage:
    python test_ingestion_local.py fichier.nc
    python test_ingestion_local.py --url "https://erddap.example.com/dataset.nc"

Auteur: Ocean Sentinel Team
Date: 2026-04-16
"""

import sys
import os
import gc
import logging
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_ingestion_local.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CHUNK_SIZE_TIME = 20000
MEMORY_LIMIT_MB = 256
MEMORY_WARNING_MB = 200


def get_memory_usage_mb():
    """Retourne l'utilisation mémoire en Mo."""
    try:
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    except ImportError:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def check_memory_limit():
    """Vérifie la mémoire et log."""
    mem_mb = get_memory_usage_mb()
    logger.info(f"💾 Mémoire: {mem_mb:.2f} Mo / {MEMORY_LIMIT_MB} Mo ({mem_mb/MEMORY_LIMIT_MB*100:.1f}%)")
    
    if mem_mb > MEMORY_LIMIT_MB:
        raise MemoryError(f"Limite dépassée: {mem_mb:.1f} Mo")
    if mem_mb > MEMORY_WARNING_MB:
        logger.warning(f"⚠️  Mémoire élevée: {mem_mb:.1f} Mo")
    
    return mem_mb


def force_garbage_collection():
    """Force le garbage collection."""
    mem_before = get_memory_usage_mb()
    gc.collect()
    mem_after = get_memory_usage_mb()
    freed = mem_before - mem_after
    if freed > 0:
        logger.info(f"🧹 GC: {freed:.2f} Mo libérés")
    return mem_after


def test_ingestion(filepath_or_url):
    """Test d'ingestion principal."""
    logger.info("=" * 80)
    logger.info("🌊 MISSION 3: TEST D'INGESTION COAST-HF")
    logger.info("=" * 80)
    logger.info(f"Source: {filepath_or_url}")
    logger.info("")
    
    mem_initial = check_memory_limit()
    logger.info("")
    
    try:
        import xarray as xr
        
        logger.info("═══ ÉTAPE 1: Ouverture Dataset (Lazy Loading) ═══")
        
        # Ouverture avec chunking
        ds = xr.open_dataset(
            filepath_or_url,
            chunks={'time': CHUNK_SIZE_TIME} if 'time' in xr.open_dataset(filepath_or_url, decode_times=False).dims else None,
            decode_times=True
        )
        
        logger.info("✓ Dataset ouvert")
        logger.info(f"   Dimensions: {dict(ds.dims)}")
        logger.info(f"   Variables: {list(ds.data_vars)[:10]}")
        logger.info("")
        
        mem_after_open = check_memory_limit()
        logger.info(f"   Mémoire lazy: +{mem_after_open - mem_initial:.2f} Mo")
        logger.info("")
        
        # Inspection
        logger.info("═══ ÉTAPE 2: Inspection ═══")
        if 'time' in ds.coords:
            logger.info(f"⏰ Période: {pd.Timestamp(ds.time.values[0])} → {pd.Timestamp(ds.time.values[-1])}")
            logger.info(f"   Points: {len(ds.time):,}")
        logger.info("")
        
        # Extraction par chunks
        logger.info("═══ ÉTAPE 3: Extraction par Chunks ═══")
        
        # Identifier les variables de température et salinité
        temp_vars = [v for v in ds.data_vars if 'TEMP' in v.upper() and 'QC' not in v.upper()]
        psal_vars = [v for v in ds.data_vars if 'PSAL' in v.upper() and 'QC' not in v.upper()]
        
        if temp_vars:
            logger.info(f"   TEMP trouvé: {temp_vars[0]}")
        if psal_vars:
            logger.info(f"   PSAL trouvé: {psal_vars[0]}")
        
        if not temp_vars and not psal_vars:
            logger.warning("   Aucune variable TEMP/PSAL standard détectée")
            logger.info(f"   Variables disponibles: {list(ds.data_vars)[:20]}")
        
        logger.info("")
        
        # Traitement par chunks
        if 'time' in ds.dims:
            n_chunks = int(np.ceil(len(ds.time) / CHUNK_SIZE_TIME))
            logger.info(f"   Chunks à traiter: {n_chunks}")
            logger.info("")
            
            total_points = 0
            
            for i in range(min(n_chunks, 3)):  # Limiter à 3 chunks pour le test
                start_idx = i * CHUNK_SIZE_TIME
                end_idx = min((i + 1) * CHUNK_SIZE_TIME, len(ds.time))
                
                logger.info(f"   📦 Chunk {i+1}/{n_chunks} ({start_idx}-{end_idx})...")
                
                mem_before = check_memory_limit()
                
                # Chargement chunk
                ds_chunk = ds.isel(time=slice(start_idx, end_idx))
                
                # Extraction données
                if temp_vars:
                    temp_data = ds_chunk[temp_vars[0]].values
                    logger.info(f"      TEMP: {np.nanmin(temp_data):.2f} - {np.nanmax(temp_data):.2f}°C")
                
                if psal_vars:
                    psal_data = ds_chunk[psal_vars[0]].values
                    logger.info(f"      PSAL: {np.nanmin(psal_data):.2f} - {np.nanmax(psal_data):.2f} PSU")
                
                total_points += (end_idx - start_idx)
                
                mem_after = check_memory_limit()
                logger.info(f"      Mémoire chunk: +{mem_after - mem_before:.2f} Mo")
                
                force_garbage_collection()
                logger.info("")
        
        ds.close()
        logger.info("✓ Dataset fermé")
        logger.info("")
        
        # Validation finale
        force_garbage_collection()
        mem_final = check_memory_limit()
        
        logger.info("═══ ÉTAPE 4: Validation Mémoire ═══")
        logger.info(f"   Initiale: {mem_initial:.2f} Mo")
        logger.info(f"   Finale: {mem_final:.2f} Mo")
        logger.info(f"   Max observé: {max(mem_initial, mem_final):.2f} Mo")
        logger.info(f"   Limite: {MEMORY_LIMIT_MB} Mo")
        logger.info("")
        
        if max(mem_initial, mem_final) < MEMORY_LIMIT_MB:
            logger.info("✅ CONTRAINTE MÉMOIRE RESPECTÉE")
        else:
            logger.error("❌ CONTRAINTE MÉMOIRE VIOLÉE")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("🎉 MISSION 3 RÉUSSIE")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERREUR: {e}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    parser = argparse.ArgumentParser(description='Test d\'ingestion Ocean Sentinel')
    parser.add_argument('filepath', nargs='?', help='Chemin vers fichier NetCDF')
    parser.add_argument('--url', help='URL ERDDAP')
    
    args = parser.parse_args()
    
    if args.url:
        source = args.url
    elif args.filepath:
        source = args.filepath
        if not Path(source).exists():
            logger.error(f"❌ Fichier introuvable: {source}")
            return False
    else:
        logger.error("❌ Usage: python test_ingestion_local.py fichier.nc")
        logger.error("   ou: python test_ingestion_local.py --url URL")
        return False
    
    return test_ingestion(source)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
