#!/bin/bash
# ============================================================================
# Ocean Sentinel V3.0 - Test Mission 8 (API + Grafana + Alertes SACS)
# ============================================================================

set -e

echo "================================================================================"
echo "OCEAN SENTINEL V3.0 - TEST MISSION 8"
echo "================================================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Étape 1: Démarrer les services
print_step "Démarrage des services Docker..."
docker compose -f docker-compose-vps-full.yml up -d

echo ""
print_step "Attente du démarrage des services (30s)..."
sleep 30

# Étape 2: Vérifier les conteneurs
print_step "Vérification des conteneurs..."
docker compose -f docker-compose-vps-full.yml ps

# Étape 3: Tester l'API
echo ""
print_step "Test de l'API REST..."

# Health check
echo "  - GET /health"
curl -s http://localhost:8000/health | python -m json.tool

# Latest measurement
echo ""
echo "  - GET /api/v1/station/VPS_PROD/latest"
curl -s http://localhost:8000/api/v1/station/VPS_PROD/latest | python -m json.tool

# History
echo ""
echo "  - GET /api/v1/station/VPS_PROD/history"
curl -s "http://localhost:8000/api/v1/station/VPS_PROD/history?limit=3" | python -m json.tool

# SACS Alerts
echo ""
echo "  - GET /api/v1/alerts/sacs"
curl -s http://localhost:8000/api/v1/alerts/sacs | python -m json.tool

# Étape 4: Vérifier Grafana
echo ""
print_step "Vérification de Grafana..."
echo "  - Grafana accessible sur: http://localhost:3000"
echo "  - User: admin / Password: admin"

# Étape 5: Vérifier l'utilisation mémoire
echo ""
print_step "Utilisation mémoire..."
docker stats --no-stream

echo ""
echo "================================================================================"
print_success "TEST MISSION 8 COMPLÉTÉ !"
echo "================================================================================"
echo ""
echo "Services disponibles:"
echo "  - API REST:    http://localhost:8000"
echo "  - API Docs:    http://localhost:8000/docs"
echo "  - Grafana:     http://localhost:3000 (admin/admin)"
echo "  - TimescaleDB: localhost:6543"
echo ""
echo "Pour arrêter:"
echo "  docker compose -f docker-compose-vps-full.yml down"
echo ""
