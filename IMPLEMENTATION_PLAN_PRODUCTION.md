# 🚀 Ocean Sentinel V3.0 - Plan d'Implémentation Production

## Document de Référence : Mise en Service Pipeline API Complet

**Version :** 1.0  
**Date :** 17 avril 2026  
**Auteur :** Lead Engineer Ocean Sentinel  
**Statut :** READY FOR EXECUTION

---

# A. Vue d'Ensemble d'Implémentation

## Résumé Pipeline Cible

Ocean Sentinel V3.0 implémente un **pipeline industriel de données océanographiques** avec architecture 3 couches :

```
SOURCES → INGESTION → RAW → TRANSFORMATION → PROCESSED → SERVING → API → CLIENTS
```

### Objectifs Métier

- ✅ Surveillance temps réel Bassin d'Arcachon
- ✅ Alertes écologiques SACS (pH, O₂)
- ✅ Prévisions IA (LSTM 12h/24h)
- ✅ Dashboard Grafana opérationnel
- ✅ API REST pour intégrations tierces

### Composants à Construire

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Connecteurs API** | Python + requests | Collecte multi-sources |
| **Orchestrateur** | Python asyncio | Coordination ingestion |
| **Validateur** | Pydantic | Validation schéma |
| **Transformateur** | Pandas/NumPy | Normalisation + enrichissement |
| **Base de données** | TimescaleDB | Stockage 3 couches |
| **API Backend** | FastAPI | Exposition REST |
| **Dashboard** | Grafana | Visualisation |
| **Alertes** | Python + règles SACS | Détection anomalies |
| **ML Engine** | TensorFlow/LSTM | Prédictions |
| **Monitoring** | Logs + métriques | Supervision |

### Dépendances Principales

```txt
# Backend
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
psycopg2-binary==2.9.9

# Data processing
pandas==2.1.4
numpy==1.24.3
xarray==2023.1.0
dask==2023.1.0

# ML
tensorflow==2.15.0
scikit-learn==1.3.2

# Monitoring
python-dotenv==1.0.0
requests==2.31.0
```

---

# B. Architecture Technique à Implémenter

## Modules Backend

```
ocean-sentinel/
├── api/                    # FastAPI backend
│   ├── main.py            # Point d'entrée API
│   ├── routes/            # Endpoints REST
│   │   ├── stations.py
│   │   ├── metrics.py
│   │   ├── alerts.py
│   │   ├── forecast.py
│   │   └── quality.py
│   ├── models/            # Modèles Pydantic
│   ├── database.py        # Pool connexions
│   └── config.py          # Configuration
│
├── workers/               # Services d'ingestion
│   ├── orchestrator.py    # Orchestrateur principal
│   ├── connectors/        # Connecteurs sources
│   │   ├── coast_hf.py
│   │   ├── weather.py
│   │   ├── tide.py
│   │   └── sentinel3.py
│   ├── validators/        # Validation données
│   ├── transformers/      # Normalisation
│   └── enrichers/         # Enrichissement
│
├── ml/                    # Moteur ML
│   ├── models/            # Modèles LSTM
│   ├── training.py        # Entraînement
│   ├── inference.py       # Prédictions
│   └── features.py        # Feature engineering
│
├── alerts/                # Moteur alertes
│   ├── rules.py           # Règles SACS
│   ├── engine.py          # Évaluation
│   └── notifications.py   # Notifications
│
└── scripts/               # Utilitaires
    ├── init_db.sql        # Schéma BDD
    ├── migrate.py         # Migrations
    └── seed_data.py       # Données test
```

## Services Docker

```yaml
services:
  timescaledb:     # Base de données
  api:             # FastAPI backend
  ingestion:       # Worker ingestion
  ml-engine:       # Prédictions IA
  grafana:         # Dashboard
  nginx:           # Reverse proxy (optionnel)
```

## Stockage 3 Couches

### RAW LAYER
- `raw_ingestion_log` - Audit
- `raw_measurements` - Payload JSON

### PROCESSED LAYER
- `validated_measurements` - Données normalisées
- `derived_metrics` - Métriques calculées

### SERVING LAYER
- `latest_metrics` - Vue matérialisée
- `hourly_aggregates` - Agrégats
- `alerts` - Événements
- `forecast_predictions` - Prévisions

## Exposition API

**Base URL:** `http://VPS_IP:8000/api/v1`

### Endpoints Critiques

```
GET  /stations                    # Liste stations
GET  /stations/{id}               # Détails station
GET  /metrics/latest              # Dernières mesures
GET  /metrics/latest/{station_id} # Mesures station
GET  /metrics/history             # Historique
GET  /alerts                      # Alertes actives
GET  /alerts/{id}                 # Détail alerte
GET  /forecast/{station_id}       # Prévisions
GET  /quality/station/{id}        # Rapport qualité
GET  /health                      # Health check
```

---

# C. Plan d'Implémentation Détaillé

## PHASE 1 : Préparation Environnement (Jour 1)

### Étape 1.1 : Structure Projet

```bash
# Créer structure
mkdir -p api/{routes,models}
mkdir -p workers/{connectors,validators,transformers,enrichers}
mkdir -p ml/{models,training,inference}
mkdir -p alerts
mkdir -p scripts
mkdir -p tests/{unit,integration}
mkdir -p docs

# Fichiers configuration
touch .env.example
touch .env.production
touch requirements.txt
touch docker-compose-full.yml
touch README.md
```

**Résultat attendu :** Structure projet cohérente

### Étape 1.2 : Configuration Base

**Fichier `.env.example` :**
```bash
# Database
DB_HOST=timescaledb
DB_PORT=5432
DB_NAME=oceansentinelle
DB_USER=oceansentinel
DB_PASSWORD=CHANGE_ME

# API
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=CHANGE_ME

# External APIs
COAST_HF_API_URL=https://coastwatch.pfeg.noaa.gov/erddap
WEATHER_API_KEY=CHANGE_ME
TIDE_API_KEY=CHANGE_ME

# ML
ML_MODEL_PATH=/app/ml/models
ML_BATCH_SIZE=32

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=
```

**Résultat attendu :** Configuration centralisée

### Étape 1.3 : Dépendances Python

**Fichier `requirements.txt` :**
```txt
# API
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.25

# Data processing
pandas==2.1.4
numpy==1.24.3
xarray==2023.1.0
dask==2023.1.0
netCDF4==1.6.3

# ML
tensorflow==2.15.0
scikit-learn==1.3.2

# HTTP
requests==2.31.0
httpx==0.26.0

# Monitoring
python-dotenv==1.0.0
structlog==24.1.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
```

**Commande :**
```bash
pip install -r requirements.txt
```

**Résultat attendu :** Environnement Python prêt

---

## PHASE 2 : Base de Données (Jour 1-2)

### Étape 2.1 : Initialisation Tables

**Fichier déjà créé :** `scripts/init_pipeline_tables.sql`

**Commande d'exécution :**
```bash
# Local
docker exec -i oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle < scripts/init_pipeline_tables.sql

# VPS
ssh root@76.13.43.3
psql -U oceansentinel -d oceansentinelle -f /opt/oceansentinel/scripts/init_pipeline_tables.sql
```

**Vérification :**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

**Résultat attendu :** 11 tables créées

### Étape 2.2 : Seed Data (Optionnel)

**Fichier `scripts/seed_data.py` :**
```python
#!/usr/bin/env python3
"""Génère données de test."""
import psycopg2
from datetime import datetime, timedelta
import random

DB_CONFIG = {...}

def seed_test_data():
    """Insère données de test."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Insérer station test
    cursor.execute("""
        INSERT INTO stations (station_id, name, latitude, longitude)
        VALUES ('TEST_001', 'Station Test Arcachon', 44.666, -1.25)
        ON CONFLICT DO NOTHING;
    """)
    
    # Insérer mesures test (7 derniers jours)
    for i in range(7 * 24 * 6):  # 6 mesures/heure
        timestamp = datetime.utcnow() - timedelta(minutes=i*10)
        
        cursor.execute("""
            INSERT INTO validated_measurements (
                station_id, timestamp_utc, variable, value, unit,
                quality_score, validation_status, data_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            'TEST_001',
            timestamp,
            'temperature',
            15.0 + random.gauss(0, 2),
            '°C',
            0.95,
            'valid',
            'measured'
        ))
    
    conn.commit()
    print(f"✅ {7*24*6} mesures test insérées")

if __name__ == "__main__":
    seed_test_data()
```

**Résultat attendu :** Données test disponibles

---

## PHASE 3 : Connecteurs Sources (Jour 2-3)

### Étape 3.1 : Connecteur Base

**Fichier `workers/connectors/base.py` :**
```python
from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseConnector(ABC):
    """Connecteur API de base."""
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OceanSentinel/3.0'
        })
    
    @abstractmethod
    def fetch_data(self, start_time, end_time) -> List[Dict[str, Any]]:
        """Récupère données de la source."""
        pass
    
    def _make_request(self, url: str, params: dict = None, retries: int = 3):
        """Requête HTTP avec retry."""
        for attempt in range(retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == retries - 1:
                    raise
                logger.warning(f"Retry {attempt+1}/{retries}: {e}")
        
    def close(self):
        """Ferme la session."""
        self.session.close()
```

### Étape 3.2 : Connecteur COAST-HF

**Fichier `workers/connectors/coast_hf.py` :**
```python
from .base import BaseConnector
from datetime import datetime
import pandas as pd

class CoastHFConnector(BaseConnector):
    """Connecteur COAST-HF ERDDAP."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://coastwatch.pfeg.noaa.gov/erddap/tabledap')
        self.dataset_id = config.get('dataset_id', 'BARAG')
    
    def fetch_data(self, start_time: datetime, end_time: datetime):
        """Récupère données COAST-HF."""
        url = f"{self.base_url}/{self.dataset_id}.csv"
        
        params = {
            'time>=': start_time.isoformat() + 'Z',
            'time<=': end_time.isoformat() + 'Z',
        }
        
        response = self._make_request(url, params)
        
        # Parser CSV
        df = pd.read_csv(response.text, skiprows=[1])  # Skip units row
        
        # Convertir en liste de dicts
        measurements = []
        for _, row in df.iterrows():
            measurements.append({
                'station_id': 'BARAG',
                'timestamp_utc': pd.to_datetime(row['time']),
                'variable': 'temperature',
                'raw_value': row['temperature_water'],
                'raw_unit': '°C',
                'source_name': 'COAST-HF'
            })
        
        return measurements
```

**Résultat attendu :** Connecteur fonctionnel

### Étape 3.3 : Tests Connecteurs

**Fichier `tests/test_connectors.py` :**
```python
import pytest
from workers.connectors.coast_hf import CoastHFConnector
from datetime import datetime, timedelta

def test_coast_hf_connector():
    """Test connecteur COAST-HF."""
    config = {'base_url': '...', 'dataset_id': 'BARAG'}
    connector = CoastHFConnector(config)
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    data = connector.fetch_data(start_time, end_time)
    
    assert len(data) > 0
    assert 'station_id' in data[0]
    assert 'timestamp_utc' in data[0]
    
    connector.close()
```

**Commande :**
```bash
pytest tests/test_connectors.py -v
```

**Résultat attendu :** Tests passent

---

## PHASE 4 : Orchestrateur Ingestion (Jour 3-4)

### Étape 4.1 : Orchestrateur

**Fichier déjà créé :** `scripts/ingestion_orchestrator.py`

**Améliorations à apporter :**

1. Implémenter `fetch_coast_hf_data()`
2. Implémenter `fetch_weather_data()`
3. Implémenter `fetch_tide_data()`
4. Ajouter gestion watermark (dernière collecte)
5. Ajouter métriques Prometheus (optionnel)

### Étape 4.2 : Planification Cron

**Fichier `scripts/cron_ingestion.sh` :**
```bash
#!/bin/bash
# Ingestion toutes les 10 minutes

cd /opt/oceansentinel
source venv/bin/activate
python3 scripts/ingestion_orchestrator.py >> /var/log/oceansentinel/ingestion.log 2>&1
```

**Crontab :**
```bash
# Ingestion toutes les 10 min
*/10 * * * * /opt/oceansentinel/scripts/cron_ingestion.sh

# Rafraîchissement vue matérialisée toutes les heures
0 * * * * psql -U oceansentinel -d oceansentinelle -c "REFRESH MATERIALIZED VIEW CONCURRENTLY latest_metrics;"
```

**Résultat attendu :** Ingestion automatisée

---

## PHASE 5 : API Backend (Jour 4-5)

### Étape 5.1 : Point d'Entrée API

**Fichier `api/main.py` (déjà existant, à enrichir) :**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routes import stations, metrics, alerts, forecast, quality
from .database import init_db_pool, close_db_pool
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ocean Sentinel API",
    version="3.0.0",
    description="API REST pour surveillance océanographique"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifecycle
@app.on_event("startup")
async def startup():
    """Initialisation au démarrage."""
    logger.info("🚀 Démarrage Ocean Sentinel API v3.0")
    await init_db_pool()

@app.on_event("shutdown")
async def shutdown():
    """Nettoyage à l'arrêt."""
    logger.info("🛑 Arrêt Ocean Sentinel API")
    await close_db_pool()

# Routes
app.include_router(stations.router, prefix="/api/v1", tags=["stations"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(forecast.router, prefix="/api/v1", tags=["forecast"])
app.include_router(quality.router, prefix="/api/v1", tags=["quality"])

# Health check
@app.get("/health")
async def health_check():
    """Vérification santé API."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Étape 5.2 : Routes Stations

**Fichier `api/routes/stations.py` :**
```python
from fastapi import APIRouter, HTTPException
from typing import List
from ..database import get_db_connection
from ..models import Station

router = APIRouter()

@router.get("/stations", response_model=List[Station])
async def list_stations():
    """Liste toutes les stations."""
    conn = await get_db_connection()
    
    query = """
        SELECT 
            station_id,
            MAX(timestamp_utc) as last_measurement,
            COUNT(DISTINCT variable) as variables_count,
            AVG(quality_score) as avg_quality
        FROM validated_measurements
        WHERE timestamp_utc > NOW() - INTERVAL '7 days'
        GROUP BY station_id
    """
    
    results = await conn.fetch(query)
    return [dict(r) for r in results]

@router.get("/stations/{station_id}")
async def get_station(station_id: str):
    """Détails d'une station."""
    conn = await get_db_connection()
    
    query = """
        SELECT * FROM stations_status
        WHERE station_id = $1
    """
    
    result = await conn.fetchrow(query, station_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Station not found")
    
    return dict(result)
```

### Étape 5.3 : Routes Metrics

**Fichier `api/routes/metrics.py` :**
```python
from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from ..database import get_db_connection

router = APIRouter()

@router.get("/metrics/latest")
async def get_latest_metrics():
    """Dernières mesures toutes stations."""
    conn = await get_db_connection()
    
    query = "SELECT * FROM latest_metrics ORDER BY station_id, variable"
    results = await conn.fetch(query)
    
    return [dict(r) for r in results]

@router.get("/metrics/latest/{station_id}")
async def get_latest_station_metrics(station_id: str):
    """Dernières mesures d'une station."""
    conn = await get_db_connection()
    
    query = """
        SELECT * FROM latest_metrics
        WHERE station_id = $1
        ORDER BY variable
    """
    
    results = await conn.fetch(query, station_id)
    return [dict(r) for r in results]

@router.get("/metrics/history")
async def get_history(
    station_id: str = Query(...),
    variable: str = Query(...),
    start_time: datetime = Query(None),
    end_time: datetime = Query(None),
    limit: int = Query(1000, le=10000)
):
    """Historique mesures."""
    conn = await get_db_connection()
    
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=7)
    if not end_time:
        end_time = datetime.utcnow()
    
    query = """
        SELECT timestamp_utc, value, unit, quality_score
        FROM validated_measurements
        WHERE station_id = $1
          AND variable = $2
          AND timestamp_utc BETWEEN $3 AND $4
        ORDER BY timestamp_utc DESC
        LIMIT $5
    """
    
    results = await conn.fetch(query, station_id, variable, start_time, end_time, limit)
    return [dict(r) for r in results]
```

**Résultat attendu :** API fonctionnelle

---

## PHASE 6 : Alertes SACS (Jour 5-6)

### Étape 6.1 : Moteur Alertes

**Fichier `alerts/engine.py` :**
```python
import psycopg2
from datetime import datetime
from .rules import SACS_RULES
import logging

logger = logging.getLogger(__name__)

class AlertEngine:
    """Moteur d'évaluation des alertes SACS."""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
    
    def check_station_alerts(self, station_id: str):
        """Vérifie les alertes pour une station."""
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Récupérer dernières mesures
        cursor.execute("""
            SELECT variable, value, unit, timestamp_utc
            FROM latest_metrics
            WHERE station_id = %s
        """, (station_id,))
        
        metrics = {row[0]: {'value': row[1], 'unit': row[2], 'time': row[3]} 
                   for row in cursor.fetchall()}
        
        # Évaluer chaque règle
        for rule in SACS_RULES:
            if rule.evaluate(metrics):
                self._trigger_alert(
                    station_id,
                    rule.alert_type,
                    rule.severity,
                    rule.confidence,
                    metrics
                )
        
        cursor.close()
        conn.close()
    
    def _trigger_alert(self, station_id, alert_type, severity, confidence, evidence):
        """Déclenche une alerte."""
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts (
                station_id, alert_type, severity,
                triggered_at, confidence, evidence
            ) VALUES (%s, %s, %s, %s, %s, %s::jsonb)
        """, (
            station_id,
            alert_type,
            severity,
            datetime.utcnow(),
            confidence,
            json.dumps(evidence)
        ))
        
        conn.commit()
        logger.warning(f"🚨 Alerte {alert_type} déclenchée pour {station_id}")
```

**Résultat attendu :** Alertes fonctionnelles

---

## PHASE 7 : ML Engine (Jour 6-7)

### Étape 7.1 : Prédictions LSTM

**Fichier `ml/inference.py` :**
```python
import tensorflow as tf
import numpy as np
from datetime import datetime, timedelta

class ForecastEngine:
    """Moteur de prédictions LSTM."""
    
    def __init__(self, model_path: str):
        self.model = tf.keras.models.load_model(model_path)
    
    def predict(self, station_id: str, variable: str, horizon_hours: int = 12):
        """Génère prévision."""
        # 1. Récupérer historique
        history = self._fetch_history(station_id, variable, lookback=168)  # 7 jours
        
        # 2. Préparer features
        X = self._prepare_features(history)
        
        # 3. Prédire
        predictions = self.model.predict(X)
        
        # 4. Post-traiter
        forecast = self._postprocess(predictions, horizon_hours)
        
        return forecast
```

**Résultat attendu :** Prévisions disponibles

---

# D. Structure Projet Recommandée

```
ocean-sentinel/
├── .env.example
├── .env.production
├── .gitignore
├── README.md
├── requirements.txt
├── docker-compose.yml
├── docker-compose-full.yml
├── Dockerfile.api
├── Dockerfile.ingestion
├── Dockerfile.ml
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── station.py
│   │   ├── measurement.py
│   │   ├── alert.py
│   │   └── forecast.py
│   └── routes/
│       ├── __init__.py
│       ├── stations.py
│       ├── metrics.py
│       ├── alerts.py
│       ├── forecast.py
│       └── quality.py
│
├── workers/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── coast_hf.py
│   │   ├── weather.py
│   │   ├── tide.py
│   │   └── sentinel3.py
│   ├── validators/
│   │   ├── __init__.py
│   │   └── schema_validator.py
│   ├── transformers/
│   │   ├── __init__.py
│   │   ├── unit_normalizer.py
│   │   └── quality_scorer.py
│   └── enrichers/
│       ├── __init__.py
│       └── context_enricher.py
│
├── ml/
│   ├── __init__.py
│   ├── models/
│   │   └── lstm_temperature.h5
│   ├── training.py
│   ├── inference.py
│   └── features.py
│
├── alerts/
│   ├── __init__.py
│   ├── engine.py
│   ├── rules.py
│   └── notifications.py
│
├── scripts/
│   ├── init_pipeline_tables.sql
│   ├── ingestion_orchestrator.py
│   ├── ingestion_sentinel3_optimized.py
│   ├── cron_ingestion.sh
│   ├── migrate.py
│   └── seed_data.py
│
├── tests/
│   ├── unit/
│   │   ├── test_connectors.py
│   │   ├── test_validators.py
│   │   └── test_transformers.py
│   └── integration/
│       ├── test_api.py
│       └── test_pipeline.py
│
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
│
└── grafana/
    └── provisioning/
        ├── datasources/
        └── dashboards/
```

---

# E. Schéma de Données et Endpoints

## Tables Principales

Voir `scripts/init_pipeline_tables.sql` pour le schéma complet.

### Résumé Tables

| Table | Type | Rôle |
|-------|------|------|
| `raw_ingestion_log` | Audit | Journal ingestions |
| `raw_measurements` | Raw | Payload JSON brut |
| `validated_measurements` | Processed | Données normalisées |
| `derived_metrics` | Processed | Métriques calculées |
| `latest_metrics` | Serving | Vue matérialisée |
| `hourly_aggregates` | Serving | Agrégats continus |
| `alerts` | Serving | Alertes actives |
| `forecast_predictions` | Serving | Prévisions IA |
| `data_quality_reports` | Serving | Rapports qualité |

## Endpoints API Complets

### Stations
```
GET  /api/v1/stations
GET  /api/v1/stations/{station_id}
GET  /api/v1/stations/{station_id}/status
```

### Metrics
```
GET  /api/v1/metrics/latest
GET  /api/v1/metrics/latest/{station_id}
GET  /api/v1/metrics/history?station_id=X&variable=Y&start=Z&end=W
GET  /api/v1/metrics/{station_id}/{variable}
```

### Alerts
```
GET  /api/v1/alerts
GET  /api/v1/alerts/{alert_id}
GET  /api/v1/alerts/station/{station_id}
POST /api/v1/alerts/{alert_id}/resolve
GET  /api/v1/alerts/active
```

### Forecast
```
GET  /api/v1/forecast/{station_id}?variable=X&horizon=12h
GET  /api/v1/forecast/{station_id}?variable=X&horizon=24h
GET  /api/v1/forecast/models
```

### Quality
```
GET  /api/v1/quality/station/{station_id}
GET  /api/v1/quality/reports
GET  /api/v1/quality/anomalies
```

### System
```
GET  /health
GET  /api/v1/system/stats
```

---

# F. Mise en Service

## Docker Compose Complet

**Fichier `docker-compose-full.yml` :**

```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: oceansentinel_timescaledb
    environment:
      POSTGRES_DB: oceansentinelle
      POSTGRES_USER: oceansentinel
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - timescale_data:/var/lib/postgresql/data
      - ./scripts/init_pipeline_tables.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "6543:5432"
    mem_limit: 256m
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: oceansentinel_api
    environment:
      DB_HOST: timescaledb
      DB_PORT: 5432
      DB_NAME: oceansentinelle
      DB_USER: oceansentinel
      DB_PASSWORD: ${DB_PASSWORD}
      API_SECRET_KEY: ${API_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - timescaledb
    mem_limit: 256m
    restart: unless-stopped

  ingestion:
    build:
      context: .
      dockerfile: Dockerfile.ingestion
    container_name: oceansentinel_ingestion
    environment:
      DB_HOST: timescaledb
      DB_PORT: 5432
      DB_NAME: oceansentinelle
      DB_USER: oceansentinel
      DB_PASSWORD: ${DB_PASSWORD}
      COAST_HF_API_URL: ${COAST_HF_API_URL}
      WEATHER_API_KEY: ${WEATHER_API_KEY}
    depends_on:
      - timescaledb
    mem_limit: 256m
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: oceansentinel_grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
      GF_INSTALL_PLUGINS: ""
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"
    depends_on:
      - timescaledb
    mem_limit: 128m
    restart: unless-stopped

volumes:
  timescale_data:
  grafana_data:
```

## Dockerfiles

### Dockerfile.api

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code application
COPY api/ ./api/
COPY workers/ ./workers/
COPY alerts/ ./alerts/

# Port
EXPOSE 8000

# Commande
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile.ingestion

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY workers/ ./workers/
COPY scripts/ ./scripts/

# Cron job
COPY scripts/cron_ingestion.sh /etc/cron.d/ingestion
RUN chmod 0644 /etc/cron.d/ingestion
RUN crontab /etc/cron.d/ingestion

CMD ["cron", "-f"]
```

## Commandes Déploiement

### Local

```bash
# 1. Copier .env
cp .env.example .env
# Éditer .env avec vos valeurs

# 2. Build
docker-compose -f docker-compose-full.yml build

# 3. Démarrer
docker-compose -f docker-compose-full.yml up -d

# 4. Vérifier
docker-compose -f docker-compose-full.yml ps
docker-compose -f docker-compose-full.yml logs -f

# 5. Tester API
curl http://localhost:8000/health
```

### VPS Production

```bash
# 1. Transférer fichiers
rsync -avz --exclude='*.pyc' --exclude='__pycache__' \
  . root@76.13.43.3:/opt/oceansentinel/

# 2. SSH VPS
ssh root@76.13.43.3

# 3. Configuration
cd /opt/oceansentinel
cp .env.example .env.production
nano .env.production  # Éditer

# 4. Build et démarrage
docker-compose -f docker-compose-full.yml --env-file .env.production build
docker-compose -f docker-compose-full.yml --env-file .env.production up -d

# 5. Vérification
docker-compose -f docker-compose-full.yml ps
curl http://localhost:8000/health
curl http://76.13.43.3:8000/api/v1/stations

# 6. Logs
docker-compose -f docker-compose-full.yml logs -f api
```

---

# G. Exploitation et Maintenance

## Monitoring

### Logs Centralisés

```bash
# Tous les services
docker-compose -f docker-compose-full.yml logs -f

# Service spécifique
docker-compose -f docker-compose-full.yml logs -f api
docker-compose -f docker-compose-full.yml logs -f ingestion

# Dernières 100 lignes
docker-compose -f docker-compose-full.yml logs --tail=100 api
```

### Métriques Système

```bash
# Utilisation ressources
docker stats

# Espace disque
df -h
du -sh /var/lib/docker/volumes/*

# Mémoire TimescaleDB
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT 
    pg_size_pretty(pg_database_size('oceansentinelle')) as db_size,
    pg_size_pretty(pg_total_relation_size('validated_measurements')) as validated_size,
    pg_size_pretty(pg_total_relation_size('raw_measurements')) as raw_size;
"
```

## Alertes Techniques

**Fichier `scripts/health_check.sh` :**
```bash
#!/bin/bash
# Vérification santé système

# API
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ API DOWN" | mail -s "Ocean Sentinel Alert" admin@example.com
fi

# Database
if ! docker exec oceansentinel_timescaledb pg_isready -U oceansentinel; then
    echo "❌ DATABASE DOWN" | mail -s "Ocean Sentinel Alert" admin@example.com
fi

# Disk space
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️ DISK USAGE: ${DISK_USAGE}%" | mail -s "Ocean Sentinel Alert" admin@example.com
fi
```

**Cron:**
```bash
*/5 * * * * /opt/oceansentinel/scripts/health_check.sh
```

## Rotation Logs

**Fichier `/etc/logrotate.d/oceansentinel` :**
```
/var/log/oceansentinel/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
```

## Backup Base de Données

```bash
# Backup quotidien
0 2 * * * docker exec oceansentinel_timescaledb pg_dump -U oceansentinel -Fc oceansentinelle > /backups/oceansentinel_$(date +\%Y\%m\%d).dump

# Rétention 30 jours
find /backups -name "oceansentinel_*.dump" -mtime +30 -delete
```

## Reprise sur Incident

### Redémarrage Services

```bash
# Redémarrer tout
docker-compose -f docker-compose-full.yml restart

# Redémarrer service spécifique
docker-compose -f docker-compose-full.yml restart api

# Rebuild et redémarrer
docker-compose -f docker-compose-full.yml build api
docker-compose -f docker-compose-full.yml up -d api
```

### Restauration Base

```bash
# Arrêter services
docker-compose -f docker-compose-full.yml stop api ingestion

# Restaurer
docker exec -i oceansentinel_timescaledb pg_restore -U oceansentinel -d oceansentinelle -c < /backups/oceansentinel_20260417.dump

# Redémarrer
docker-compose -f docker-compose-full.yml start api ingestion
```

---

# H. Checklist Finale Mise en Production

## Pré-Déploiement

- [ ] Code versionné (Git)
- [ ] Tests unitaires passent
- [ ] Tests intégration passent
- [ ] Documentation à jour
- [ ] Secrets configurés (.env.production)
- [ ] Backup base de données existante
- [ ] Plan rollback défini

## Infrastructure

- [ ] VPS accessible (SSH)
- [ ] Docker installé
- [ ] Docker Compose installé
- [ ] Ports ouverts (8000, 3000, 6543)
- [ ] Firewall configuré (UFW)
- [ ] Certificats SSL (optionnel)
- [ ] Nom de domaine configuré (optionnel)

## Base de Données

- [ ] Tables créées (init_pipeline_tables.sql)
- [ ] Hypertables configurées
- [ ] Continuous aggregates actifs
- [ ] Politiques rétention activées
- [ ] Politiques compression activées
- [ ] Index créés
- [ ] Permissions configurées

## Services

- [ ] API démarre sans erreur
- [ ] Ingestion démarre sans erreur
- [ ] Grafana accessible
- [ ] TimescaleDB accessible
- [ ] Health check API répond
- [ ] Logs visibles

## Fonctionnel

- [ ] Endpoint /health répond
- [ ] Endpoint /api/v1/stations répond
- [ ] Endpoint /api/v1/metrics/latest répond
- [ ] Grafana affiche données
- [ ] Ingestion insère données
- [ ] Alertes se déclenchent
- [ ] Prévisions générées (si ML actif)

## Monitoring

- [ ] Logs centralisés configurés
- [ ] Rotation logs active
- [ ] Health checks automatiques
- [ ] Alertes email configurées
- [ ] Métriques système surveillées
- [ ] Backup automatique actif

## Documentation

- [ ] README à jour
- [ ] API documentée (Swagger)
- [ ] Procédures déploiement
- [ ] Procédures rollback
- [ ] Procédures troubleshooting
- [ ] Contacts support

---

# BONUS 1 : Checklist Smoke Test

```bash
#!/bin/bash
# Smoke test post-déploiement

echo "🧪 SMOKE TEST OCEAN SENTINEL V3.0"
echo "=================================="

# 1. Health check API
echo -n "1. API Health Check... "
if curl -f http://76.13.43.3:8000/health > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    exit 1
fi

# 2. Database connection
echo -n "2. Database Connection... "
if docker exec oceansentinel_timescaledb pg_isready -U oceansentinel > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    exit 1
fi

# 3. Stations endpoint
echo -n "3. Stations Endpoint... "
if curl -f http://76.13.43.3:8000/api/v1/stations > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    exit 1
fi

# 4. Latest metrics
echo -n "4. Latest Metrics... "
if curl -f http://76.13.43.3:8000/api/v1/metrics/latest > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    exit 1
fi

# 5. Grafana
echo -n "5. Grafana... "
if curl -f http://76.13.43.3:3000 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    exit 1
fi

# 6. Data in database
echo -n "6. Data in Database... "
COUNT=$(docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -t -c "SELECT COUNT(*) FROM validated_measurements;")
if [ $COUNT -gt 0 ]; then
    echo "✅ OK ($COUNT records)"
else
    echo "❌ FAIL (no data)"
    exit 1
fi

echo ""
echo "✅ ALL TESTS PASSED"
```

---

# BONUS 2 : Erreurs Critiques à Éviter

## Erreurs de Conception

1. ❌ **Mélanger raw et validated dans même table**
   - ✅ Toujours séparer 3 couches

2. ❌ **Ne pas conserver payload source**
   - ✅ Toujours garder raw_measurements

3. ❌ **Timestamps sans UTC**
   - ✅ Toujours UTC + conversion frontend

4. ❌ **Pas de versioning transformations**
   - ✅ Tracer version règles/modèles

5. ❌ **IA sur données non validées**
   - ✅ Toujours validated_measurements pour ML

## Erreurs Techniques

6. ❌ **Pas de timeout HTTP**
   - ✅ Timeout 30s minimum

7. ❌ **Pas de retry**
   - ✅ 3 tentatives avec backoff

8. ❌ **Secrets en dur**
   - ✅ Variables d'environnement

9. ❌ **Collecte non incrémentale**
   - ✅ Watermark + déduplication

10. ❌ **Pas de monitoring**
    - ✅ Logs + health checks

## Erreurs Métier

11. ❌ **Données imputées pour alertes critiques**
    - ✅ Seulement mesures validées

12. ❌ **Ignorer dérives capteur**
    - ✅ Score qualité + anomaly_flag

13. ❌ **Confondre disponible et fiable**
    - ✅ quality_score < 0.7 = suspect

14. ❌ **Pas de journalisation anomalies**
    - ✅ Table data_quality_reports

15. ❌ **Mélanger monitoring/alerte/prédiction**
    - ✅ Séparer clairement les usages

---

# BONUS 3 : Ordre de Mission Équipe Dev

## MISSION : Mise en Service Pipeline API Ocean Sentinel V3.0

**Deadline :** 7 jours  
**Équipe :** 2-3 développeurs  
**Priorité :** HAUTE

### Jour 1-2 : Infrastructure
- [ ] Setup environnement (Docker, PostgreSQL)
- [ ] Initialiser base de données (init_pipeline_tables.sql)
- [ ] Tester connexions

### Jour 3-4 : Backend API
- [ ] Implémenter routes FastAPI
- [ ] Tester endpoints
- [ ] Documenter API (Swagger)

### Jour 5-6 : Ingestion
- [ ] Implémenter connecteurs sources
- [ ] Tester orchestrateur
- [ ] Configurer cron

### Jour 7 : Déploiement
- [ ] Build images Docker
- [ ] Déployer VPS
- [ ] Smoke tests
- [ ] Go/No-Go

### Critères de Succès
- ✅ API répond sur VPS
- ✅ Grafana affiche données
- ✅ Ingestion automatique fonctionne
- ✅ Alertes se déclenchent
- ✅ Documentation complète

---

**🌊 Ocean Sentinel V3.0 - Ready for Production Deployment**
