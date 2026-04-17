#!/usr/bin/env python3
"""
================================================================================
Connecteurs INSEE Phase 2
================================================================================

Connecteurs pour référentiels INSEE:
1. InseeGeoConnector: Géographie administrative (API Geo)
2. InseeSireneConnector: Établissements (API Sirene)

Sources:
- https://geo.api.gouv.fr
- https://api.insee.fr/api-sirene/3.11

Mode:
- Batch référentiel (quotidien)
- Enrichissement territorial
- Segmentation établissements

Conformité:
- source_code='insee_geo' / 'insee_sirene'
- Traçabilité complète
- API key sécurisée (Sirene)
================================================================================
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from workers.connectors.contracts import ConnectorRecord, ConnectorRunResult

logger = logging.getLogger("ocean_sentinel.connector.insee")


class InseeGeoConnector:
    """Connecteur INSEE Geo (référentiel géographique)."""
    
    source_code = "insee_geo"

    def __init__(
        self,
        base_url: str,
        departments: list[str],
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.departments = [d.strip() for d in departments if d.strip()]
        self.timeout_seconds = timeout_seconds

    def _fetch_departments(self, client: httpx.Client) -> list[dict[str, Any]]:
        """Récupère liste départements."""
        response = client.get(f"{self.base_url}/departements", params={"format": "json"})
        response.raise_for_status()
        return response.json()

    def _fetch_communes_for_department(
        self,
        client: httpx.Client,
        department_code: str
    ) -> list[dict[str, Any]]:
        """Récupère communes d'un département."""
        response = client.get(
            f"{self.base_url}/departements/{department_code}/communes",
            params={
                "format": "json",
                "fields": "nom,code,codeDepartement,codeRegion,codesPostaux,population,centre",
            },
        )
        response.raise_for_status()
        return response.json()

    def run(self) -> ConnectorRunResult:
        """
        Exécute synchronisation référentiel géographique.
        
        Returns:
            ConnectorRunResult avec départements et communes
        """
        started_at = datetime.now(timezone.utc)
        result = ConnectorRunResult(
            source_code=self.source_code,
            started_at=started_at,
            ended_at=started_at,
        )

        with httpx.Client(timeout=self.timeout_seconds) as client:
            try:
                # Récupérer départements
                departments = self._fetch_departments(client)
                
                for dep in departments:
                    dep_code = dep.get("code")
                    
                    # Filtrer si liste départements spécifiée
                    if self.departments and dep_code not in self.departments:
                        continue

                    # Enregistrer département
                    result.records.append(
                        ConnectorRecord(
                            source_code=self.source_code,
                            external_id=f"department:{dep_code}",
                            record_type="department_reference",
                            observed_at=datetime.now(timezone.utc),
                            payload=dep,
                            metadata={"scope": "department"},
                        )
                    )

                    # Récupérer communes du département
                    try:
                        communes = self._fetch_communes_for_department(client, dep_code)
                        
                        for commune in communes:
                            result.records.append(
                                ConnectorRecord(
                                    source_code=self.source_code,
                                    external_id=f"commune:{commune.get('code')}",
                                    record_type="commune_reference",
                                    observed_at=datetime.now(timezone.utc),
                                    payload=commune,
                                    metadata={
                                        "department_code": dep_code,
                                        "region_code": commune.get("codeRegion"),
                                        "scope": "commune",
                                    },
                                )
                            )
                        
                        logger.info(
                            "insee_geo.department.ok | code=%s | communes=%d",
                            dep_code,
                            len(communes)
                        )
                        
                    except Exception as exc:
                        logger.exception("insee_geo.communes.failure | department=%s", dep_code)
                        result.errors.append(f"department:{dep_code} communes: {exc}")
                        
            except Exception as exc:
                logger.exception("insee_geo.run.failure")
                result.errors.append(str(exc))

        result.ended_at = datetime.now(timezone.utc)
        logger.info(
            "insee_geo.run.done | total_records=%s | errors=%s | duration=%.2fs",
            result.record_count,
            len(result.errors),
            result.duration_seconds
        )
        return result


class InseeSireneConnector:
    """Connecteur INSEE Sirene (établissements)."""
    
    source_code = "insee_sirene"

    def __init__(
        self,
        base_url: str,
        api_key: str | None,
        tracked_sirens: list[str],
        tracked_sirets: list[str],
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.tracked_sirens = tracked_sirens
        self.tracked_sirets = tracked_sirets
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict[str, str]:
        """Headers HTTP avec API key."""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _fetch_siren(self, client: httpx.Client, siren: str) -> dict[str, Any]:
        """Récupère données SIREN (unité légale)."""
        response = client.get(
            f"{self.base_url}/siren/{siren}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def _fetch_siret(self, client: httpx.Client, siret: str) -> dict[str, Any]:
        """Récupère données SIRET (établissement)."""
        response = client.get(
            f"{self.base_url}/siret/{siret}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def run(self) -> ConnectorRunResult:
        """
        Exécute synchronisation établissements Sirene.
        
        Returns:
            ConnectorRunResult avec SIREN/SIRET trackés
        """
        started_at = datetime.now(timezone.utc)
        result = ConnectorRunResult(
            source_code=self.source_code,
            started_at=started_at,
            ended_at=started_at,
        )

        if not self.api_key:
            result.warnings.append("INSEE_SIRENE_API_KEY missing; connector skipped.")
            result.ended_at = datetime.now(timezone.utc)
            logger.warning("insee_sirene.skipped | missing api key")
            return result

        with httpx.Client(timeout=self.timeout_seconds) as client:
            # Récupérer SIREN (unités légales)
            for siren in self.tracked_sirens:
                try:
                    payload = self._fetch_siren(client, siren)
                    result.records.append(
                        ConnectorRecord(
                            source_code=self.source_code,
                            external_id=f"siren:{siren}",
                            record_type="legal_unit_reference",
                            observed_at=datetime.now(timezone.utc),
                            payload=payload,
                            metadata={"scope": "siren"},
                        )
                    )
                    logger.info("insee_sirene.siren.ok | siren=%s", siren)
                except Exception as exc:
                    logger.exception("insee_sirene.fetch_siren.failure | siren=%s", siren)
                    result.errors.append(f"siren:{siren}: {exc}")

            # Récupérer SIRET (établissements)
            for siret in self.tracked_sirets:
                try:
                    payload = self._fetch_siret(client, siret)
                    result.records.append(
                        ConnectorRecord(
                            source_code=self.source_code,
                            external_id=f"siret:{siret}",
                            record_type="establishment_reference",
                            observed_at=datetime.now(timezone.utc),
                            payload=payload,
                            metadata={"scope": "siret"},
                        )
                    )
                    logger.info("insee_sirene.siret.ok | siret=%s", siret)
                except Exception as exc:
                    logger.exception("insee_sirene.fetch_siret.failure | siret=%s", siret)
                    result.errors.append(f"siret:{siret}: {exc}")

        result.ended_at = datetime.now(timezone.utc)
        logger.info(
            "insee_sirene.run.done | total_records=%s | warnings=%s | errors=%s | duration=%.2fs",
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
    # Test INSEE Geo
    print("=" * 80)
    print("TEST CONNECTEUR INSEE GEO")
    print("=" * 80)
    
    geo_connector = InseeGeoConnector(
        base_url="https://geo.api.gouv.fr",
        departments=["33"],  # Gironde uniquement pour test
    )
    
    geo_result = geo_connector.run()
    
    print(f"\n✅ Synchronisation terminée")
    print(f"   Records: {geo_result.record_count}")
    print(f"   Errors: {len(geo_result.errors)}")
    print(f"   Duration: {geo_result.duration_seconds:.2f}s")
    
    if geo_result.records:
        print("\nExemple département:")
        dept = [r for r in geo_result.records if r.record_type == "department_reference"][0]
        print(f"  Code: {dept.payload.get('code')}")
        print(f"  Nom: {dept.payload.get('nom')}")
        
        print("\nExemple commune:")
        commune = [r for r in geo_result.records if r.record_type == "commune_reference"][0]
        print(f"  Code: {commune.payload.get('code')}")
        print(f"  Nom: {commune.payload.get('nom')}")
        print(f"  Population: {commune.payload.get('population')}")
    
    # Test INSEE Sirene (skip si pas d'API key)
    print("\n" + "=" * 80)
    print("TEST CONNECTEUR INSEE SIRENE")
    print("=" * 80)
    
    sirene_connector = InseeSireneConnector(
        base_url="https://api.insee.fr/api-sirene/3.11",
        api_key=None,  # Pas d'API key pour test
        tracked_sirens=[],
        tracked_sirets=[],
    )
    
    sirene_result = sirene_connector.run()
    
    print(f"\n⚠️  Skipped (no API key)")
    print(f"   Warnings: {len(sirene_result.warnings)}")
