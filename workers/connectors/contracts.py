#!/usr/bin/env python3
"""
================================================================================
Contrats Connecteurs - Ocean Sentinel V3.0
================================================================================

Contrats standardisés pour tous les connecteurs.

Architecture:
- ConnectorRecord: Enregistrement normalisé
- ConnectorRunResult: Résultat d'exécution job

Conformité:
- Traçabilité complète
- Métadonnées structurées
- Gestion erreurs/warnings
================================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ConnectorRecord:
    """Enregistrement normalisé d'un connecteur."""
    
    source_code: str
    """Code source (ex: 'shom_reference', 'insee_geo')"""
    
    external_id: str
    """Identifiant externe unique"""
    
    record_type: str
    """Type d'enregistrement (ex: 'reference_metadata', 'commune_reference')"""
    
    observed_at: datetime | None
    """Date d'observation/collecte"""
    
    payload: dict[str, Any]
    """Payload complet de l'enregistrement"""
    
    metadata: dict[str, Any] = field(default_factory=dict)
    """Métadonnées additionnelles"""


@dataclass
class ConnectorRunResult:
    """Résultat d'exécution d'un connecteur."""
    
    source_code: str
    """Code source"""
    
    started_at: datetime
    """Date début exécution"""
    
    ended_at: datetime
    """Date fin exécution"""
    
    records: list[ConnectorRecord] = field(default_factory=list)
    """Enregistrements collectés"""
    
    warnings: list[str] = field(default_factory=list)
    """Warnings non bloquants"""
    
    errors: list[str] = field(default_factory=list)
    """Erreurs rencontrées"""

    @property
    def record_count(self) -> int:
        """Nombre d'enregistrements."""
        return len(self.records)
    
    @property
    def duration_seconds(self) -> float:
        """Durée d'exécution en secondes."""
        return (self.ended_at - self.started_at).total_seconds()
    
    @property
    def success(self) -> bool:
        """Succès si aucune erreur."""
        return len(self.errors) == 0
