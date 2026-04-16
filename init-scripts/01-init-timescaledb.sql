-- =====================================================
-- Ocean Sentinel - Initialisation TimescaleDB
-- =====================================================
-- Description: Configuration initiale de la base de données
--              avec extension TimescaleDB et hypertables
-- Auteur: Ocean Sentinel Team
-- Date: 2026-04-16
-- =====================================================

-- Activation de l'extension TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Vérification de la version
SELECT extname, extversion FROM pg_extension WHERE extname = 'timescaledb';

-- =====================================================
-- CRÉATION DES SCHÉMAS
-- =====================================================

CREATE SCHEMA IF NOT EXISTS barag;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS metadata;

-- =====================================================
-- TABLE PRINCIPALE : Données de la station BARAG
-- =====================================================

CREATE TABLE IF NOT EXISTS barag.sensor_data (
    time TIMESTAMPTZ NOT NULL,
    station_id TEXT NOT NULL,
    
    -- Données météorologiques
    temperature_air DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    wind_direction DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    
    -- Données océanographiques
    temperature_water DOUBLE PRECISION,
    salinity DOUBLE PRECISION,
    ph DOUBLE PRECISION,
    dissolved_oxygen DOUBLE PRECISION,
    turbidity DOUBLE PRECISION,
    
    -- Données de qualité
    quality_flag INTEGER DEFAULT 0,
    data_source TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (time, station_id)
);

-- Conversion en hypertable (partitionnement automatique par temps)
SELECT create_hypertable(
    'barag.sensor_data',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- =====================================================
-- POLITIQUE DE COMPRESSION (7 jours)
-- =====================================================

ALTER TABLE barag.sensor_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'station_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy(
    'barag.sensor_data',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- =====================================================
-- POLITIQUE DE RÉTENTION (optionnelle - 2 ans)
-- =====================================================

SELECT add_retention_policy(
    'barag.sensor_data',
    INTERVAL '2 years',
    if_not_exists => TRUE
);

-- =====================================================
-- VUES MATÉRIALISÉES CONTINUES (Agrégats)
-- =====================================================

-- Agrégat horaire
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.hourly_aggregates
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    station_id,
    
    -- Statistiques température air
    AVG(temperature_air) AS temp_air_avg,
    MIN(temperature_air) AS temp_air_min,
    MAX(temperature_air) AS temp_air_max,
    
    -- Statistiques température eau
    AVG(temperature_water) AS temp_water_avg,
    MIN(temperature_water) AS temp_water_min,
    MAX(temperature_water) AS temp_water_max,
    
    -- Statistiques vent
    AVG(wind_speed) AS wind_speed_avg,
    MAX(wind_speed) AS wind_speed_max,
    
    -- Statistiques océanographiques
    AVG(salinity) AS salinity_avg,
    AVG(ph) AS ph_avg,
    AVG(dissolved_oxygen) AS do_avg,
    
    -- Métadonnées
    COUNT(*) AS sample_count
FROM barag.sensor_data
GROUP BY bucket, station_id
WITH NO DATA;

-- Politique de rafraîchissement (toutes les 15 minutes)
SELECT add_continuous_aggregate_policy(
    'analytics.hourly_aggregates',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '15 minutes',
    if_not_exists => TRUE
);

-- Agrégat journalier
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.daily_aggregates
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    station_id,
    
    AVG(temperature_air) AS temp_air_avg,
    MIN(temperature_air) AS temp_air_min,
    MAX(temperature_air) AS temp_air_max,
    STDDEV(temperature_air) AS temp_air_stddev,
    
    AVG(temperature_water) AS temp_water_avg,
    MIN(temperature_water) AS temp_water_min,
    MAX(temperature_water) AS temp_water_max,
    
    AVG(wind_speed) AS wind_speed_avg,
    MAX(wind_speed) AS wind_speed_max,
    
    SUM(precipitation) AS precipitation_total,
    
    AVG(salinity) AS salinity_avg,
    AVG(ph) AS ph_avg,
    AVG(dissolved_oxygen) AS do_avg,
    AVG(turbidity) AS turbidity_avg,
    
    COUNT(*) AS sample_count
FROM barag.sensor_data
GROUP BY bucket, station_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'analytics.daily_aggregates',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- =====================================================
-- INDEX POUR OPTIMISATION DES REQUÊTES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_sensor_data_station 
    ON barag.sensor_data (station_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_sensor_data_quality 
    ON barag.sensor_data (quality_flag, time DESC) 
    WHERE quality_flag > 0;

-- =====================================================
-- TABLE DE MÉTADONNÉES DES STATIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS metadata.stations (
    station_id TEXT PRIMARY KEY,
    station_name TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    elevation DOUBLE PRECISION,
    installation_date DATE,
    status TEXT DEFAULT 'active',
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insertion de la station BARAG
INSERT INTO metadata.stations (
    station_id, 
    station_name, 
    latitude, 
    longitude,
    status,
    description
) VALUES (
    'BARAG',
    'Station BARAG - Ocean Sentinel',
    NULL,  -- À renseigner
    NULL,  -- À renseigner
    'active',
    'Station principale de surveillance océanographique'
) ON CONFLICT (station_id) DO NOTHING;

-- =====================================================
-- FONCTION DE MISE À JOUR AUTOMATIQUE
-- =====================================================

CREATE OR REPLACE FUNCTION metadata.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_stations_modtime
    BEFORE UPDATE ON metadata.stations
    FOR EACH ROW
    EXECUTE FUNCTION metadata.update_modified_column();

-- =====================================================
-- RÔLES ET PERMISSIONS
-- =====================================================

-- Rôle lecture seule pour les applications d'analyse
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'oceansentinel_readonly') THEN
        CREATE ROLE oceansentinel_readonly WITH LOGIN PASSWORD 'readonly_changeme';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE oceansentinelle TO oceansentinel_readonly;
GRANT USAGE ON SCHEMA barag, analytics, metadata TO oceansentinel_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA barag, analytics, metadata TO oceansentinel_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA barag, analytics, metadata 
    GRANT SELECT ON TABLES TO oceansentinel_readonly;

-- Rôle écriture pour l'ingesteur
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'oceansentinel_writer') THEN
        CREATE ROLE oceansentinel_writer WITH LOGIN PASSWORD 'writer_changeme';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE oceansentinelle TO oceansentinel_writer;
GRANT USAGE ON SCHEMA barag, metadata TO oceansentinel_writer;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA barag, metadata TO oceansentinel_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA barag, metadata 
    GRANT SELECT, INSERT, UPDATE ON TABLES TO oceansentinel_writer;

-- =====================================================
-- STATISTIQUES ET MONITORING
-- =====================================================

-- Vue pour le monitoring des chunks
CREATE OR REPLACE VIEW metadata.chunk_status AS
SELECT
    hypertable_name,
    chunk_name,
    range_start,
    range_end,
    is_compressed,
    pg_size_pretty(total_bytes) AS total_size,
    pg_size_pretty(compressed_total_bytes) AS compressed_size,
    ROUND(100.0 * compressed_total_bytes / NULLIF(total_bytes, 0), 2) AS compression_ratio
FROM timescaledb_information.chunks
ORDER BY range_start DESC;

-- Vue pour les statistiques d'ingestion
CREATE OR REPLACE VIEW metadata.ingestion_stats AS
SELECT
    station_id,
    DATE(time) AS date,
    COUNT(*) AS records,
    MIN(time) AS first_record,
    MAX(time) AS last_record,
    COUNT(DISTINCT DATE_TRUNC('hour', time)) AS hours_covered
FROM barag.sensor_data
WHERE time > NOW() - INTERVAL '7 days'
GROUP BY station_id, DATE(time)
ORDER BY date DESC, station_id;

-- =====================================================
-- FINALISATION
-- =====================================================

-- Analyse des tables pour optimiser le planificateur
ANALYZE barag.sensor_data;
ANALYZE metadata.stations;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE '✓ TimescaleDB initialisé avec succès pour Ocean Sentinel';
    RAISE NOTICE '✓ Hypertable créée : barag.sensor_data';
    RAISE NOTICE '✓ Compression activée : 7 jours';
    RAISE NOTICE '✓ Rétention configurée : 2 ans';
    RAISE NOTICE '✓ Agrégats continus : horaire + journalier';
END
$$;
