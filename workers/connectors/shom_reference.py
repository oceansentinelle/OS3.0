#!/usr/bin/env python3
"""
================================================================================
Connecteur SHOM Reference - Phase 2
================================================================================

Connecteur pour moissonner les métadonnées et référentiels SHOM.

Source: https://services.data.shom.fr/geonetwork/srv/api

Fonctionnalités:
- Moissonnage GeoNetwork API
- Récupération métadonnées Litto3D
- Liens téléchargement et services OGC
- Référentiels bathymétrie/marée

Mode:
- Batch référentiel (pas temps réel)
- Stockage métadonnées pour enrichissement
- Mise à jour périodique (12h par défaut)

Conformité:
- source_code='shom_reference'
- record_type='reference_metadata'
- Traçabilité complète
================================================================================
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from workers.connectors.contracts import ConnectorRecord, ConnectorRunResult

logger = logging.getLogger("ocean_sentinel.connector.shom")


class ShomReferenceConnector:
    """Connecteur SHOM Reference (GeoNetwork)."""
    
    source_code = "shom_reference"

    def __init__(
        self,
        base_url: str,
        default_queries: list[str],
        max_records: int = 50,
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_queries = [q.strip() for q in default_queries if q.strip()]
        self.max_records = max_records
        self.timeout_seconds = timeout_seconds

    def _extract_records(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extrait enregistrements depuis réponse GeoNetwork.
        
        GeoNetwork peut retourner différents formats selon version/endpoint.
        """
        if isinstance(payload.get("metadata"), list):
            return payload["metadata"]
        if isinstance(payload.get("records"), list):
            return payload["records"]
        if isinstance(payload.get("items"), list):
            return payload["items"]
        if isinstance(payload.get("results"), list):
            return payload["results"]
        return []

    def _normalize_record(self, raw: dict[str, Any]) -> ConnectorRecord:
        """
        Normalise enregistrement GeoNetwork vers ConnectorRecord.
        
        Args:
            raw: Enregistrement brut GeoNetwork
            
        Returns:
            ConnectorRecord normalisé
        """
        # Identifier
        identifier = (
            raw.get("uuid")
            or raw.get("id")
            or raw.get("metadataIdentifier")
            or raw.get("fileIdentifier")
            or raw.get("name")
            or "unknown"
        )

        # Extraire liens (téléchargement, OGC, etc.)
        links = raw.get("link") or raw.get("links") or raw.get("onlineResources") or []
        if isinstance(links, dict):
            links = [links]

        # Payload normalisé
        payload = {
            "title": raw.get("title"),
            "abstract": raw.get("abstract") or raw.get("description"),
            "keywords": raw.get("keyword") or raw.get("keywords"),
            "changeDate": raw.get("changeDate"),
            "creationDate": raw.get("createDate") or raw.get("creationDate"),
            "links": links,
            "raw": raw,
        }

        # Métadonnées enrichies
        metadata = {
            "bbox": raw.get("bbox") or raw.get("geom"),
            "dataset_type": raw.get("type"),
            "organisation": raw.get("orgName") or raw.get("org"),
            "topic": raw.get("topicCat"),
        }

        return ConnectorRecord(
            source_code=self.source_code,
            external_id=str(identifier),
            record_type="reference_metadata",
            observed_at=datetime.now(timezone.utc),
            payload=payload,
            metadata=metadata,
        )

    def _search(self, client: httpx.Client, query: str) -> list[ConnectorRecord]:
        """
        Recherche métadonnées GeoNetwork.
        
        Args:
            client: Client HTTP
            query: Terme de recherche
            
        Returns:
            Liste de ConnectorRecord
        """
        url = f"{self.base_url}/records"
        params = {
            "any": query,
            "from": 1,
            "to": self.max_records,
            "hitsPerPage": self.max_records,
        }
        headers = {"Accept": "application/json"}

        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()

        payload = response.json()
        raw_records = self._extract_records(payload)
        normalized = [self._normalize_record(item) for item in raw_records]

        logger.info(
            "shom.search.ok | query=%s | count=%s",
            query,
            len(normalized),
        )
        return normalized

    def run(self) -> ConnectorRunResult:
        """
        Exécute moissonnage SHOM.
        
        Returns:
            ConnectorRunResult avec métadonnées collectées
        """
        started_at = datetime.now(timezone.utc)
        result = ConnectorRunResult(
            source_code=self.source_code,
            started_at=started_at,
            ended_at=started_at,
        )

        seen_ids: set[str] = set()

        with httpx.Client(timeout=self.timeout_seconds) as client:
            for query in self.default_queries:
                try:
                    records = self._search(client, query)
                    for record in records:
                        if record.external_id in seen_ids:
                            continue
                        seen_ids.add(record.external_id)
                        result.records.append(record)
                except Exception as exc:
                    logger.exception("shom.search.failure | query=%s", query)
                    result.errors.append(f"{query}: {exc}")

        result.ended_at = datetime.now(timezone.utc)
        logger.info(
            "shom.run.done | total_records=%s | warnings=%s | errors=%s | duration=%.2fs",
            result.record_count,
            len(result.warnings),
            len(result.errors),
            result.duration_seconds
        )
        return result


# ============================================================================
# Tests
# ============================================================================

if __name__ == "__main__":
    # Test connecteur SHOM
    connector = ShomReferenceConnector(
        base_url="https://services.data.shom.fr/geonetwork/srv/api",
        default_queries=["Litto3D Nouvelle-Aquitaine", "Arcachon", "bathymetrie"],
        max_records=10,
    )
    
    print("=" * 80)
    print("TEST CONNECTEUR SHOM REFERENCE")
    print("=" * 80)
    
    result = connector.run()
    
    print(f"\n✅ Moissonnage terminé")
    print(f"   Records: {result.record_count}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Duration: {result.duration_seconds:.2f}s")
    
    if result.records:
        print("\nExemple record:")
        record = result.records[0]
        print(f"  ID: {record.external_id}")
        print(f"  Type: {record.record_type}")
        print(f"  Title: {record.payload.get('title')}")
        print(f"  Links: {len(record.payload.get('links', []))}")
