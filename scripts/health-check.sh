#!/bin/bash

# =====================================================
# Script de Vérification de Santé TimescaleDB
# =====================================================
# Description: Vérifie l'état complet de l'instance
# Usage: ./health-check.sh
# =====================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONTAINER_NAME="oceansentinel_timescaledb"
DB_USER="oceansentinel"
DB_NAME="oceansentinelle"

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Health Check - Ocean Sentinel TimescaleDB        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Fonction de test
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# 1. Vérification du conteneur
echo -ne "${YELLOW}[1/8]${NC} Conteneur Docker actif... "
docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
check_status

# 2. Vérification de la connectivité
echo -ne "${YELLOW}[2/8]${NC} Connectivité PostgreSQL... "
docker exec ${CONTAINER_NAME} pg_isready -U ${DB_USER} -d ${DB_NAME} > /dev/null 2>&1
check_status

# 3. Vérification de l'extension TimescaleDB
echo -ne "${YELLOW}[3/8]${NC} Extension TimescaleDB... "
VERSION=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';
" 2>/dev/null)
if [ -n "$VERSION" ]; then
    echo -e "${GREEN}✓${NC} (v${VERSION})"
else
    echo -e "${RED}✗${NC}"
fi

# 4. Vérification des hypertables
echo -ne "${YELLOW}[4/8]${NC} Hypertables... "
HYPERTABLES=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT COUNT(*) FROM timescaledb_information.hypertables;
" 2>/dev/null)
if [ "$HYPERTABLES" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} (${HYPERTABLES} hypertable(s))"
else
    echo -e "${RED}✗${NC} (Aucune hypertable trouvée)"
fi

# 5. Vérification de la compression
echo -ne "${YELLOW}[5/8]${NC} Politique de compression... "
COMPRESSION=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT COUNT(*) FROM timescaledb_information.jobs 
    WHERE proc_name = 'policy_compression';
" 2>/dev/null)
if [ "$COMPRESSION" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} (${COMPRESSION} politique(s))"
else
    echo -e "${YELLOW}⚠${NC} (Aucune politique configurée)"
fi

# 6. Vérification des agrégats continus
echo -ne "${YELLOW}[6/8]${NC} Agrégats continus... "
CAGGS=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT COUNT(*) FROM timescaledb_information.continuous_aggregates;
" 2>/dev/null)
if [ "$CAGGS" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} (${CAGGS} agrégat(s))"
else
    echo -e "${YELLOW}⚠${NC} (Aucun agrégat configuré)"
fi

# 7. Vérification de l'utilisation disque
echo -ne "${YELLOW}[7/8]${NC} Utilisation disque... "
DB_SIZE=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT pg_size_pretty(pg_database_size('${DB_NAME}'));
" 2>/dev/null | tr -d ' ')
if [ -n "$DB_SIZE" ]; then
    echo -e "${GREEN}✓${NC} (${DB_SIZE})"
else
    echo -e "${RED}✗${NC}"
fi

# 8. Vérification des connexions actives
echo -ne "${YELLOW}[8/8]${NC} Connexions actives... "
CONNECTIONS=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT COUNT(*) FROM pg_stat_activity WHERE datname = '${DB_NAME}';
" 2>/dev/null)
if [ -n "$CONNECTIONS" ]; then
    echo -e "${GREEN}✓${NC} (${CONNECTIONS} connexion(s))"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Statistiques détaillées
echo -e "${BLUE}📊 Statistiques Détaillées${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Chunks
CHUNKS=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT COUNT(*) FROM timescaledb_information.chunks;
" 2>/dev/null)
COMPRESSED_CHUNKS=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT COUNT(*) FROM timescaledb_information.chunks WHERE is_compressed = true;
" 2>/dev/null)
echo -e "  • Chunks totaux:      ${GREEN}${CHUNKS}${NC}"
echo -e "  • Chunks compressés:  ${GREEN}${COMPRESSED_CHUNKS}${NC}"

# Données récentes
RECENT_DATA=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT COUNT(*) FROM barag.sensor_data WHERE time > NOW() - INTERVAL '24 hours';
" 2>/dev/null)
echo -e "  • Données (24h):      ${GREEN}${RECENT_DATA}${NC} enregistrements"

# Uptime
UPTIME=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "
    SELECT date_trunc('second', NOW() - pg_postmaster_start_time());
" 2>/dev/null)
echo -e "  • Uptime:             ${GREEN}${UPTIME}${NC}"

# Utilisation mémoire
MEMORY=$(docker stats ${CONTAINER_NAME} --no-stream --format "{{.MemUsage}}" 2>/dev/null)
echo -e "  • Mémoire:            ${GREEN}${MEMORY}${NC}"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Top 5 des tables par taille
echo -e "${BLUE}📦 Top 5 Tables par Taille${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -c "
    SELECT 
        schemaname || '.' || tablename AS table,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
    FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
    LIMIT 5;
" 2>/dev/null

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ Health Check Terminé                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
