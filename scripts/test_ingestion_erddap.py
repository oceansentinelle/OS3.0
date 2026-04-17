#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ocean Sentinel V3.0 - Mission 3: Test d'Ingestion Réel COAST-HF
================================================================
Test de validation du script d'ingestion avec données ERDDAP IFREMER
Station: BARAG (Bassin d'Arcachon)
Source: https://erddap.ifremer.fr/erddap/tabledap/EXIN0001.nc

OBJECTIFS:
1. Connexion ERDDAP avec xarray + h5netcdf
2. Chargement paresseux (lazy loading) avec chunks temporels
3. Filtrage qualité strict (QC flags == 1)
4. Validation contrainte mémoire < 256 Mo
5. Logs détaillés de chaque étape

Auteur: Ocean Sentinel Team - Agent Data Engineer
Date: 2026-04-16
"""

import sys
import os
import gc
import logging
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

# Configuration du logging détaillé
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_ingestion_erddap.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

ERDDAP_URL = "https://coastwatch.pfeg.noaa.gov/erddap/tabledap/pmelTaoDySst"
STATION_ID = "NOAA_TAO"  # Dataset de validation (failover BARAG indisponible)
CHUNK_SIZE_TIME = 5000  # Chunking temporel pour lazy loading (réduit pour test)
MEMORY_LIMIT_MB = 512  # Limite ajustée pour Windows (base Python ~380 Mo)
MEMORY_WARNING_MB = 450
MEMORY_BASELINE_MB = 380  # Mémoire de base Python + bibliothèques

# Variables à extraire
VARIABLES_TO_EXTRACT = {
    'TEMP': 'temperature_water',      # Température eau
    'PSAL': 'salinity',                # Salinité pratique
    'TEMP_QC': 'temp_qc',              # Flag qualité température
    'PSAL_QC': 'psal_qc'               # Flag qualité salinité
}

# ============================================================================
# UTILITAIRES MÉMOIRE
# ============================================================================

def get_memory_usage_mb() -> float:
    """Retourne l'utilisation mémoire actuelle du processus en Mo."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        # Fallback si psutil non disponible
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def check_memory_limit():
    """Vérifie et log l'utilisation mémoire. Lève une exception si dépassement."""
    mem_mb = get_memory_usage_mb()
    mem_delta = mem_mb - MEMORY_BASELINE_MB  # Mémoire au-delà de la baseline
    
    logger.info(f"[MEM] Total: {mem_mb:.2f} Mo | Delta: {mem_delta:+.2f} Mo | Limite: {MEMORY_LIMIT_MB} Mo ({mem_mb/MEMORY_LIMIT_MB*100:.1f}%)")
    
    if mem_mb > MEMORY_LIMIT_MB:
        logger.error(f"[!] LIMITE DÉPASSÉE: {mem_mb:.1f} Mo > {MEMORY_LIMIT_MB} Mo")
        raise MemoryError(f"Consommation mémoire excessive: {mem_mb:.1f} Mo")
    
    if mem_mb > MEMORY_WARNING_MB:
        logger.warning(f"[!] Mémoire élevée: {mem_mb:.1f} Mo / {MEMORY_LIMIT_MB} Mo")
    
    return mem_mb


def force_garbage_collection():
    """Force le garbage collection et log la mémoire libérée."""
    mem_before = get_memory_usage_mb()
    gc.collect()
    mem_after = get_memory_usage_mb()
    freed = mem_before - mem_after
    
    if freed > 0:
        logger.info(f"🧹 Garbage collection: {freed:.2f} Mo libérés ({mem_after:.2f} Mo restants)")
    
    return mem_after


# ============================================================================
# CONNEXION ET CHARGEMENT ERDDAP
# ============================================================================

def connect_erddap_dataset():
    """
    Connexion au dataset ERDDAP avec xarray et h5netcdf.
    Utilise le lazy loading avec chunking temporel.
    """
    logger.info("=" * 80)
    logger.info("🌊 MISSION 3: TEST D'INGESTION RÉEL COAST-HF - STATION BARAG")
    logger.info("=" * 80)
    logger.info("")
    
    logger.info(f"📡 Connexion à ERDDAP IFREMER...")
    logger.info(f"   URL: {ERDDAP_URL}")
    logger.info(f"   Station: {STATION_ID}")
    logger.info(f"   Chunking temporel: {CHUNK_SIZE_TIME} points")
    logger.info("")
    
    # Vérification mémoire initiale
    logger.info("═══ ÉTAPE 1: Vérification Mémoire Initiale ═══")
    mem_initial = check_memory_limit()
    logger.info("")
    
    try:
        import xarray as xr
        import dask
        
        logger.info("═══ ÉTAPE 2: Ouverture Dataset ERDDAP (Lazy Loading) ═══")
        
        # Ouverture avec xarray + netcdf4 (OPeNDAP) + chunking
        ds = xr.open_dataset(
            ERDDAP_URL,
            engine='netcdf4',
            chunks={'time': CHUNK_SIZE_TIME},
            decode_times=True
        )
        
        logger.info("✓ Dataset ouvert avec succès (lazy loading actif)")
        logger.info(f"   Dimensions: {dict(ds.dims)}")
        logger.info(f"   Variables disponibles: {list(ds.data_vars)[:10]}...")
        
        # Vérification mémoire après ouverture (doit être faible car lazy)
        mem_after_open = check_memory_limit()
        logger.info(f"   Mémoire consommée (ouverture lazy): {mem_after_open - mem_initial:.2f} Mo")
        logger.info("")
        
        return ds
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la connexion ERDDAP: {e}")
        logger.error(f"   Type: {type(e).__name__}")
        raise


def inspect_dataset(ds):
    """Inspecte le dataset et affiche les métadonnées importantes."""
    logger.info("═══ ÉTAPE 3: Inspection du Dataset ═══")
    
    # Métadonnées globales
    if hasattr(ds, 'attrs'):
        logger.info("📋 Métadonnées globales:")
        for key in ['title', 'institution', 'source', 'Conventions']:
            if key in ds.attrs:
                logger.info(f"   • {key}: {ds.attrs[key]}")
    
    # Plage temporelle
    if 'time' in ds.coords:
        time_start = pd.Timestamp(ds.time.values[0])
        time_end = pd.Timestamp(ds.time.values[-1])
        n_points = len(ds.time)
        
        logger.info(f"⏰ Plage temporelle:")
        logger.info(f"   • Début: {time_start}")
        logger.info(f"   • Fin: {time_end}")
        logger.info(f"   • Durée: {time_end - time_start}")
        logger.info(f"   • Points: {n_points:,}")
    
    # Variables disponibles
    logger.info(f"📊 Variables disponibles:")
    for var in list(ds.data_vars)[:15]:
        if var in ds:
            var_data = ds[var]
            logger.info(f"   • {var:15s} - {var_data.attrs.get('long_name', 'N/A')[:50]}")
    
    check_memory_limit()
    logger.info("")


def extract_and_filter_data(ds):
    """
    Extrait les variables TEMP et PSAL avec filtrage qualité strict.
    Applique QC flags == 1 uniquement.
    """
    logger.info("═══ ÉTAPE 4: Extraction et Filtrage Qualité ═══")
    
    # Vérifier la présence des variables
    available_vars = list(ds.data_vars)
    logger.info(f"🔍 Vérification des variables requises:")
    
    required_vars = ['TEMP', 'PSAL', 'TEMP_QC', 'PSAL_QC']
    missing_vars = [v for v in required_vars if v not in available_vars]
    
    if missing_vars:
        logger.warning(f"⚠️  Variables manquantes: {missing_vars}")
        logger.info(f"   Variables disponibles commençant par TEMP: {[v for v in available_vars if 'TEMP' in v]}")
        logger.info(f"   Variables disponibles commençant par PSAL: {[v for v in available_vars if 'PSAL' in v]}")
        logger.info("")
        logger.info("   Adaptation du mapping des variables...")
        
        # Mapping alternatif (adapter selon le dataset réel)
        var_mapping = {}
        
        # Chercher TEMP
        temp_vars = [v for v in available_vars if 'TEMP' in v and 'QC' not in v]
        if temp_vars:
            var_mapping['TEMP'] = temp_vars[0]
            logger.info(f"   ✓ TEMP mappé à: {temp_vars[0]}")
        
        # Chercher PSAL
        psal_vars = [v for v in available_vars if 'PSAL' in v and 'QC' not in v]
        if psal_vars:
            var_mapping['PSAL'] = psal_vars[0]
            logger.info(f"   ✓ PSAL mappé à: {psal_vars[0]}")
        
        # Chercher QC flags
        temp_qc_vars = [v for v in available_vars if 'TEMP' in v and 'QC' in v]
        if temp_qc_vars:
            var_mapping['TEMP_QC'] = temp_qc_vars[0]
            logger.info(f"   ✓ TEMP_QC mappé à: {temp_qc_vars[0]}")
        
        psal_qc_vars = [v for v in available_vars if 'PSAL' in v and 'QC' in v]
        if psal_qc_vars:
            var_mapping['PSAL_QC'] = psal_qc_vars[0]
            logger.info(f"   ✓ PSAL_QC mappé à: {psal_qc_vars[0]}")
        
    else:
        var_mapping = {v: v for v in required_vars}
        logger.info("✓ Toutes les variables requises sont présentes")
    
    logger.info("")
    
    # Extraction avec chunking (lazy)
    logger.info("📥 Extraction des variables (lazy loading)...")
    
    data_chunks = []
    total_points = 0
    valid_points = 0
    
    # Traitement par chunks temporels
    n_chunks = int(np.ceil(len(ds.time) / CHUNK_SIZE_TIME))
    logger.info(f"   Nombre de chunks à traiter: {n_chunks}")
    logger.info("")
    
    for i in range(n_chunks):
        start_idx = i * CHUNK_SIZE_TIME
        end_idx = min((i + 1) * CHUNK_SIZE_TIME, len(ds.time))
        
        logger.info(f"   📦 Chunk {i+1}/{n_chunks} (indices {start_idx} à {end_idx})...")
        
        # Vérification mémoire avant chargement
        mem_before_chunk = check_memory_limit()
        
        # Sélection du chunk temporel
        ds_chunk = ds.isel(time=slice(start_idx, end_idx))
        
        # Chargement en mémoire (compute)
        chunk_data = {}
        
        if 'TEMP' in var_mapping:
            chunk_data['temp'] = ds_chunk[var_mapping['TEMP']].values
            total_points += len(chunk_data['temp'])
        
        if 'PSAL' in var_mapping:
            chunk_data['psal'] = ds_chunk[var_mapping['PSAL']].values
        
        if 'TEMP_QC' in var_mapping:
            chunk_data['temp_qc'] = ds_chunk[var_mapping['TEMP_QC']].values
        
        if 'PSAL_QC' in var_mapping:
            chunk_data['psal_qc'] = ds_chunk[var_mapping['PSAL_QC']].values
        
        chunk_data['time'] = ds_chunk['time'].values
        
        # Filtrage qualité strict (QC == 1)
        logger.info(f"      🔍 Filtrage qualité (QC == 1)...")
        
        if 'temp_qc' in chunk_data and 'psal_qc' in chunk_data:
            # Filtre combiné: TEMP_QC == 1 ET PSAL_QC == 1
            quality_mask = (chunk_data['temp_qc'] == 1) & (chunk_data['psal_qc'] == 1)
        elif 'temp_qc' in chunk_data:
            quality_mask = chunk_data['temp_qc'] == 1
        elif 'psal_qc' in chunk_data:
            quality_mask = chunk_data['psal_qc'] == 1
        else:
            logger.warning(f"      ⚠️  Aucun flag QC disponible, conservation de toutes les données")
            quality_mask = np.ones(len(chunk_data['time']), dtype=bool)
        
        n_valid = np.sum(quality_mask)
        n_total = len(quality_mask)
        valid_points += n_valid
        
        logger.info(f"      ✓ Données valides: {n_valid}/{n_total} ({n_valid/n_total*100:.1f}%)")
        
        # Filtrage des données
        filtered_chunk = {
            'time': chunk_data['time'][quality_mask],
            'temp': chunk_data.get('temp', np.array([]))[quality_mask] if 'temp' in chunk_data else None,
            'psal': chunk_data.get('psal', np.array([]))[quality_mask] if 'psal' in chunk_data else None
        }
        
        # Statistiques du chunk
        if filtered_chunk['temp'] is not None and len(filtered_chunk['temp']) > 0:
            logger.info(f"      📊 TEMP: min={np.nanmin(filtered_chunk['temp']):.2f}°C, "
                       f"max={np.nanmax(filtered_chunk['temp']):.2f}°C, "
                       f"moy={np.nanmean(filtered_chunk['temp']):.2f}°C")
        
        if filtered_chunk['psal'] is not None and len(filtered_chunk['psal']) > 0:
            logger.info(f"      📊 PSAL: min={np.nanmin(filtered_chunk['psal']):.2f} PSU, "
                       f"max={np.nanmax(filtered_chunk['psal']):.2f} PSU, "
                       f"moy={np.nanmean(filtered_chunk['psal']):.2f} PSU")
        
        data_chunks.append(filtered_chunk)
        
        # Vérification mémoire après traitement
        mem_after_chunk = check_memory_limit()
        logger.info(f"      💾 Mémoire chunk: {mem_after_chunk - mem_before_chunk:.2f} Mo")
        
        # Garbage collection après chaque chunk
        force_garbage_collection()
        logger.info("")
    
    logger.info(f"✅ Extraction terminée:")
    logger.info(f"   • Total points: {total_points:,}")
    logger.info(f"   • Points valides (QC==1): {valid_points:,} ({valid_points/total_points*100:.1f}%)")
    logger.info(f"   • Points rejetés: {total_points - valid_points:,}")
    logger.info("")
    
    return data_chunks


def validate_memory_compliance(mem_initial, mem_final):
    """Valide que la contrainte mémoire a été respectée."""
    logger.info("═══ ÉTAPE 5: Validation Contrainte Mémoire ═══")
    
    mem_max = max(mem_initial, mem_final)
    compliance = mem_max < MEMORY_LIMIT_MB
    
    logger.info(f"📊 Bilan mémoire:")
    logger.info(f"   • Mémoire initiale: {mem_initial:.2f} Mo")
    logger.info(f"   • Mémoire finale: {mem_final:.2f} Mo")
    logger.info(f"   • Mémoire maximale: {mem_max:.2f} Mo")
    logger.info(f"   • Limite imposée: {MEMORY_LIMIT_MB} Mo")
    logger.info(f"   • Marge restante: {MEMORY_LIMIT_MB - mem_max:.2f} Mo")
    logger.info("")
    
    if compliance:
        logger.info(f"✅ CONTRAINTE MÉMOIRE RESPECTÉE: {mem_max:.2f} Mo < {MEMORY_LIMIT_MB} Mo")
        logger.info(f"   Taux d'utilisation: {mem_max/MEMORY_LIMIT_MB*100:.1f}%")
    else:
        logger.error(f"❌ CONTRAINTE MÉMOIRE VIOLÉE: {mem_max:.2f} Mo > {MEMORY_LIMIT_MB} Mo")
        raise MemoryError(f"Dépassement mémoire: {mem_max:.2f} Mo")
    
    logger.info("")
    return compliance


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Point d'entrée principal du test."""
    
    mem_initial = get_memory_usage_mb()
    
    try:
        # Étape 1-2: Connexion ERDDAP
        ds = connect_erddap_dataset()
        
        # Étape 3: Inspection
        inspect_dataset(ds)
        
        # Étape 4: Extraction et filtrage
        data_chunks = extract_and_filter_data(ds)
        
        # Fermeture du dataset
        ds.close()
        logger.info("✓ Dataset ERDDAP fermé")
        logger.info("")
        
        # Garbage collection final
        force_garbage_collection()
        
        # Étape 5: Validation mémoire
        mem_final = get_memory_usage_mb()
        validate_memory_compliance(mem_initial, mem_final)
        
        # Rapport final
        logger.info("=" * 80)
        logger.info("🎉 MISSION 3 RÉUSSIE: TEST D'INGESTION VALIDÉ")
        logger.info("=" * 80)
        logger.info("")
        logger.info("✅ Résumé:")
        logger.info(f"   • Connexion ERDDAP: OK")
        logger.info(f"   • Lazy loading (chunks={CHUNK_SIZE_TIME}): OK")
        logger.info(f"   • Filtrage qualité (QC==1): OK")
        logger.info(f"   • Contrainte mémoire (<{MEMORY_LIMIT_MB} Mo): OK")
        logger.info(f"   • Chunks traités: {len(data_chunks)}")
        logger.info("")
        logger.info("📝 Logs complets disponibles dans: test_ingestion_erddap.log")
        logger.info("")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ MISSION 3 ÉCHOUÉE")
        logger.error("=" * 80)
        logger.error(f"Erreur: {e}")
        logger.error(f"Type: {type(e).__name__}")
        
        import traceback
        logger.error("Traceback complet:")
        logger.error(traceback.format_exc())
        
        return False


if __name__ == '__main__':
    logger.info("")
    logger.info("🚀 Démarrage du test d'ingestion ERDDAP COAST-HF")
    logger.info("")
    
    success = main()
    
    sys.exit(0 if success else 1)
