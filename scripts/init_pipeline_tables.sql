-- ============================================================================
-- Ocean Sentinel V3.0 - Initialisation Tables Pipeline API
-- ============================================================================
-- 
-- Ce script crée toutes les tables nécessaires au pipeline API 3 couches:
-- 1. RAW LAYER (données brutes)
-- 2. PROCESSED LAYER (données validées)
-- 3. SERVING LAYER (données métier)
--
-- Exécution:
-- psql -U oceansentinel -d oceansentinelle -f init_pipeline_tables.sql
-- ============================================================================

-- Extension UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension TimescaleDB (si pas déjà fait)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- RAW LAYER
-- ============================================================================

-- Table d'audit ingestion
CREATE TABLE IF NOT EXISTS raw_ingestion_log (
    ingestion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'partial', 'failed')),
    records_fetched INTEGER DEFAULT 0,
    records_rejected INTEGER DEFAULT 0,
    payload_path TEXT,
    checksum TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ingestion_log_source_time 
ON raw_ingestion_log (source_name, fetched_at DESC);

COMMENT ON TABLE raw_ingestion_log IS 'Journal d''audit des ingestions de données';

-- Table données brutes
CREATE TABLE IF NOT EXISTS raw_measurements (
    raw_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ingestion_id UUID REFERENCES raw_ingestion_log(ingestion_id),
    station_id TEXT NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    source_name TEXT NOT NULL,
    payload JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_measurements_station_time 
ON raw_measurements (station_id, timestamp_utc DESC);

CREATE INDEX IF NOT EXISTS idx_raw_measurements_source 
ON raw_measurements (source_name, timestamp_utc DESC);

CREATE INDEX IF NOT EXISTS idx_raw_measurements_ingestion 
ON raw_measurements (ingestion_id);

COMMENT ON TABLE raw_measurements IS 'Données brutes non transformées (payload JSON complet)';

-- ============================================================================
-- PROCESSED LAYER
-- ============================================================================

-- Table mesures validées (extension de ocean_data existante)
-- Note: Si ocean_data existe déjà, cette commande échouera gracieusement
CREATE TABLE IF NOT EXISTS validated_measurements (
    measurement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_id UUID REFERENCES raw_measurements(raw_id),
    station_id TEXT NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    variable TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit TEXT NOT NULL,
    quality_score DOUBLE PRECISION CHECK (quality_score >= 0 AND quality_score <= 1),
    validation_status TEXT CHECK (validation_status IN ('valid', 'suspect', 'invalid')),
    anomaly_flag BOOLEAN DEFAULT FALSE,
    data_source TEXT,
    data_status TEXT CHECK (data_status IN ('measured', 'inferred', 'interpolated', 'simulated')),
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (station_id, timestamp_utc, variable)
);

-- Créer hypertable si pas déjà fait
SELECT create_hypertable(
    'validated_measurements', 
    'timestamp_utc',
    if_not_exists => TRUE,
    migrate_data => TRUE
);

CREATE INDEX IF NOT EXISTS idx_validated_station_var_time 
ON validated_measurements (station_id, variable, timestamp_utc DESC);

CREATE INDEX IF NOT EXISTS idx_validated_quality 
ON validated_measurements (quality_score, timestamp_utc DESC) 
WHERE quality_score < 0.7;

CREATE INDEX IF NOT EXISTS idx_validated_anomaly 
ON validated_measurements (anomaly_flag, timestamp_utc DESC) 
WHERE anomaly_flag = TRUE;

CREATE INDEX IF NOT EXISTS idx_validated_status 
ON validated_measurements (validation_status, timestamp_utc DESC);

COMMENT ON TABLE validated_measurements IS 'Mesures validées et normalisées avec score qualité';

-- Table métriques dérivées
CREATE TABLE IF NOT EXISTS derived_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id TEXT NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    metric_unit TEXT,
    calculation_version TEXT,
    metadata JSONB DEFAULT '{}',
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (station_id, timestamp_utc, metric_name)
);

SELECT create_hypertable(
    'derived_metrics', 
    'timestamp_utc',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_derived_station_metric_time 
ON derived_metrics (station_id, metric_name, timestamp_utc DESC);

COMMENT ON TABLE derived_metrics IS 'Métriques calculées (variations, tendances, scores)';

-- ============================================================================
-- SERVING LAYER
-- ============================================================================

-- Vue matérialisée: dernières mesures
DROP MATERIALIZED VIEW IF EXISTS latest_metrics CASCADE;

CREATE MATERIALIZED VIEW latest_metrics AS
SELECT DISTINCT ON (station_id, variable)
    station_id,
    variable,
    value,
    unit,
    quality_score,
    timestamp_utc,
    data_status,
    anomaly_flag
FROM validated_measurements
ORDER BY station_id, variable, timestamp_utc DESC;

CREATE UNIQUE INDEX idx_latest_metrics_station_var 
ON latest_metrics (station_id, variable);

COMMENT ON MATERIALIZED VIEW latest_metrics IS 'Dernières mesures par station et variable';

-- Agrégats horaires (continuous aggregate TimescaleDB)
DROP MATERIALIZED VIEW IF EXISTS hourly_aggregates CASCADE;

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
    COUNT(*) as sample_count,
    AVG(quality_score) as avg_quality
FROM validated_measurements
WHERE validation_status = 'valid'
GROUP BY bucket, station_id, variable;

COMMENT ON MATERIALIZED VIEW hourly_aggregates IS 'Agrégats horaires pour analytics';

-- Politique de rafraîchissement automatique
SELECT add_continuous_aggregate_policy(
    'hourly_aggregates',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Table alertes
CREATE TABLE IF NOT EXISTS alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id TEXT NOT NULL,
    zone_id TEXT,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    triggered_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'dismissed')),
    confidence DOUBLE PRECISION CHECK (confidence >= 0 AND confidence <= 1),
    evidence JSONB DEFAULT '{}',
    action_recommended TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_station_time 
ON alerts (station_id, triggered_at DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_status 
ON alerts (status, severity, triggered_at DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_type 
ON alerts (alert_type, triggered_at DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_active 
ON alerts (triggered_at DESC) 
WHERE status = 'active';

COMMENT ON TABLE alerts IS 'Alertes écologiques et techniques';

-- Table prévisions
CREATE TABLE IF NOT EXISTS forecast_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id TEXT NOT NULL,
    variable TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL,
    forecast_timestamp TIMESTAMPTZ NOT NULL,
    horizon_hours INTEGER NOT NULL,
    predicted_value DOUBLE PRECISION NOT NULL,
    confidence_lower DOUBLE PRECISION,
    confidence_upper DOUBLE PRECISION,
    model_version TEXT NOT NULL,
    model_type TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecast_station_time 
ON forecast_predictions (station_id, forecast_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_forecast_generated 
ON forecast_predictions (generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_forecast_horizon 
ON forecast_predictions (horizon_hours, forecast_timestamp DESC);

COMMENT ON TABLE forecast_predictions IS 'Prévisions IA (LSTM, ARIMA, ensemble)';

-- Table rapports qualité
CREATE TABLE IF NOT EXISTS data_quality_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id TEXT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    completeness_rate DOUBLE PRECISION CHECK (completeness_rate >= 0 AND completeness_rate <= 1),
    anomaly_rate DOUBLE PRECISION CHECK (anomaly_rate >= 0 AND anomaly_rate <= 1),
    latency_avg_minutes INTEGER,
    final_quality_score DOUBLE PRECISION CHECK (final_quality_score >= 0 AND final_quality_score <= 1),
    details JSONB DEFAULT '{}',
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quality_reports_station_period 
ON data_quality_reports (station_id, period_end DESC);

CREATE INDEX IF NOT EXISTS idx_quality_reports_score 
ON data_quality_reports (final_quality_score, period_end DESC);

COMMENT ON TABLE data_quality_reports IS 'Rapports qualité des données par station et période';

-- ============================================================================
-- Fonctions Utilitaires
-- ============================================================================

-- Fonction de rafraîchissement latest_metrics
CREATE OR REPLACE FUNCTION refresh_latest_metrics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY latest_metrics;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_latest_metrics() IS 'Rafraîchit la vue matérialisée des dernières mesures';

-- Fonction de calcul score qualité station
CREATE OR REPLACE FUNCTION calculate_station_quality_score(
    p_station_id TEXT,
    p_period_hours INTEGER DEFAULT 24
)
RETURNS DOUBLE PRECISION AS $$
DECLARE
    v_score DOUBLE PRECISION;
BEGIN
    SELECT AVG(quality_score)
    INTO v_score
    FROM validated_measurements
    WHERE station_id = p_station_id
      AND timestamp_utc > NOW() - (p_period_hours || ' hours')::INTERVAL
      AND validation_status = 'valid';
    
    RETURN COALESCE(v_score, 0.0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_station_quality_score IS 'Calcule le score qualité moyen d''une station sur une période';

-- ============================================================================
-- Politiques de Rétention
-- ============================================================================

-- Rétention raw_measurements: 90 jours
SELECT add_retention_policy(
    'raw_measurements',
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- Rétention validated_measurements: conservation longue (pas de politique)
-- Les agrégats horaires permettent de réduire la charge

-- Compression automatique des données anciennes
SELECT add_compression_policy(
    'validated_measurements',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

SELECT add_compression_policy(
    'derived_metrics',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- Vues Métier
-- ============================================================================

-- Vue: Stations avec dernière activité
CREATE OR REPLACE VIEW stations_status AS
SELECT 
    station_id,
    MAX(timestamp_utc) as last_measurement,
    COUNT(DISTINCT variable) as variables_count,
    AVG(quality_score) as avg_quality,
    CASE 
        WHEN MAX(timestamp_utc) > NOW() - INTERVAL '1 hour' THEN 'active'
        WHEN MAX(timestamp_utc) > NOW() - INTERVAL '24 hours' THEN 'delayed'
        ELSE 'inactive'
    END as status
FROM validated_measurements
WHERE timestamp_utc > NOW() - INTERVAL '7 days'
GROUP BY station_id;

COMMENT ON VIEW stations_status IS 'Statut temps réel des stations';

-- Vue: Alertes actives avec contexte
CREATE OR REPLACE VIEW active_alerts_with_context AS
SELECT 
    a.alert_id,
    a.station_id,
    a.alert_type,
    a.severity,
    a.triggered_at,
    a.confidence,
    a.evidence,
    s.last_measurement,
    s.avg_quality
FROM alerts a
LEFT JOIN stations_status s ON a.station_id = s.station_id
WHERE a.status = 'active'
ORDER BY a.severity DESC, a.triggered_at DESC;

COMMENT ON VIEW active_alerts_with_context IS 'Alertes actives avec contexte station';

-- ============================================================================
-- Grants (Permissions)
-- ============================================================================

-- Accès lecture pour utilisateur API
GRANT SELECT ON ALL TABLES IN SCHEMA public TO oceansentinel;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO oceansentinel;

-- Accès écriture pour processus d'ingestion
GRANT INSERT, UPDATE ON raw_ingestion_log TO oceansentinel;
GRANT INSERT ON raw_measurements TO oceansentinel;
GRANT INSERT, UPDATE ON validated_measurements TO oceansentinel;
GRANT INSERT ON derived_metrics TO oceansentinel;
GRANT INSERT, UPDATE ON alerts TO oceansentinel;
GRANT INSERT ON forecast_predictions TO oceansentinel;
GRANT INSERT ON data_quality_reports TO oceansentinel;

-- ============================================================================
-- Statistiques et Vacuum
-- ============================================================================

ANALYZE raw_ingestion_log;
ANALYZE raw_measurements;
ANALYZE validated_measurements;
ANALYZE derived_metrics;
ANALYZE alerts;
ANALYZE forecast_predictions;
ANALYZE data_quality_reports;

-- ============================================================================
-- Résumé
-- ============================================================================

SELECT 
    'Pipeline API initialisé avec succès' as message,
    COUNT(*) FILTER (WHERE table_type = 'BASE TABLE') as tables_created,
    COUNT(*) FILTER (WHERE table_type = 'VIEW') as views_created
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'raw_ingestion_log',
      'raw_measurements',
      'validated_measurements',
      'derived_metrics',
      'alerts',
      'forecast_predictions',
      'data_quality_reports',
      'latest_metrics',
      'hourly_aggregates',
      'stations_status',
      'active_alerts_with_context'
  );

\echo '============================================================================'
\echo 'Ocean Sentinel V3.0 - Pipeline API Tables Initialisées'
\echo '============================================================================'
\echo 'RAW LAYER:'
\echo '  - raw_ingestion_log'
\echo '  - raw_measurements'
\echo ''
\echo 'PROCESSED LAYER:'
\echo '  - validated_measurements (hypertable)'
\echo '  - derived_metrics (hypertable)'
\echo ''
\echo 'SERVING LAYER:'
\echo '  - latest_metrics (materialized view)'
\echo '  - hourly_aggregates (continuous aggregate)'
\echo '  - alerts'
\echo '  - forecast_predictions'
\echo '  - data_quality_reports'
\echo ''
\echo 'VUES MÉTIER:'
\echo '  - stations_status'
\echo '  - active_alerts_with_context'
\echo '============================================================================'
