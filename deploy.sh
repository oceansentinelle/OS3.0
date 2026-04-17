#!/bin/bash
# ============================================================================
# Ocean Sentinel V3.0 - Script Déploiement Rapide
# ============================================================================
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh
#
# ============================================================================

set -e  # Arrêt si erreur

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=============================================================================="
echo "OCEAN SENTINEL V3.0 - DÉPLOIEMENT BACKEND"
echo "=============================================================================="
echo ""

# ============================================================================
# 1. Vérifications Préalables
# ============================================================================

echo -e "${YELLOW}1. Vérifications préalables...${NC}"

# Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker non installé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker installé${NC}"

# Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose non installé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose installé${NC}"

# Fichier .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Fichier .env manquant${NC}"
    echo "Copie de .env.full.example vers .env..."
    cp .env.full.example .env
    echo -e "${RED}⚠️  IMPORTANT: Éditez .env et changez les mots de passe !${NC}"
    echo "Commande: vim .env"
    read -p "Appuyez sur Entrée après avoir édité .env..."
fi
echo -e "${GREEN}✅ Fichier .env présent${NC}"

echo ""

# ============================================================================
# 2. Création Répertoires
# ============================================================================

echo -e "${YELLOW}2. Création répertoires...${NC}"

mkdir -p data/seanoe
mkdir -p data_drop/siba/processed
mkdir -p alerts
mkdir -p grafana/provisioning
mkdir -p backups

chmod -R 755 data data_drop alerts grafana backups

echo -e "${GREEN}✅ Répertoires créés${NC}"
echo ""

# ============================================================================
# 3. Build Images
# ============================================================================

echo -e "${YELLOW}3. Build images Docker...${NC}"

docker compose -f docker-compose-full.yml build

echo -e "${GREEN}✅ Images buildées${NC}"
echo ""

# ============================================================================
# 4. Démarrage Infrastructure
# ============================================================================

echo -e "${YELLOW}4. Démarrage infrastructure (PostgreSQL, Redis, MinIO)...${NC}"

docker compose -f docker-compose-full.yml up -d postgres redis minio

echo "Attente démarrage services (30s)..."
sleep 30

# Vérification healthchecks
echo "Vérification healthchecks..."

# PostgreSQL
if docker exec os_postgres pg_isready -U admin -d oceansentinel &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL prêt${NC}"
else
    echo -e "${RED}❌ PostgreSQL non prêt${NC}"
    exit 1
fi

# Redis
if docker exec os_redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✅ Redis prêt${NC}"
else
    echo -e "${RED}❌ Redis non prêt${NC}"
    exit 1
fi

# MinIO
if curl -f http://localhost:9000/minio/health/live &> /dev/null; then
    echo -e "${GREEN}✅ MinIO prêt${NC}"
else
    echo -e "${RED}❌ MinIO non prêt${NC}"
    exit 1
fi

echo ""

# ============================================================================
# 5. Initialisation Base de Données
# ============================================================================

echo -e "${YELLOW}5. Initialisation base de données...${NC}"

# Migrations Alembic
echo "Exécution migrations Alembic..."
docker compose -f docker-compose-full.yml run --rm api alembic upgrade head
echo -e "${GREEN}✅ Migrations exécutées${NC}"

# Seed sources
echo "Seed sources..."
docker compose -f docker-compose-full.yml run --rm api python scripts/seed_sources.py
echo -e "${GREEN}✅ Sources seedées${NC}"

# Init tables pipeline (si script existe)
if [ -f scripts/init_pipeline_tables.sql ]; then
    echo "Initialisation tables pipeline..."
    docker exec -i os_postgres psql -U admin -d oceansentinel < scripts/init_pipeline_tables.sql
    echo -e "${GREEN}✅ Tables pipeline initialisées${NC}"
fi

echo ""

# ============================================================================
# 6. Démarrage Application
# ============================================================================

echo -e "${YELLOW}6. Démarrage application...${NC}"

# API
echo "Démarrage API..."
docker compose -f docker-compose-full.yml up -d api
sleep 10

# Vérification API
if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
    echo -e "${GREEN}✅ API démarrée${NC}"
else
    echo -e "${RED}❌ API non accessible${NC}"
    docker compose -f docker-compose-full.yml logs api
    exit 1
fi

# Orchestrateur
echo "Démarrage orchestrateur..."
docker compose -f docker-compose-full.yml up -d orchestrator
echo -e "${GREEN}✅ Orchestrateur démarré${NC}"

# Workers
echo "Démarrage workers..."
docker compose -f docker-compose-full.yml up -d ingest_worker transform_worker alert_worker
echo -e "${GREEN}✅ Workers démarrés${NC}"

echo ""

# ============================================================================
# 7. Vérifications Finales
# ============================================================================

echo -e "${YELLOW}7. Vérifications finales...${NC}"

# Status conteneurs
echo "Status conteneurs:"
docker compose -f docker-compose-full.yml ps

echo ""

# API Health
echo "API Health:"
curl -s http://localhost:8000/api/v1/health | jq -r '.status'

echo ""

# Pipeline Status
echo "Pipeline Status:"
curl -s http://localhost:8000/api/v1/pipeline/status | jq -r '.database.connected, .sources.active'

echo ""

# ============================================================================
# 8. Résumé
# ============================================================================

echo "=============================================================================="
echo -e "${GREEN}✅ DÉPLOIEMENT TERMINÉ${NC}"
echo "=============================================================================="
echo ""
echo "Services démarrés:"
echo "  - PostgreSQL (TimescaleDB): localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - MinIO: localhost:9000 (console: localhost:9001)"
echo "  - API: http://localhost:8000"
echo ""
echo "Endpoints utiles:"
echo "  - Health: http://localhost:8000/api/v1/health"
echo "  - Pipeline Status: http://localhost:8000/api/v1/pipeline/status"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Commandes utiles:"
echo "  - Logs orchestrateur: docker compose -f docker-compose-full.yml logs -f orchestrator"
echo "  - Logs API: docker compose -f docker-compose-full.yml logs -f api"
echo "  - Status: docker compose -f docker-compose-full.yml ps"
echo "  - Arrêter: docker compose -f docker-compose-full.yml down"
echo ""
echo "Prochaines étapes:"
echo "  1. Vérifier ingestion: docker compose -f docker-compose-full.yml logs -f orchestrator"
echo "  2. Consulter données: docker exec os_postgres psql -U admin -d oceansentinel"
echo "  3. Lancer smoke tests: ./scripts/smoke_tests.sh"
echo ""
echo "=============================================================================="
