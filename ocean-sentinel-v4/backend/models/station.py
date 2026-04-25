"""
Modèles Pydantic pour données stations
Conformes au format Ocean Sentinel
"""

from pydantic import BaseModel, Field
from typing import Literal, List
from datetime import datetime


class Parameter(BaseModel):
    """Paramètre océanographique"""
    name: str = Field(..., description="Code paramètre (TEMP, PSAL, DOX2, PH_TOTAL)")
    value: float = Field(..., description="Valeur mesurée")
    unit: str = Field(..., description="Unité (°C, PSU, µmol/kg)")
    status: Literal["measured", "inferred", "simulated"] = Field(
        ..., 
        description="Statut vérité SACS"
    )
    source: str = Field(..., description="Source données (COAST-HF, Hub'Eau, etc.)")
    timestamp: str = Field(..., description="Timestamp ISO 8601")
    quality_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Score qualité (0-1)"
    )
    is_critical: bool = Field(..., description="Alerte critique SACS")


class StationData(BaseModel):
    """Données complètes d'une station"""
    station_id: str = Field(..., description="Identifiant station")
    timestamp: str = Field(..., description="Timestamp agrégation ISO 8601")
    parameters: List[Parameter] = Field(..., description="Liste paramètres")


class HealthCheck(BaseModel):
    """Health check response"""
    status: Literal["ok", "degraded", "error"] = "ok"
    timestamp: str
    version: str = "1.0.0"
    services: dict = {}
