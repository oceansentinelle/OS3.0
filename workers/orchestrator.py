#!/usr/bin/env python3
"""
================================================================================
Ocean Sentinel V3.0 - Orchestrateur Principal
================================================================================

Orchestrateur central pour planification et exécution des jobs d'ingestion.

Architecture:
- APScheduler pour planification
- Jobs configurables via variables d'environnement
- Logging structuré
- Gestion erreurs avec retry

Jobs supportés:
- Phase 1 MVP: ERDDAP, Hub'Eau, SEANOE, SIBA
- Phase 2: SHOM Reference, INSEE Geo, INSEE Sirene
- Phase 3: Copernicus, EUMETSAT, NOAA (à venir)

Conformité:
- Fail-safe (un job qui échoue ne bloque pas les autres)
- Métriques de succès/échec
- Traçabilité complète
================================================================================
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Iterable

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Imports connecteurs Phase 1
from workers.connectors.erddap_ifremer import get_coast_hf_arcachon_connector, get_somlit_arcachon_connector
from workers.connectors.hubeau import get_bassin_arcachon_connector
from workers.connectors.seanoe_loader import SeanoeLoader
from workers.connectors.siba_enki_loader import SibaEnkiLoader

# Imports connecteurs Phase 2
from workers.connectors.shom_reference import ShomReferenceConnector
from workers.connectors.insee_phase2 import InseeGeoConnector, InseeSireneConnector

logger = logging.getLogger("ocean_sentinel.orchestrator")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


@dataclass(frozen=True)
class JobSpec:
    """Spécification d'un job planifié."""
    job_id: str
    enabled: bool
    interval_minutes: int
    runner: Callable[[], None]
    description: str


def _bool_env(name: str, default: bool = False) -> bool:
    """Parse variable d'environnement booléenne."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    """Parse variable d'environnement entière."""
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _safe_run(job_name: str, fn: Callable[[], None]) -> Callable[[], None]:
    """
    Wrapper pour exécution sécurisée d'un job.
    
    Capture exceptions et log succès/échec.
    """
    def wrapped() -> None:
        started_at = datetime.now(timezone.utc)
        logger.info("job.start | job=%s | started_at=%s", job_name, started_at.isoformat())
        try:
            fn()
            ended_at = datetime.now(timezone.utc)
            duration = (ended_at - started_at).total_seconds()
            logger.info(
                "job.success | job=%s | ended_at=%s | duration_seconds=%.2f",
                job_name,
                ended_at.isoformat(),
                duration
            )
        except Exception:
            logger.exception("job.failure | job=%s", job_name)
            # Ne pas re-raise pour ne pas bloquer le scheduler

    return wrapped


# ============================================================================
# Jobs Phase 1 - MVP
# ============================================================================

def run_erddap_coast_hf():
    """Job ERDDAP COAST-HF Arcachon-Ferret."""
    from datetime import timedelta
    
    connector = get_coast_hf_arcachon_connector()
    
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)
    
    measurements = connector.fetch_data(start_time, end_time)
    
    logger.info(
        "erddap_coast_hf.complete | measurements=%d | period=%s to %s",
        len(measurements),
        start_time.isoformat(),
        end_time.isoformat()
    )
    
    # TODO: Insérer dans base de données
    # from workers.pipelines.ingest import insert_measurements
    # insert_measurements(measurements)


def run_erddap_somlit():
    """Job ERDDAP SOMLIT Arcachon."""
    from datetime import timedelta
    
    connector = get_somlit_arcachon_connector()
    
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)
    
    measurements = connector.fetch_data(start_time, end_time)
    
    logger.info(
        "erddap_somlit.complete | measurements=%d | period=%s to %s",
        len(measurements),
        start_time.isoformat(),
        end_time.isoformat()
    )


def run_hubeau():
    """Job Hub'Eau Bassin d'Arcachon."""
    from datetime import timedelta
    
    connector = get_bassin_arcachon_connector()
    
    # Bbox Bassin d'Arcachon
    bbox = (-1.30, 44.60, -1.15, 44.75)
    
    # Rechercher stations
    stations = connector.search_stations(bbox=bbox)
    station_codes = [s['code_station'] for s in stations[:10]]  # Limiter à 10 stations
    
    logger.info("hubeau.stations_found | count=%d", len(stations))
    
    # Récupérer données (7 derniers jours avec chunking)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)
    
    measurements = connector.fetch_data_chunked(
        start_time,
        end_time,
        station_codes=station_codes,
        chunk_days=7
    )
    
    logger.info(
        "hubeau.complete | measurements=%d | stations=%d",
        len(measurements),
        len(station_codes)
    )


def run_seanoe_loader():
    """Job chargement SEANOE (batch historique)."""
    loader = SeanoeLoader({
        'data_dir': os.getenv('SEANOE_DATA_DIR', './data/seanoe')
    })
    
    measurements = loader.load_directory(file_pattern='*.nc')
    
    logger.info("seanoe.complete | measurements=%d", len(measurements))


def run_siba_loader():
    """Job chargement SIBA Enki (data_drop)."""
    loader = SibaEnkiLoader({
        'data_drop_dir': os.getenv('SIBA_DATA_DROP_DIR', './data_drop/siba'),
        'processed_dir': os.getenv('SIBA_PROCESSED_DIR', './data_drop/siba/processed')
    })
    
    measurements = loader.load_data_drop()
    
    logger.info("siba.complete | measurements=%d", len(measurements))


# ============================================================================
# Jobs Phase 2 - Référentiels
# ============================================================================

def run_shom_reference():
    """Job SHOM Reference (métadonnées/référentiels)."""
    connector = ShomReferenceConnector(
        base_url=os.getenv("SHOM_BASE_URL", "https://services.data.shom.fr/geonetwork/srv/api"),
        default_queries=os.getenv(
            "SHOM_DEFAULT_QUERIES",
            "Litto3D Nouvelle-Aquitaine,Arcachon,bathymetrie,maree"
        ).split(","),
        max_records=_int_env("SHOM_MAX_RECORDS", 50),
    )
    
    result = connector.run()
    
    logger.info(
        "shom_reference.complete | records=%d | warnings=%d | errors=%d",
        result.record_count,
        len(result.warnings),
        len(result.errors)
    )


def run_insee_geo():
    """Job INSEE Geo (référentiel géographique)."""
    connector = InseeGeoConnector(
        base_url=os.getenv("API_GEO_BASE_URL", "https://geo.api.gouv.fr"),
        departments=os.getenv("API_GEO_DEPARTMENTS", "33,17").split(","),
    )
    
    result = connector.run()
    
    logger.info(
        "insee_geo.complete | records=%d | errors=%d",
        result.record_count,
        len(result.errors)
    )


def run_insee_sirene():
    """Job INSEE Sirene (établissements)."""
    connector = InseeSireneConnector(
        base_url=os.getenv("INSEE_SIRENE_BASE_URL", "https://api.insee.fr/api-sirene/3.11"),
        api_key=os.getenv("INSEE_SIRENE_API_KEY"),
        tracked_sirens=[x for x in os.getenv("INSEE_TRACKED_SIRENS", "").split(",") if x],
        tracked_sirets=[x for x in os.getenv("INSEE_TRACKED_SIRETS", "").split(",") if x],
    )
    
    result = connector.run()
    
    logger.info(
        "insee_sirene.complete | records=%d | warnings=%d | errors=%d",
        result.record_count,
        len(result.warnings),
        len(result.errors)
    )


# ============================================================================
# Configuration Jobs
# ============================================================================

def build_jobs() -> Iterable[JobSpec]:
    """
    Construit la liste des jobs à planifier.
    
    Returns:
        Liste de JobSpec
    """
    return [
        # Phase 1 - MVP
        JobSpec(
            job_id="erddap_coast_hf",
            enabled=_bool_env("ENABLE_ERDDAP_COAST_HF", True),
            interval_minutes=_int_env("ERDDAP_COAST_HF_INTERVAL_MINUTES", 60),
            runner=_safe_run("erddap_coast_hf", run_erddap_coast_hf),
            description="Ingestion ERDDAP COAST-HF Arcachon-Ferret (hourly)",
        ),
        JobSpec(
            job_id="erddap_somlit",
            enabled=_bool_env("ENABLE_ERDDAP_SOMLIT", True),
            interval_minutes=_int_env("ERDDAP_SOMLIT_INTERVAL_MINUTES", 360),  # 6h
            runner=_safe_run("erddap_somlit", run_erddap_somlit),
            description="Ingestion ERDDAP SOMLIT Arcachon (every 6h)",
        ),
        JobSpec(
            job_id="hubeau",
            enabled=_bool_env("ENABLE_HUBEAU", True),
            interval_minutes=_int_env("HUBEAU_INTERVAL_MINUTES", 360),  # 6h
            runner=_safe_run("hubeau", run_hubeau),
            description="Ingestion Hub'Eau Bassin d'Arcachon (every 6h)",
        ),
        JobSpec(
            job_id="seanoe_loader",
            enabled=_bool_env("ENABLE_SEANOE_LOADER", False),  # Batch manuel par défaut
            interval_minutes=_int_env("SEANOE_LOADER_INTERVAL_MINUTES", 1440),  # daily
            runner=_safe_run("seanoe_loader", run_seanoe_loader),
            description="Chargement SEANOE historique (daily batch)",
        ),
        JobSpec(
            job_id="siba_loader",
            enabled=_bool_env("ENABLE_SIBA_LOADER", True),
            interval_minutes=_int_env("SIBA_LOADER_INTERVAL_MINUTES", 120),  # 2h
            runner=_safe_run("siba_loader", run_siba_loader),
            description="Chargement SIBA Enki data_drop (every 2h)",
        ),
        
        # Phase 2 - Référentiels
        JobSpec(
            job_id="shom_reference_sync",
            enabled=_bool_env("ENABLE_SHOM_REFERENCE", True),
            interval_minutes=_int_env("SHOM_SYNC_INTERVAL_MINUTES", 720),  # 12h
            runner=_safe_run("shom_reference_sync", run_shom_reference),
            description="Harvest SHOM metadata/reference layers (GeoNetwork / Litto3D / tide refs).",
        ),
        JobSpec(
            job_id="insee_geo_sync",
            enabled=_bool_env("ENABLE_INSEE_GEO", True),
            interval_minutes=_int_env("INSEE_GEO_SYNC_INTERVAL_MINUTES", 1440),  # daily
            runner=_safe_run("insee_geo_sync", run_insee_geo),
            description="Sync communes/departments/regions reference data for configured departments.",
        ),
        JobSpec(
            job_id="insee_sirene_sync",
            enabled=_bool_env("ENABLE_INSEE_SIRENE", False),  # Désactivé par défaut (nécessite API key)
            interval_minutes=_int_env("INSEE_SIRENE_SYNC_INTERVAL_MINUTES", 1440),  # daily
            runner=_safe_run("insee_sirene_sync", run_insee_sirene),
            description="Refresh tracked SIREN/SIRET entities from INSEE Sirene API.",
        ),
    ]


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    """Point d'entrée orchestrateur."""
    logger.info("=" * 80)
    logger.info("OCEAN SENTINEL V3.0 - ORCHESTRATEUR")
    logger.info("=" * 80)
    
    scheduler = BlockingScheduler(timezone="UTC")

    for job in build_jobs():
        if not job.enabled:
            logger.info("job.disabled | job_id=%s | description=%s", job.job_id, job.description)
            continue

        scheduler.add_job(
            job.runner,
            trigger=IntervalTrigger(minutes=job.interval_minutes),
            id=job.job_id,
            name=job.description,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=600,
        )
        logger.info(
            "job.scheduled | job_id=%s | every=%s min | description=%s",
            job.job_id,
            job.interval_minutes,
            job.description,
        )

    logger.info("=" * 80)
    logger.info("orchestrator.ready | jobs_enabled=%d", len([j for j in build_jobs() if j.enabled]))
    logger.info("=" * 80)
    
    scheduler.start()


if __name__ == "__main__":
    main()
