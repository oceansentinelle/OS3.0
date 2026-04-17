#!/bin/bash

# =====================================================
# Script de Déploiement Ocean Sentinel sur VPS
# =====================================================
# Usage: bash deploy-to-vps.sh
# =====================================================

set -e

echo "🌊 Déploiement Ocean Sentinel TimescaleDB"
echo "=========================================="
echo ""

# Création de la structure
echo "[1/10] Création de la structure de répertoires..."
mkdir -p ~/oceansentinel/{init-scripts,scripts}
cd ~/oceansentinel

# docker-compose.yml
echo "[2/10] Création de docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: oceansentinel_timescaledb
    restart: unless-stopped
    
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-oceansentinel}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Variable POSTGRES_PASSWORD requise}
      POSTGRES_DB: ${POSTGRES_DB:-oceansentinelle}
      POSTGRES_HOST_AUTH_METHOD: scram-sha-256
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256"
      TIMESCALEDB_TELEMETRY: "off"
      TS_TUNE_MEMORY: "8GB"
      TS_TUNE_NUM_CPUS: "4"
      TS_TUNE_MAX_CONNS: "100"
      TS_TUNE_MAX_BG_WORKERS: "8"
    
    ports:
      - "${POSTGRES_PORT:-6543}:5432"
    
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
      - ./postgresql-custom.conf:/etc/postgresql/postgresql.conf:ro
    
    command: 
      - "postgres"
      - "-c"
      - "config_file=/etc/postgresql/postgresql.conf"
    
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-oceansentinel} -d ${POSTGRES_DB:-oceansentinelle}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    
    user: postgres
    
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 7G
        reservations:
          cpus: '2'
          memory: 4G
    
    networks:
      - oceansentinel_network
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  timescaledb_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/oceansentinel/data

networks:
  oceansentinel_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
EOF

# .env.example
echo "[3/10] Création de .env.example..."
cat > .env.example << 'EOF'
POSTGRES_USER=oceansentinel
POSTGRES_PASSWORD=CHANGEZ_MOI_AVEC_UN_MOT_DE_PASSE_FORT
POSTGRES_DB=oceansentinelle
POSTGRES_PORT=6543
TS_TUNE_MEMORY=8GB
TS_TUNE_NUM_CPUS=4
TS_TUNE_MAX_CONNS=100
TS_TUNE_MAX_BG_WORKERS=8
TIMESCALEDB_TELEMETRY=off
EOF

# postgresql-custom.conf (version simplifiée)
echo "[4/10] Création de postgresql-custom.conf..."
cat > postgresql-custom.conf << 'EOF'
listen_addresses = '*'
port = 5432
max_connections = 100
password_encryption = scram-sha-256
shared_buffers = 2GB
effective_cache_size = 4GB
work_mem = 20MB
maintenance_work_mem = 512MB
max_worker_processes = 8
max_parallel_workers = 4
timescaledb.max_background_workers = 8
wal_level = replica
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
checkpoint_timeout = 15min
random_page_cost = 1.1
effective_io_concurrency = 200
shared_preload_libraries = 'timescaledb'
log_min_duration_statement = 1000
logging_collector = on
track_io_timing = on
autovacuum = on
timezone = 'UTC'
EOF

# Script SQL d'initialisation (version compacte)
echo "[5/10] Création du script d'initialisation SQL..."
cat > init-scripts/01-init-timescaledb.sql << 'EOSQL'
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE SCHEMA IF NOT EXISTS barag;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS metadata;

CREATE TABLE IF NOT EXISTS barag.sensor_data (
    time TIMESTAMPTZ NOT NULL,
    station_id TEXT NOT NULL,
    temperature_air DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    wind_direction DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    temperature_water DOUBLE PRECISION,
    salinity DOUBLE PRECISION,
    ph DOUBLE PRECISION,
    dissolved_oxygen DOUBLE PRECISION,
    turbidity DOUBLE PRECISION,
    quality_flag INTEGER DEFAULT 0,
    data_source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, station_id)
);

SELECT create_hypertable(
    'barag.sensor_data',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

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

SELECT add_retention_policy(
    'barag.sensor_data',
    INTERVAL '2 years',
    if_not_exists => TRUE
);

CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.hourly_aggregates
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    station_id,
    AVG(temperature_air) AS temp_air_avg,
    MIN(temperature_air) AS temp_air_min,
    MAX(temperature_air) AS temp_air_max,
    AVG(temperature_water) AS temp_water_avg,
    AVG(wind_speed) AS wind_speed_avg,
    MAX(wind_speed) AS wind_speed_max,
    AVG(salinity) AS salinity_avg,
    AVG(ph) AS ph_avg,
    COUNT(*) AS sample_count
FROM barag.sensor_data
GROUP BY bucket, station_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'analytics.hourly_aggregates',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '15 minutes',
    if_not_exists => TRUE
);

CREATE TABLE IF NOT EXISTS metadata.stations (
    station_id TEXT PRIMARY KEY,
    station_name TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    status TEXT DEFAULT 'active',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO metadata.stations (station_id, station_name, status, description)
VALUES ('BARAG', 'Station BARAG - Ocean Sentinel', 'active', 'Station principale')
ON CONFLICT (station_id) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE '✓ TimescaleDB initialisé avec succès pour Ocean Sentinel';
END
$$;
EOSQL

# Script de tuning
echo "[6/10] Création du script de tuning..."
cat > scripts/tune-timescaledb.sh << 'EOSCRIPT'
#!/bin/bash
set -e
CONTAINER_NAME="oceansentinel_timescaledb"
echo "🔧 Tuning TimescaleDB..."
docker exec -u postgres ${CONTAINER_NAME} timescaledb-tune --quiet --yes --conf-path=/etc/postgresql/postgresql.conf --memory=8GB --cpus=4 --max-conns=100 --max-bg-workers=8
echo "♻️  Redémarrage du conteneur..."
docker-compose restart timescaledb
sleep 5
docker exec ${CONTAINER_NAME} pg_isready -U oceansentinel -d oceansentinelle
echo "✅ Tuning terminé !"
EOSCRIPT

chmod +x scripts/tune-timescaledb.sh

# Script de health check
echo "[7/10] Création du script de health check..."
cat > scripts/health-check.sh << 'EOSCRIPT'
#!/bin/bash
CONTAINER="oceansentinel_timescaledb"
echo "🔍 Health Check Ocean Sentinel"
echo "================================"
docker exec $CONTAINER pg_isready -U oceansentinel -d oceansentinelle && echo "✅ Database OK" || echo "❌ Database DOWN"
docker exec $CONTAINER psql -U oceansentinel -d oceansentinelle -c "SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';" -t | xargs echo "TimescaleDB version:"
docker exec $CONTAINER psql -U oceansentinel -d oceansentinelle -c "SELECT COUNT(*) FROM timescaledb_information.hypertables;" -t | xargs echo "Hypertables:"
docker exec $CONTAINER psql -U oceansentinel -d oceansentinelle -c "SELECT pg_size_pretty(pg_database_size('oceansentinelle'));" -t | xargs echo "Database size:"
echo "✅ Health check terminé"
EOSCRIPT

chmod +x scripts/health-check.sh

# Configuration de l'environnement
echo "[8/10] Configuration de l'environnement..."
if [ ! -f .env ]; then
    cp .env.example .env
    PASSWORD=$(openssl rand -base64 32)
    sed -i "s/CHANGEZ_MOI_AVEC_UN_MOT_DE_PASSE_FORT/$PASSWORD/" .env
    echo "✅ Mot de passe généré: $PASSWORD"
    echo "⚠️  SAUVEGARDEZ CE MOT DE PASSE !"
else
    echo "⚠️  Fichier .env existe déjà, non modifié"
fi

# Création du répertoire de données
echo "[9/10] Création du répertoire de données..."
sudo mkdir -p /opt/oceansentinel/data
sudo chown -R 999:999 /opt/oceansentinel/data
sudo chmod 700 /opt/oceansentinel/data

# Résumé
echo "[10/10] Résumé de l'installation..."
echo ""
echo "✅ Déploiement terminé !"
echo ""
echo "📁 Fichiers créés:"
echo "   - docker-compose.yml"
echo "   - postgresql-custom.conf"
echo "   - .env (avec mot de passe généré)"
echo "   - init-scripts/01-init-timescaledb.sql"
echo "   - scripts/tune-timescaledb.sh"
echo "   - scripts/health-check.sh"
echo ""
echo "🚀 Prochaines étapes:"
echo "   1. docker compose up -d"
echo "   2. docker compose logs -f timescaledb"
echo "   3. ./scripts/tune-timescaledb.sh"
echo "   4. ./scripts/health-check.sh"
echo ""
