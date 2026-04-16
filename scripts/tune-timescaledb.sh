#!/bin/bash

# =====================================================
# Script de Tuning Automatique TimescaleDB
# =====================================================
# Description: Exécute timescaledb-tune dans le conteneur
#              et applique les recommandations optimales
# Usage: ./tune-timescaledb.sh
# =====================================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="oceansentinel_timescaledb"
POSTGRES_CONF="/etc/postgresql/postgresql.conf"
BACKUP_CONF="/etc/postgresql/postgresql.conf.backup"

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TimescaleDB Tuning - Ocean Sentinel              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Vérification que le conteneur est en cours d'exécution
echo -e "${YELLOW}[1/5]${NC} Vérification du conteneur..."
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}✗ Erreur: Le conteneur ${CONTAINER_NAME} n'est pas en cours d'exécution${NC}"
    echo -e "${YELLOW}  Démarrez-le avec: docker-compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Conteneur actif${NC}"
echo ""

# Sauvegarde de la configuration actuelle
echo -e "${YELLOW}[2/5]${NC} Sauvegarde de la configuration actuelle..."
docker exec -u postgres ${CONTAINER_NAME} bash -c "
    if [ -f ${POSTGRES_CONF} ]; then
        cp ${POSTGRES_CONF} ${BACKUP_CONF}
        echo 'Backup créé: ${BACKUP_CONF}'
    fi
"
echo -e "${GREEN}✓ Configuration sauvegardée${NC}"
echo ""

# Exécution de timescaledb-tune
echo -e "${YELLOW}[3/5]${NC} Exécution de timescaledb-tune..."
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker exec -u postgres ${CONTAINER_NAME} timescaledb-tune \
    --quiet \
    --yes \
    --conf-path=${POSTGRES_CONF} \
    --memory=8GB \
    --cpus=4 \
    --max-conns=100 \
    --max-bg-workers=8

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Tuning appliqué${NC}"
echo ""

# Affichage des paramètres clés
echo -e "${YELLOW}[4/5]${NC} Paramètres optimisés:"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker exec -u postgres ${CONTAINER_NAME} bash -c "
    grep -E '^(shared_buffers|effective_cache_size|work_mem|maintenance_work_mem|max_worker_processes|timescaledb.max_background_workers)' ${POSTGRES_CONF} || true
"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Redémarrage du conteneur pour appliquer les changements
echo -e "${YELLOW}[5/5]${NC} Redémarrage du conteneur pour appliquer les changements..."
docker-compose restart timescaledb

# Attente que le conteneur soit prêt
echo -e "${YELLOW}⏳ Attente de la disponibilité de la base de données...${NC}"
sleep 5

# Vérification de la santé
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec ${CONTAINER_NAME} pg_isready -U oceansentinel -d oceansentinelle > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Base de données prête${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -ne "${YELLOW}  Tentative ${RETRY_COUNT}/${MAX_RETRIES}...\r${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Timeout: La base de données n'a pas démarré${NC}"
    echo -e "${YELLOW}  Vérifiez les logs: docker-compose logs timescaledb${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ Tuning terminé avec succès                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo -e "  • Voir les logs:        ${YELLOW}docker-compose logs -f timescaledb${NC}"
echo -e "  • Restaurer le backup:  ${YELLOW}docker exec ${CONTAINER_NAME} cp ${BACKUP_CONF} ${POSTGRES_CONF}${NC}"
echo -e "  • Vérifier la config:   ${YELLOW}docker exec ${CONTAINER_NAME} cat ${POSTGRES_CONF}${NC}"
echo ""
