#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ocean Sentinel V3.0 - Agent Data Engineer
==========================================
Script d'ingestion streaming pour données océanographiques volumineuses.

CONTRAINTE CRITIQUE: Consommation mémoire MAX 256 Mo
Architecture: Lecture par morceaux (chunked) pour fichiers NetCDF, GRIB2, CSV

Formats supportés:
- NetCDF (xarray avec dask)
- GRIB2 (pygrib avec lecture séquentielle)
- CSV SEANOE (pandas chunks)

Auteur: Ocean Sentinel Team - Agent Data Engineer
Date: 2026-04-16
Licence: Projet ILICO - Infrastructure de Recherche
"""

import sys
import os
import gc
import logging
import time
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Generator, Dict, Any, Optional, List, Tuple
import psycopg2
from psycopg2.extras import execute_batch
from psycopg2 import sql
import numpy as np

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion_stream.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

# Taille des chunks pour limiter la mémoire (ajustable selon les besoins)
CHUNK_SIZE_CSV = 5000  # Lignes par chunk pour CSV
CHUNK_SIZE_NETCDF = 1000  # Points temporels par chunk pour NetCDF
CHUNK_SIZE_ERDDAP = 5000  # Points temporels par chunk pour ERDDAP OPeNDAP
BATCH_SIZE_DB = 500  # Insertions par batch PostgreSQL

# Seuils de mémoire (en Mo)
MEMORY_LIMIT_MB = 256
MEMORY_WARNING_MB = 200

# Configuration base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '6543')),
    'database': os.getenv('DB_NAME', 'oceansentinelle'),
    'user': os.getenv('DB_USER', 'oceansentinel_writer'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# Configuration sources de données (Failover)
DATA_SOURCES = {
    'primary': {
        'type': 'erddap',
        'url': 'https://erddap.ifremer.fr/erddap/tabledap/EXIN0001',
        'station_id': 'BARAG',
        'timeout': 30,
    },
    'fallback': {
        'type': 'erddap',
        'url': 'https://coastwatch.pfeg.noaa.gov/erddap/tabledap/pmelTaoDySst',
        'station_id': 'NOAA_TAO',
        'timeout': 30,
    },
    'seanoe': {
        'type': 'static',
        'doi': '10.17882/100119',
        'base_url': 'https://www.seanoe.org/data/00811/92312/',
        'station_id': 'BARAG_ARCHIVE',
    }
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
    
    if mem_mb > MEMORY_LIMIT_MB:
        logger.error(f"⚠️ LIMITE MÉMOIRE DÉPASSÉE: {mem_mb:.1f} Mo > {MEMORY_LIMIT_MB} Mo")
        raise MemoryError(f"Consommation mémoire excessive: {mem_mb:.1f} Mo")
    
    if mem_mb > MEMORY_WARNING_MB:
        logger.warning(f"⚠️ Mémoire élevée: {mem_mb:.1f} Mo / {MEMORY_LIMIT_MB} Mo")
    
    return mem_mb


def force_garbage_collection():
    """Force le garbage collection et log la mémoire libérée."""
    mem_before = get_memory_usage_mb()
    gc.collect()
    mem_after = get_memory_usage_mb()
    freed = mem_before - mem_after
    
    if freed > 10:
        logger.info(f"[GC] {freed:.1f} Mo libérés ({mem_after:.1f} Mo restants)")


# ============================================================================
# FAILOVER MULTI-SOURCES (Mission 4)
# ============================================================================

def test_erddap_connection(url: str, timeout: int = 30) -> bool:
    """Teste la disponibilité d'un serveur ERDDAP."""
    try:
        logger.info(f"[FAILOVER] Test connexion: {url}")
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            logger.info(f"[FAILOVER] Serveur disponible (HTTP {response.status_code})")
            return True
        else:
            logger.warning(f"[FAILOVER] Serveur indisponible (HTTP {response.status_code})")
            return False
    except requests.exceptions.Timeout:
        logger.warning(f"[FAILOVER] Timeout après {timeout}s")
        return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"[FAILOVER] Erreur connexion: {e}")
        return False


def get_active_data_source() -> Tuple[str, Dict[str, Any]]:
    """
    Détermine la source de données active avec mécanisme de failover.
    
    Returns:
        Tuple (source_name, source_config)
    """
    logger.info("="*80)
    logger.info("[FAILOVER] Détection source de données active")
    logger.info("="*80)
    
    # Test source primaire
    primary = DATA_SOURCES['primary']
    if primary['type'] == 'erddap':
        if test_erddap_connection(primary['url'], primary['timeout']):
            logger.info(f"[FAILOVER] Source primaire active: {primary['url']}")
            return 'primary', primary
    
    # Fallback sur source secondaire
    logger.warning("[FAILOVER] Source primaire indisponible, bascule sur fallback")
    fallback = DATA_SOURCES['fallback']
    if fallback['type'] == 'erddap':
        if test_erddap_connection(fallback['url'], fallback['timeout']):
            logger.info(f"[FAILOVER] Source fallback active: {fallback['url']}")
            return 'fallback', fallback
    
    # Dernière option: archives SEANOE
    logger.warning("[FAILOVER] ERDDAP indisponible, utilisation archives SEANOE")
    seanoe = DATA_SOURCES['seanoe']
    logger.info(f"[FAILOVER] Source SEANOE: DOI {seanoe['doi']}")
    return 'seanoe', seanoe


def stream_erddap_chunks(url: str, station_id: str, chunk_size: int = CHUNK_SIZE_ERDDAP) -> Generator[Dict[str, Any], None, None]:
    """
    Lit un dataset ERDDAP via OPeNDAP avec chunking temporel.
    
    Args:
        url: URL ERDDAP (sans extension)
        station_id: Identifiant de la station
        chunk_size: Nombre de points temporels par chunk
        
    Yields:
        Dict contenant les données du chunk avec métadonnées
    """
    try:
        import xarray as xr
        import pandas as pd
    except ImportError:
        logger.error("xarray requis. Installation: pip install xarray netCDF4")
        raise
    
    logger.info(f"[ERDDAP] Connexion OPeNDAP: {url}")
    logger.info(f"[ERDDAP] Chunk size: {chunk_size} points")
    
    try:
        # Ouverture avec lazy loading (backend netcdf4 pour OPeNDAP)
        ds = xr.open_dataset(
            url,
            engine='netcdf4',
            chunks={'time': chunk_size} if 'time' in xr.open_dataset(url, engine='netcdf4', decode_times=False).dims else None,
            decode_times=True
        )
        
        logger.info(f"[ERDDAP] Dataset ouvert (lazy loading actif)")
        logger.info(f"[ERDDAP] Dimensions: {dict(ds.dims)}")
        logger.info(f"[ERDDAP] Variables: {list(ds.data_vars)[:10]}")
        
        # Identifier les variables de température et salinité
        temp_vars = [v for v in ds.data_vars if 'TEMP' in v.upper() or 'T_' in v.upper()]
        psal_vars = [v for v in ds.data_vars if 'PSAL' in v.upper() or 'SAL' in v.upper() or 'S_' in v.upper()]
        temp_qc_vars = [v for v in ds.data_vars if 'QC' in v.upper() and 'TEMP' in v.upper()]
        psal_qc_vars = [v for v in ds.data_vars if 'QC' in v.upper() and 'PSAL' in v.upper()]
        
        temp_var = temp_vars[0] if temp_vars else None
        psal_var = psal_vars[0] if psal_vars else None
        temp_qc_var = temp_qc_vars[0] if temp_qc_vars else None
        psal_qc_var = psal_qc_vars[0] if psal_qc_vars else None
        
        logger.info(f"[ERDDAP] Mapping variables: TEMP={temp_var}, PSAL={psal_var}")
        
        # Déterminer la dimension temporelle
        time_dim = None
        for dim in ds.dims:
            if 'time' in dim.lower():
                time_dim = dim
                break
        
        if not time_dim:
            logger.warning("[ERDDAP] Aucune dimension temporelle trouvée")
            ds.close()
            return
        
        total_times = len(ds[time_dim])
        logger.info(f"[ERDDAP] Dimension temps: {total_times} points")
        
        chunk_count = 0
        total_processed = 0
        
        # Itération par chunks temporels
        for i in range(0, total_times, chunk_size):
            chunk_count += 1
            end_idx = min(i + chunk_size, total_times)
            
            logger.info(f"[ERDDAP] Chunk {chunk_count}: indices {i}-{end_idx}")
            
            # Vérification mémoire avant chargement
            mem_before = check_memory_limit()
            
            # Sélection et chargement du chunk
            chunk_ds = ds.isel({time_dim: slice(i, end_idx)})
            
            # Extraction des données
            records = []
            for t_idx in range(len(chunk_ds[time_dim])):
                try:
                    time_val = chunk_ds[time_dim].values[t_idx]
                    
                    # Extraction température
                    temp = None
                    temp_qc = None
                    if temp_var:
                        temp_data = chunk_ds[temp_var].values
                        if temp_data.ndim > 1:
                            temp = float(temp_data[t_idx, 0]) if temp_data.shape[1] > 0 else None
                        else:
                            temp = float(temp_data[t_idx])
                    
                    if temp_qc_var:
                        temp_qc_data = chunk_ds[temp_qc_var].values
                        if temp_qc_data.ndim > 1:
                            temp_qc = int(temp_qc_data[t_idx, 0]) if temp_qc_data.shape[1] > 0 else 0
                        else:
                            temp_qc = int(temp_qc_data[t_idx])
                    
                    # Extraction salinité
                    psal = None
                    psal_qc = None
                    if psal_var:
                        psal_data = chunk_ds[psal_var].values
                        if psal_data.ndim > 1:
                            psal = float(psal_data[t_idx, 0]) if psal_data.shape[1] > 0 else None
                        else:
                            psal = float(psal_data[t_idx])
                    
                    if psal_qc_var:
                        psal_qc_data = chunk_ds[psal_qc_var].values
                        if psal_qc_data.ndim > 1:
                            psal_qc = int(psal_qc_data[t_idx, 0]) if psal_qc_data.shape[1] > 0 else 0
                        else:
                            psal_qc = int(psal_qc_data[t_idx])
                    
                    # Filtrage qualité strict (QC == 1)
                    quality_ok = True
                    if temp_qc is not None and temp_qc != 1:
                        quality_ok = False
                    if psal_qc is not None and psal_qc != 1:
                        quality_ok = False
                    
                    if not quality_ok:
                        continue  # Skip données de mauvaise qualité
                    
                    record = {
                        'time': pd.Timestamp(time_val).to_pydatetime(),
                        'station_id': station_id,
                        'temperature_water': temp if temp and not np.isnan(temp) else None,
                        'salinity': psal if psal and not np.isnan(psal) else None,
                        'quality_flag': 1,  # Données validées
                        'data_source': f"ERDDAP:{url}",
                    }
                    
                    records.append(record)
                    
                except Exception as e:
                    logger.debug(f"[ERDDAP] Erreur extraction point {t_idx}: {e}")
                    continue
            
            total_processed += len(records)
            mem_after = check_memory_limit()
            
            logger.info(f"[ERDDAP] Chunk {chunk_count}: {len(records)} records valides (QC==1)")
            logger.info(f"[ERDDAP] Mémoire: {mem_after:.1f} Mo (delta: +{mem_after - mem_before:.1f} Mo)")
            
            yield {
                'records': records,
                'chunk_number': chunk_count,
                'chunk_size': len(records),
                'total_processed': total_processed,
                'memory_mb': mem_after,
                'source_url': url,
                'format': 'ERDDAP_OPeNDAP'
            }
            
            # Nettoyage
            del chunk_ds, records
            force_garbage_collection()
        
        ds.close()
        logger.info(f"[ERDDAP] Terminé: {total_processed} points valides en {chunk_count} chunks")
        
    except Exception as e:
        logger.error(f"[ERDDAP] Erreur: {e}")
        raise


# ============================================================================
# LECTEUR CSV STREAMING (SEANOE)
# ============================================================================

def stream_csv_chunks(filepath: Path, chunk_size: int = CHUNK_SIZE_CSV) -> Generator[Dict[str, Any], None, None]:
    """
    Lit un fichier CSV par morceaux pour limiter la mémoire.
    
    Args:
        filepath: Chemin vers le fichier CSV
        chunk_size: Nombre de lignes par chunk
        
    Yields:
        Dict contenant les données du chunk avec métadonnées
    """
    try:
        import pandas as pd
    except ImportError:
        logger.error("pandas requis pour CSV. Installation: pip install pandas")
        raise
    
    logger.info(f"📄 Lecture CSV streaming: {filepath.name}")
    logger.info(f"   Chunk size: {chunk_size} lignes")
    
    total_rows = 0
    chunk_count = 0
    
    # Lecture par chunks
    for chunk_df in pd.read_csv(filepath, chunksize=chunk_size, parse_dates=['time']):
        chunk_count += 1
        total_rows += len(chunk_df)
        
        # Vérification mémoire
        mem_mb = check_memory_limit()
        
        # Conversion en format standardisé
        records = []
        for _, row in chunk_df.iterrows():
            record = {
                'time': row.get('time'),
                'station_id': row.get('station_id', 'UNKNOWN'),
                'temperature_air': float(row['temperature_air']) if pd.notna(row.get('temperature_air')) else None,
                'humidity': float(row['humidity']) if pd.notna(row.get('humidity')) else None,
                'pressure': float(row['pressure']) if pd.notna(row.get('pressure')) else None,
                'wind_speed': float(row['wind_speed']) if pd.notna(row.get('wind_speed')) else None,
                'wind_direction': float(row['wind_direction']) if pd.notna(row.get('wind_direction')) else None,
                'precipitation': float(row['precipitation']) if pd.notna(row.get('precipitation')) else None,
                'temperature_water': float(row['temperature_water']) if pd.notna(row.get('temperature_water')) else None,
                'salinity': float(row['salinity']) if pd.notna(row.get('salinity')) else None,
                'ph': float(row['ph']) if pd.notna(row.get('ph')) else None,
                'dissolved_oxygen': float(row['dissolved_oxygen']) if pd.notna(row.get('dissolved_oxygen')) else None,
                'turbidity': float(row['turbidity']) if pd.notna(row.get('turbidity')) else None,
                'quality_flag': int(row.get('quality_flag', 0)),
                'data_source': f"SEANOE_CSV:{filepath.name}",
            }
            records.append(record)
        
        yield {
            'records': records,
            'chunk_number': chunk_count,
            'chunk_size': len(records),
            'total_processed': total_rows,
            'memory_mb': mem_mb,
            'source_file': str(filepath),
            'format': 'CSV'
        }
        
        # Nettoyage explicite
        del chunk_df, records
        force_garbage_collection()
    
    logger.info(f"✓ CSV terminé: {total_rows} lignes en {chunk_count} chunks")


# ============================================================================
# LECTEUR NETCDF STREAMING (COAST-HF, COPERNICUS)
# ============================================================================

def stream_netcdf_chunks(filepath: Path, time_chunk_size: int = CHUNK_SIZE_NETCDF) -> Generator[Dict[str, Any], None, None]:
    """
    Lit un fichier NetCDF par morceaux temporels avec xarray+dask.
    
    Args:
        filepath: Chemin vers le fichier NetCDF
        time_chunk_size: Nombre de pas de temps par chunk
        
    Yields:
        Dict contenant les données du chunk avec métadonnées
    """
    try:
        import xarray as xr
        import dask
    except ImportError:
        logger.error("xarray et dask requis. Installation: pip install xarray dask netCDF4")
        raise
    
    logger.info(f"🌐 Lecture NetCDF streaming: {filepath.name}")
    logger.info(f"   Chunk size: {time_chunk_size} pas de temps")
    
    # Ouvrir avec dask (lazy loading)
    with xr.open_dataset(filepath, chunks={'time': time_chunk_size}) as ds:
        
        # Métadonnées globales
        station_id = ds.attrs.get('station_id', 'BARAG')
        total_times = len(ds.time)
        
        logger.info(f"   Variables: {list(ds.data_vars)}")
        logger.info(f"   Dimension temps: {total_times} points")
        
        chunk_count = 0
        total_processed = 0
        
        # Itération par chunks temporels
        for i in range(0, total_times, time_chunk_size):
            chunk_count += 1
            end_idx = min(i + time_chunk_size, total_times)
            
            # Sélection du chunk (toujours lazy)
            chunk_ds = ds.isel(time=slice(i, end_idx))
            
            # Chargement en mémoire du chunk uniquement
            chunk_ds = chunk_ds.load()
            
            # Vérification mémoire
            mem_mb = check_memory_limit()
            
            # Conversion en records
            records = []
            for t_idx in range(len(chunk_ds.time)):
                time_val = chunk_ds.time.values[t_idx]
                
                record = {
                    'time': pd.Timestamp(time_val).to_pydatetime(),
                    'station_id': station_id,
                    'temperature_air': float(chunk_ds['TEMP'].values[t_idx]) if 'TEMP' in chunk_ds else None,
                    'temperature_water': float(chunk_ds['TEMP_WATER'].values[t_idx]) if 'TEMP_WATER' in chunk_ds else None,
                    'salinity': float(chunk_ds['PSAL'].values[t_idx]) if 'PSAL' in chunk_ds else None,
                    'ph': float(chunk_ds['PH'].values[t_idx]) if 'PH' in chunk_ds else None,
                    'dissolved_oxygen': float(chunk_ds['DOX2'].values[t_idx]) if 'DOX2' in chunk_ds else None,
                    'quality_flag': int(chunk_ds.get('QC_FLAG', 0)),
                    'data_source': f"NetCDF:{filepath.name}",
                }
                
                # Filtrer les NaN
                record = {k: (None if isinstance(v, float) and np.isnan(v) else v) for k, v in record.items()}
                records.append(record)
            
            total_processed += len(records)
            
            yield {
                'records': records,
                'chunk_number': chunk_count,
                'chunk_size': len(records),
                'total_processed': total_processed,
                'memory_mb': mem_mb,
                'source_file': str(filepath),
                'format': 'NetCDF',
                'global_attrs': dict(ds.attrs)
            }
            
            # Nettoyage explicite
            del chunk_ds, records
            force_garbage_collection()
    
    logger.info(f"✓ NetCDF terminé: {total_processed} points en {chunk_count} chunks")


# ============================================================================
# LECTEUR GRIB2 STREAMING (MÉTÉO-FRANCE, COPERNICUS)
# ============================================================================

def stream_grib2_chunks(filepath: Path, message_chunk_size: int = 50) -> Generator[Dict[str, Any], None, None]:
    """
    Lit un fichier GRIB2 message par message (streaming séquentiel).
    
    Args:
        filepath: Chemin vers le fichier GRIB2
        message_chunk_size: Nombre de messages par chunk
        
    Yields:
        Dict contenant les données du chunk avec métadonnées
    """
    try:
        import pygrib
    except ImportError:
        logger.error("pygrib requis. Installation: pip install pygrib")
        raise
    
    logger.info(f"🌦️ Lecture GRIB2 streaming: {filepath.name}")
    
    grbs = pygrib.open(str(filepath))
    
    chunk_count = 0
    total_messages = 0
    records_buffer = []
    
    for grb in grbs:
        total_messages += 1
        
        # Extraction des données du message
        try:
            values = grb.values
            lats, lons = grb.latlons()
            valid_time = grb.validDate
            
            # Pour chaque point de grille (sous-échantillonnage si nécessaire)
            # Ici on prend un point représentatif (centre du bassin d'Arcachon)
            # Lat: 44.6°N, Lon: -1.2°W
            target_lat, target_lon = 44.6, -1.2
            
            # Trouver le point le plus proche
            lat_idx = np.argmin(np.abs(lats[:, 0] - target_lat))
            lon_idx = np.argmin(np.abs(lons[0, :] - target_lon))
            
            value = float(values[lat_idx, lon_idx])
            
            # Identifier le paramètre
            param_name = grb.name
            
            record = {
                'time': valid_time,
                'station_id': 'ARCACHON_GRID',
                'data_source': f"GRIB2:{filepath.name}:{param_name}",
                'quality_flag': 0,
            }
            
            # Mapper les paramètres GRIB aux champs de la base
            if 'Temperature' in param_name:
                record['temperature_air'] = value - 273.15  # Kelvin -> Celsius
            elif 'wind' in param_name.lower():
                record['wind_speed'] = value
            elif 'pressure' in param_name.lower():
                record['pressure'] = value / 100  # Pa -> hPa
            
            records_buffer.append(record)
            
        except Exception as e:
            logger.warning(f"Erreur lecture message GRIB: {e}")
            continue
        
        # Yield par chunks
        if len(records_buffer) >= message_chunk_size:
            chunk_count += 1
            mem_mb = check_memory_limit()
            
            yield {
                'records': records_buffer.copy(),
                'chunk_number': chunk_count,
                'chunk_size': len(records_buffer),
                'total_processed': total_messages,
                'memory_mb': mem_mb,
                'source_file': str(filepath),
                'format': 'GRIB2'
            }
            
            records_buffer.clear()
            force_garbage_collection()
    
    # Dernier chunk
    if records_buffer:
        chunk_count += 1
        yield {
            'records': records_buffer,
            'chunk_number': chunk_count,
            'chunk_size': len(records_buffer),
            'total_processed': total_messages,
            'memory_mb': get_memory_usage_mb(),
            'source_file': str(filepath),
            'format': 'GRIB2'
        }
    
    grbs.close()
    logger.info(f"✓ GRIB2 terminé: {total_messages} messages en {chunk_count} chunks")


# ============================================================================
# INSERTION BASE DE DONNÉES (BATCH OPTIMISÉ)
# ============================================================================

# ============================================================================
# INTÉGRATION TIMESCALEDB (Mission 4)
# ============================================================================

def get_db_connection() -> psycopg2.extensions.connection:
    """Crée une connexion à TimescaleDB avec gestion d'erreur."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info(f"[DB] Connexion établie: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"[DB] Erreur connexion: {e}")
        logger.error(f"[DB] Vérifiez que TimescaleDB est démarré et accessible")
        raise


def insert_batch_to_db(records: List[Dict[str, Any]], conn, upsert_mode: str = 'update') -> Tuple[int, int]:
    """
    Insère un batch de records dans TimescaleDB avec upsert idempotent.
    
    Args:
        records: Liste de dictionnaires contenant les données
        conn: Connexion psycopg2
        upsert_mode: 'update' (ON CONFLICT DO UPDATE) ou 'nothing' (ON CONFLICT DO NOTHING)
        
    Returns:
        Tuple (lignes insérées, lignes mises à jour)
    """
    if not records:
        return 0, 0
    
    # Normaliser les records (remplir les champs manquants avec None)
    normalized_records = []
    for record in records:
        normalized = {
            'time': record.get('time'),
            'station_id': record.get('station_id'),
            'temperature_air': record.get('temperature_air'),
            'humidity': record.get('humidity'),
            'pressure': record.get('pressure'),
            'wind_speed': record.get('wind_speed'),
            'wind_direction': record.get('wind_direction'),
            'precipitation': record.get('precipitation'),
            'temperature_water': record.get('temperature_water'),
            'salinity': record.get('salinity'),
            'ph': record.get('ph'),
            'dissolved_oxygen': record.get('dissolved_oxygen'),
            'turbidity': record.get('turbidity'),
            'quality_flag': record.get('quality_flag', 0),
            'data_source': record.get('data_source', 'UNKNOWN'),
        }
        normalized_records.append(normalized)
    
    # Requête avec UPSERT idempotent
    if upsert_mode == 'nothing':
        # Mode idempotent strict: ignore les doublons
        insert_query = """
            INSERT INTO barag.sensor_data (
                time, station_id, temperature_air, humidity, pressure,
                wind_speed, wind_direction, precipitation, temperature_water,
                salinity, ph, dissolved_oxygen, turbidity, quality_flag, data_source
            ) VALUES (
                %(time)s, %(station_id)s, %(temperature_air)s, %(humidity)s, %(pressure)s,
                %(wind_speed)s, %(wind_direction)s, %(precipitation)s, %(temperature_water)s,
                %(salinity)s, %(ph)s, %(dissolved_oxygen)s, %(turbidity)s, %(quality_flag)s, %(data_source)s
            )
            ON CONFLICT (time, station_id) DO NOTHING;
        """
    else:
        # Mode mise à jour: écrase les données existantes
        insert_query = """
            INSERT INTO barag.sensor_data (
                time, station_id, temperature_air, humidity, pressure,
                wind_speed, wind_direction, precipitation, temperature_water,
                salinity, ph, dissolved_oxygen, turbidity, quality_flag, data_source
            ) VALUES (
                %(time)s, %(station_id)s, %(temperature_air)s, %(humidity)s, %(pressure)s,
                %(wind_speed)s, %(wind_direction)s, %(precipitation)s, %(temperature_water)s,
                %(salinity)s, %(ph)s, %(dissolved_oxygen)s, %(turbidity)s, %(quality_flag)s, %(data_source)s
            )
            ON CONFLICT (time, station_id) DO UPDATE SET
                temperature_air = COALESCE(EXCLUDED.temperature_air, barag.sensor_data.temperature_air),
                humidity = COALESCE(EXCLUDED.humidity, barag.sensor_data.humidity),
                pressure = COALESCE(EXCLUDED.pressure, barag.sensor_data.pressure),
                wind_speed = COALESCE(EXCLUDED.wind_speed, barag.sensor_data.wind_speed),
                wind_direction = COALESCE(EXCLUDED.wind_direction, barag.sensor_data.wind_direction),
                precipitation = COALESCE(EXCLUDED.precipitation, barag.sensor_data.precipitation),
                temperature_water = COALESCE(EXCLUDED.temperature_water, barag.sensor_data.temperature_water),
                salinity = COALESCE(EXCLUDED.salinity, barag.sensor_data.salinity),
                ph = COALESCE(EXCLUDED.ph, barag.sensor_data.ph),
                dissolved_oxygen = COALESCE(EXCLUDED.dissolved_oxygen, barag.sensor_data.dissolved_oxygen),
                turbidity = COALESCE(EXCLUDED.turbidity, barag.sensor_data.turbidity),
                quality_flag = EXCLUDED.quality_flag,
                data_source = EXCLUDED.data_source;
        """
    
    try:
        with conn.cursor() as cursor:
            # Compter les lignes avant insertion
            cursor.execute("SELECT COUNT(*) FROM barag.sensor_data")
            count_before = cursor.fetchone()[0]
            
            # Insertion par batch
            execute_batch(cursor, insert_query, normalized_records, page_size=BATCH_SIZE_DB)
            
            # Compter les lignes après insertion
            cursor.execute("SELECT COUNT(*) FROM barag.sensor_data")
            count_after = cursor.fetchone()[0]
            
            conn.commit()
            
            inserted = count_after - count_before
            updated = len(normalized_records) - inserted
            
            logger.info(f"[DB] Batch traité: {inserted} insérées, {updated} mises à jour (mode: {upsert_mode})")
            
            return inserted, updated
    
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"[DB] Erreur insertion: {e}")
        logger.error(f"[DB] Premier record: {normalized_records[0] if normalized_records else 'N/A'}")
        raise


# ============================================================================
# ORCHESTRATEUR PRINCIPAL
# ============================================================================

def ingest_file(filepath: Path, file_format: Optional[str] = None) -> Dict[str, Any]:
    """
    Ingère un fichier de données océanographiques en mode streaming.
    
    Args:
        filepath: Chemin vers le fichier
        file_format: Format explicite ('csv', 'netcdf', 'grib2') ou auto-détection
        
    Returns:
        Dict avec statistiques d'ingestion
    """
    logger.info(f"🚀 Démarrage ingestion: {filepath}")
    logger.info(f"   Taille fichier: {filepath.stat().st_size / 1024 / 1024:.2f} Mo")
    
    start_time = datetime.now(timezone.utc)
    
    # Auto-détection du format
    if file_format is None:
        suffix = filepath.suffix.lower()
        if suffix == '.csv':
            file_format = 'csv'
        elif suffix in ['.nc', '.nc4', '.netcdf']:
            file_format = 'netcdf'
        elif suffix in ['.grb', '.grb2', '.grib', '.grib2']:
            file_format = 'grib2'
        else:
            raise ValueError(f"Format non reconnu: {suffix}")
    
    # Sélection du lecteur streaming
    if file_format == 'csv':
        chunk_generator = stream_csv_chunks(filepath)
    elif file_format == 'netcdf':
        chunk_generator = stream_netcdf_chunks(filepath)
    elif file_format == 'grib2':
        chunk_generator = stream_grib2_chunks(filepath)
    else:
        raise ValueError(f"Format non supporté: {file_format}")
    
    # Connexion à la base de données
    conn = get_db_connection()
    
    total_inserted = 0
    total_updated = 0
    max_memory_mb = 0
    chunks_processed = 0
    
    try:
        # Traitement chunk par chunk
        for chunk_data in chunk_generator:
            chunks_processed += 1
            records = chunk_data['records']
            mem_mb = chunk_data['memory_mb']
            
            max_memory_mb = max(max_memory_mb, mem_mb)
            
            # Insertion en base avec upsert
            inserted, updated = insert_batch_to_db(records, conn, upsert_mode='update')
            total_inserted += inserted
            total_updated += updated
            
            logger.info(
                f"  Chunk {chunk_data['chunk_number']}: "
                f"{inserted} insérées, {updated} mises à jour | "
                f"Mémoire: {mem_mb:.1f} Mo | "
                f"Total: {chunk_data['total_processed']}"
            )
            
            # Vérification mémoire après insertion
            check_memory_limit()
    
    finally:
        conn.close()
        logger.info(f"[DB] Connexion fermée")
    
    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()
    
    stats = {
        'file': str(filepath),
        'format': file_format,
        'total_inserted': total_inserted,
        'total_updated': total_updated,
        'total_processed': total_inserted + total_updated,
        'chunks_processed': chunks_processed,
        'duration_seconds': duration,
        'max_memory_mb': max_memory_mb,
        'rows_per_second': (total_inserted + total_updated) / duration if duration > 0 else 0,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'status': 'SUCCESS'
    }
    
    logger.info(f"[SUCCESS] Ingestion terminée: {total_inserted} insérées, {total_updated} mises à jour en {duration:.1f}s")
    logger.info(f"   Débit: {stats['rows_per_second']:.1f} lignes/s")
    logger.info(f"   Mémoire max: {max_memory_mb:.1f} Mo / {MEMORY_LIMIT_MB} Mo")
    
    return stats


# ============================================================================
# CLI
# ============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ocean Sentinel V3.0 - Ingestion streaming de données océanographiques',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Déclaration global avant utilisation
    global MEMORY_LIMIT_MB, CHUNK_SIZE_CSV, CHUNK_SIZE_NETCDF
    
    parser.add_argument('file', type=Path, help='Fichier à ingérer')
    parser.add_argument('--format', choices=['csv', 'netcdf', 'grib2'], help='Format explicite')
    parser.add_argument('--chunk-size-csv', type=int, default=CHUNK_SIZE_CSV, help='Taille chunk CSV')
    parser.add_argument('--chunk-size-netcdf', type=int, default=CHUNK_SIZE_NETCDF, help='Taille chunk NetCDF')
    parser.add_argument('--memory-limit', type=int, default=MEMORY_LIMIT_MB, help='Limite mémoire (Mo)')
    
    args = parser.parse_args()
    
    # Mise à jour des limites
    MEMORY_LIMIT_MB = args.memory_limit
    CHUNK_SIZE_CSV = args.chunk_size_csv
    CHUNK_SIZE_NETCDF = args.chunk_size_netcdf
    
    # Vérification fichier
    if not args.file.exists():
        logger.error(f"❌ Fichier introuvable: {args.file}")
        sys.exit(1)
    
    # Ingestion
    try:
        stats = ingest_file(args.file, args.format)
        logger.info(f"📊 Statistiques: {stats}")
        sys.exit(0)
    
    except MemoryError as e:
        logger.error(f"💥 ERREUR MÉMOIRE: {e}")
        logger.error("Réduisez la taille des chunks avec --chunk-size-csv ou --chunk-size-netcdf")
        sys.exit(2)
    
    except Exception as e:
        logger.error(f"💥 ERREUR: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
