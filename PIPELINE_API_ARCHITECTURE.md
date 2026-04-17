# 🌊 Ocean Sentinel V3.0 - Architecture Pipeline API

## Vue d'Ensemble

Ce document décrit l'architecture complète du pipeline API d'Ocean Sentinel V3.0, conforme aux spécifications du cahier des charges technique.

---

## 📊 Architecture en 3 Couches

```
┌─────────────────────────────────────────────────────────────────┐
│                     SOURCES DE DONNÉES                          │
├─────────────────────────────────────────────────────────────────┤
│  Capteurs Marins  │  API Météo  │  API Marée  │  Sentinel-3   │
│   (COAST-HF)      │  (OpenWeather)│ (SHOM)     │  (Copernicus) │
└──────────┬────────┴──────┬───────┴──────┬──────┴───────┬────────┘
           │               │              │              │
           v               v              v              v
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE INGESTION                             │
├─────────────────────────────────────────────────────────────────┤
│  • Connecteurs spécialisés (Python)                             │
│  • Authentification sécurisée (secrets manager)                 │
│  • Retry + Timeout + Circuit breaker                            │
│  • Collecte incrémentale (watermark)                            │
│  • Journalisation technique                                     │
└──────────┬──────────────────────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────────────────────┐
│                    RAW LAYER (Brut)                             │
├─────────────────────────────────────────────────────────────────┤
│  TimescaleDB: raw_measurements                                  │
│  • Payload JSON complet                                         │
│  • Horodatage ingestion                                         │
│  • Checksum                                                     │
│  • Aucune transformation                                        │
└──────────┬──────────────────────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────────────────────┐
│              COUCHE TRANSFORMATION (QA/QC)                      │
├─────────────────────────────────────────────────────────────────┤
│  • Validation schéma (Pydantic)                                 │
│  • Normalisation unités                                         │
│  • Déduplication (station_id + timestamp)                       │
│  • Contrôles physiques (plages plausibles)                      │
│  • Enrichissement (météo + marée)                               │
│  • Calcul métriques dérivées                                    │
│  • Score qualité                                                │
└──────────┬──────────────────────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────────────────────┐
│                 PROCESSED LAYER (Validé)                        │
├─────────────────────────────────────────────────────────────────┤
│  TimescaleDB: validated_measurements                            │
│  • Données normalisées                                          │
│  • Unités canoniques                                            │
│  • Quality flags                                                │
│  • Métadonnées SACS                                             │
└──────────┬──────────────────────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE INTELLIGENCE                          │
├─────────────────────────────────────────────────────────────────┤
│  Moteur Alertes  │  Moteur ML  │  Métriques Dérivées           │
│  (SACS Rules)    │  (LSTM)     │  (Variations, Tendances)      │
└──────────┬───────┴──────┬──────┴───────┬─────────────────────────┘
           │              │              │
           v              v              v
┌─────────────────────────────────────────────────────────────────┐
│                   SERVING LAYER (Métier)                        │
├─────────────────────────────────────────────────────────────────┤
│  • latest_metrics (vue matérialisée)                            │
│  • alerts (table événements)                                    │
│  • forecasts (prédictions)                                      │
│  • quality_reports (audit)                                      │
└──────────┬──────────────────────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────────────────────┐
│                      API MÉTIER (FastAPI)                       │
├─────────────────────────────────────────────────────────────────┤
│  /api/v1/stations        │  /api/v1/alerts                      │
│  /api/v1/metrics/latest  │  /api/v1/forecast                    │
│  /api/v1/quality         │  /api/v1/exports                     │
└──────────┬──────────────────────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────────────────────┐
│                  CLIENTS (Frontend, Mobile, IA)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Schéma Base de Données

### **1. RAW LAYER**

```sql
-- Table d'audit ingestion
CREATE TABLE raw_ingestion_log (
    ingestion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL, -- 'success', 'partial', 'failed'
    records_fetched INTEGER,
    records_rejected INTEGER,
    payload_path TEXT,
    checksum TEXT,
    error_message TEXT,
    execution_time_ms INTEGER
);

-- Table données brutes
CREATE TABLE raw_measurements (
    raw_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ingestion_id UUID REFERENCES raw_ingestion_log(ingestion_id),
    station_id TEXT NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    source_name TEXT NOT NULL,
    payload JSONB NOT NULL, -- Payload complet non modifié
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_raw_measurements_station_time 
ON raw_measurements (station_id, timestamp_utc DESC);

CREATE INDEX idx_raw_measurements_source 
ON raw_measurements (source_name, timestamp_utc DESC);
```

### **2. PROCESSED LAYER**

```sql
-- Table mesures validées (existante, enrichie)
CREATE TABLE validated_measurements (
    measurement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_id UUID REFERENCES raw_measurements(raw_id),
    station_id TEXT NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    variable TEXT NOT NULL, -- 'temperature', 'ph', 'salinity', etc.
    value DOUBLE PRECISION NOT NULL,
    unit TEXT NOT NULL,
    quality_score DOUBLE PRECISION, -- 0.0 - 1.0
    validation_status TEXT, -- 'valid', 'suspect', 'invalid'
    anomaly_flag BOOLEAN DEFAULT FALSE,
    data_source TEXT,
    data_status TEXT, -- 'measured', 'inferred', 'interpolated'
    metadata JSONB,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (station_id, timestamp_utc, variable)
);

SELECT create_hypertable('validated_measurements', 'timestamp_utc');

CREATE INDEX idx_validated_station_var_time 
ON validated_measurements (station_id, variable, timestamp_utc DESC);

CREATE INDEX idx_validated_quality 
ON validated_measurements (quality_score, timestamp_utc DESC) 
WHERE quality_score < 0.7;
```

### **3. DERIVED METRICS**

```sql
-- Métriques calculées
CREATE TABLE derived_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id TEXT NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    metric_name TEXT NOT NULL, -- 'ph_variation_12h', 'oxygen_slope', etc.
    metric_value DOUBLE PRECISION NOT NULL,
    metric_unit TEXT,
    calculation_version TEXT,
    metadata JSONB,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (station_id, timestamp_utc, metric_name)
);

SELECT create_hypertable('derived_metrics', 'timestamp_utc');
```

### **4. SERVING LAYER**

```sql
-- Vue matérialisée: dernières mesures
CREATE MATERIALIZED VIEW latest_metrics AS
SELECT DISTINCT ON (station_id, variable)
    station_id,
    variable,
    value,
    unit,
    quality_score,
    timestamp_utc,
    data_status
FROM validated_measurements
ORDER BY station_id, variable, timestamp_utc DESC;

CREATE UNIQUE INDEX idx_latest_metrics_station_var 
ON latest_metrics (station_id, variable);

-- Rafraîchissement automatique (TimescaleDB continuous aggregate)
CREATE MATERIALIZED VIEW hourly_aggregates
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp_utc) AS bucket,
    station_id,
    variable,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    STDDEV(value) as stddev_value,
    COUNT(*) as sample_count
FROM validated_measurements
GROUP BY bucket, station_id, variable;

-- Table alertes
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id TEXT NOT NULL,
    zone_id TEXT,
    alert_type TEXT NOT NULL, -- 'HYPOXIA_RISK', 'PH_ANOMALY', etc.
    severity TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
    triggered_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active', -- 'active', 'resolved', 'dismissed'
    confidence DOUBLE PRECISION,
    evidence JSONB,
    action_recommended TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_station_time 
ON alerts (station_id, triggered_at DESC);

CREATE INDEX idx_alerts_status 
ON alerts (status, severity, triggered_at DESC);

-- Table prévisions
CREATE TABLE forecast_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id TEXT NOT NULL,
    variable TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL,
    forecast_timestamp TIMESTAMPTZ NOT NULL, -- Quand la prédiction s'applique
    horizon_hours INTEGER NOT NULL, -- 12, 24, 48
    predicted_value DOUBLE PRECISION NOT NULL,
    confidence_lower DOUBLE PRECISION,
    confidence_upper DOUBLE PRECISION,
    model_version TEXT NOT NULL,
    model_type TEXT, -- 'LSTM', 'ARIMA', 'ensemble'
    metadata JSONB
);

CREATE INDEX idx_forecast_station_time 
ON forecast_predictions (station_id, forecast_timestamp DESC);

-- Table rapports qualité
CREATE TABLE data_quality_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id TEXT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    completeness_rate DOUBLE PRECISION, -- % données présentes
    anomaly_rate DOUBLE PRECISION, -- % anomalies détectées
    latency_avg_minutes INTEGER, -- Latence moyenne ingestion
    final_quality_score DOUBLE PRECISION, -- Score global 0-1
    details JSONB,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 🔌 Connecteurs API

### **Structure Connecteur Type**

Chaque connecteur suit ce pattern :

```python
class BaseConnector:
    """Connecteur API de base."""
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.last_fetch_timestamp = None
        
    def authenticate(self):
        """Authentification API."""
        pass
        
    def fetch_data(self, start_time: datetime, end_time: datetime):
        """Récupération données avec retry."""
        pass
        
    def validate_response(self, response):
        """Validation réponse API."""
        pass
        
    def save_raw(self, data: dict):
        """Sauvegarde raw layer."""
        pass
```

---

## 📋 Endpoints API Métier

### **Base URL:** `/api/v1`

#### **Stations**
- `GET /stations` - Liste stations
- `GET /stations/{station_id}` - Détails station
- `GET /stations/{station_id}/status` - Statut temps réel

#### **Mesures**
- `GET /metrics/latest` - Dernières mesures toutes stations
- `GET /metrics/latest/{station_id}` - Dernières mesures station
- `GET /metrics/history` - Historique avec filtres
- `GET /metrics/{station_id}/{variable}` - Série temporelle

#### **Qualité**
- `GET /quality/station/{station_id}` - Rapport qualité station
- `GET /quality/reports` - Liste rapports qualité
- `GET /quality/anomalies` - Anomalies détectées

#### **Alertes**
- `GET /alerts` - Liste alertes actives
- `GET /alerts/{alert_id}` - Détail alerte
- `GET /alerts/station/{station_id}` - Alertes par station
- `POST /alerts/{alert_id}/resolve` - Résoudre alerte

#### **Prévisions**
- `GET /forecast/{station_id}?horizon=12h` - Prévision 12h
- `GET /forecast/{station_id}?horizon=24h` - Prévision 24h
- `GET /forecast/models` - Liste modèles disponibles

#### **Exports**
- `GET /exports/data?format=csv` - Export CSV
- `GET /exports/data?format=parquet` - Export Parquet
- `GET /exports/quality-report` - Rapport qualité PDF

---

## 🔄 Flux de Traitement

### **1. Ingestion (toutes les 10 min)**

```python
# scripts/ingestion_orchestrator.py
async def ingest_all_sources():
    """Orchestrateur ingestion multi-sources."""
    
    # Capteurs marins
    await ingest_coast_hf()
    
    # Météo (toutes les 30 min)
    if should_fetch_weather():
        await ingest_weather()
    
    # Marée (toutes les 60 min)
    if should_fetch_tide():
        await ingest_tide()
    
    # Sentinel-3 (quotidien)
    if should_fetch_satellite():
        await ingest_sentinel3()
```

### **2. Validation (immédiate)**

```python
# scripts/data_validator.py
def validate_measurement(raw_data: dict) -> dict:
    """Validation et normalisation."""
    
    # 1. Validation schéma
    validated = MeasurementSchema(**raw_data)
    
    # 2. Normalisation unités
    normalized = normalize_units(validated)
    
    # 3. Contrôles physiques
    quality_score = check_physical_bounds(normalized)
    
    # 4. Détection anomalies
    anomaly_flag = detect_anomaly(normalized)
    
    return {
        **normalized,
        'quality_score': quality_score,
        'anomaly_flag': anomaly_flag
    }
```

### **3. Enrichissement (après validation)**

```python
# scripts/data_enrichment.py
def enrich_measurement(measurement: dict) -> dict:
    """Enrichissement avec contexte."""
    
    # Récupérer météo contemporaine
    weather = get_weather_at_time(
        measurement['timestamp_utc']
    )
    
    # Récupérer marée
    tide = get_tide_at_time(
        measurement['timestamp_utc']
    )
    
    # Calculer métriques dérivées
    derived = calculate_derived_metrics(
        measurement,
        weather,
        tide
    )
    
    return {
        **measurement,
        'weather_context': weather,
        'tide_context': tide,
        'derived_metrics': derived
    }
```

### **4. Alertes (temps réel)**

```python
# scripts/alert_engine.py
def check_alerts(station_id: str):
    """Vérification règles d'alerte."""
    
    # Récupérer dernières mesures
    metrics = get_latest_metrics(station_id)
    
    # Règle SACS: Hypoxie
    if metrics['dissolved_oxygen'] < 4.0:
        trigger_alert(
            station_id=station_id,
            alert_type='HYPOXIA_RISK',
            severity='high',
            evidence=metrics
        )
    
    # Règle SACS: pH anormal
    if metrics['ph'] < 7.8:
        trigger_alert(
            station_id=station_id,
            alert_type='PH_ANOMALY',
            severity='medium',
            evidence=metrics
        )
```

---

## 🎯 Checklist Mise en Production

### **Gouvernance**
- ✅ Inventaire sources validé
- ✅ Criticité flux définie
- ✅ Unités documentées
- ✅ Conventions timestamp UTC

### **Connexion**
- ✅ Authentification sécurisée (secrets manager)
- ✅ Retry configurés (3 tentatives, backoff exponentiel)
- ✅ Timeout configurés (30s)
- ✅ Collecte incrémentale (watermark)
- ✅ Journalisation active

### **Qualité**
- ✅ Validation schéma (Pydantic)
- ✅ Gestion valeurs nulles
- ✅ Déduplication (station_id + timestamp)
- ✅ Contrôles physiques (plages plausibles)
- ✅ Score qualité calculé

### **Stockage**
- ✅ Raw layer active
- ✅ Processed layer active
- ✅ Serving layer optimisée
- ✅ Politique rétention définie
- ✅ Versioning tracé

### **Produit**
- ✅ Endpoints métier testés
- ✅ Dashboard alimenté
- ✅ Alertes déclenchables
- ✅ Logs consultables
- ✅ Monitoring actif

---

## 📊 Métriques de Succès

| Métrique | Objectif | Mesure |
|----------|----------|--------|
| **Latence ingestion** | < 5 min | Temps entre mesure et disponibilité API |
| **Complétude** | > 95% | % données attendues vs reçues |
| **Qualité** | > 90% | % données avec quality_score > 0.7 |
| **Disponibilité API** | > 99% | Uptime endpoints métier |
| **Temps réponse API** | < 200ms | P95 latence endpoints |

---

**🌊 Ocean Sentinel V3.0 - Pipeline API Production-Ready**
