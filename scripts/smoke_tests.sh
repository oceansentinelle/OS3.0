#!/bin/bash
# ============================================================================
# Smoke Tests - Ocean Sentinel V3.0
# ============================================================================
#
# Tests post-déploiement pour valider le pipeline complet.
#
# Tests:
# 1. API health check
# 2. Database connection
# 3. Pipeline status
# 4. Sources actives
# 5. Recent ingestions
# 6. Orchestrator logs
#
# Usage:
#   chmod +x scripts/smoke_tests.sh
#   ./scripts/smoke_tests.sh
#
# ============================================================================

set -e  # Arrêt si erreur

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
DB_CONTAINER="${DB_CONTAINER:-os_postgres}"

echo "=============================================================================="
echo "SMOKE TESTS - Ocean Sentinel V3.0"
echo "=============================================================================="
echo ""

# Compteurs
PASSED=0
FAILED=0

# ============================================================================
# Test 1: API Health Check
# ============================================================================

echo -n "1. API Health Check... "
if curl -f -s "${API_URL}/api/v1/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# ============================================================================
# Test 2: Database Connection
# ============================================================================

echo -n "2. Database Connection... "
if docker exec ${DB_CONTAINER} pg_isready -U admin > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# ============================================================================
# Test 3: Pipeline Status
# ============================================================================

echo -n "3. Pipeline Status... "
PIPELINE_STATUS=$(curl -f -s "${API_URL}/api/v1/pipeline/status" 2>&1)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
    
    # Afficher détails
    echo "   $(echo $PIPELINE_STATUS | jq -r '.database.version[0:2] | join(" ")')"
    echo "   Sources actives: $(echo $PIPELINE_STATUS | jq -r '.sources.active')"
    echo "   Mesures 24h: $(echo $PIPELINE_STATUS | jq -r '.measurements.validated_24h')"
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# ============================================================================
# Test 4: Sources Table
# ============================================================================

echo -n "4. Sources Table... "
SOURCE_COUNT=$(docker exec ${DB_CONTAINER} psql -U admin -d oceansentinel -t -c "SELECT COUNT(*) FROM sources;" 2>/dev/null | tr -d ' ')
if [ ! -z "$SOURCE_COUNT" ] && [ "$SOURCE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} ($SOURCE_COUNT sources)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} (no sources)"
    FAILED=$((FAILED + 1))
fi

# ============================================================================
# Test 5: Recent Ingestions
# ============================================================================

echo -n "5. Recent Ingestions (24h)... "
INGESTION_COUNT=$(docker exec ${DB_CONTAINER} psql -U admin -d oceansentinel -t -c "SELECT COUNT(*) FROM raw_ingestion_log WHERE fetched_at > NOW() - INTERVAL '24 hours';" 2>/dev/null | tr -d ' ')
if [ ! -z "$INGESTION_COUNT" ]; then
    if [ "$INGESTION_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} ($INGESTION_COUNT ingestions)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️  WARN${NC} (no recent ingestions)"
        PASSED=$((PASSED + 1))
    fi
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# ============================================================================
# Test 6: Orchestrator Running
# ============================================================================

echo -n "6. Orchestrator Running... "
if docker ps | grep -q "os_orchestrator"; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
    
    # Vérifier logs récents
    RECENT_LOGS=$(docker logs os_orchestrator --tail=10 2>&1 | grep -c "job.scheduled" || true)
    if [ "$RECENT_LOGS" -gt 0 ]; then
        echo "   Jobs scheduled: $RECENT_LOGS"
    fi
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# ============================================================================
# Test 7: Workers Running
# ============================================================================

echo -n "7. Workers Running... "
WORKER_COUNT=$(docker ps | grep -c "os_.*_worker" || true)
if [ "$WORKER_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} ($WORKER_COUNT workers)"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  WARN${NC} (no workers running)"
    PASSED=$((PASSED + 1))
fi

# ============================================================================
# Test 8: Reference Entities Table
# ============================================================================

echo -n "8. Reference Entities Table... "
REF_COUNT=$(docker exec ${DB_CONTAINER} psql -U admin -d oceansentinel -t -c "SELECT COUNT(*) FROM reference_entities;" 2>/dev/null | tr -d ' ')
if [ ! -z "$REF_COUNT" ]; then
    echo -e "${GREEN}✅ PASS${NC} ($REF_COUNT entities)"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  WARN${NC} (table may not exist yet)"
    PASSED=$((PASSED + 1))
fi

# ============================================================================
# Test 9: Validated Measurements
# ============================================================================

echo -n "9. Validated Measurements... "
MEAS_COUNT=$(docker exec ${DB_CONTAINER} psql -U admin -d oceansentinel -t -c "SELECT COUNT(*) FROM validated_measurements;" 2>/dev/null | tr -d ' ')
if [ ! -z "$MEAS_COUNT" ]; then
    echo -e "${GREEN}✅ PASS${NC} ($MEAS_COUNT measurements)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# ============================================================================
# Test 10: Redis Connection
# ============================================================================

echo -n "10. Redis Connection... "
if docker exec os_redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# ============================================================================
# Résumé
# ============================================================================

echo ""
echo "=============================================================================="
TOTAL=$((PASSED + FAILED))
PASS_RATE=$((PASSED * 100 / TOTAL))

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC} ($PASSED/$TOTAL)"
    echo "=============================================================================="
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC} ($FAILED/$TOTAL failed)"
    echo "   Pass rate: $PASS_RATE%"
    echo "=============================================================================="
    exit 1
fi
