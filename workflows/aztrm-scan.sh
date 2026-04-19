#!/bin/bash
set -e

echo "🔒 AZTRM-D Pre-Commit Security Scan"
echo "===================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo "📝 [1/8] Linting Python..."
if pylint backend/ --exit-zero --score=y | grep "Your code has been rated"; then
    echo -e "${GREEN}✓ Linting Python OK${NC}"
else
    echo -e "${RED}✗ Linting Python FAILED${NC}"
    ((ERRORS++))
fi
echo ""

echo "🔍 [2/8] Type Checking..."
if mypy backend/ --strict --ignore-missing-imports; then
    echo -e "${GREEN}✓ Type Checking OK${NC}"
else
    echo -e "${RED}✗ Type Checking FAILED${NC}"
    ((ERRORS++))
fi
echo ""

echo "🧪 [3/8] Tests Unitaires..."
if pytest backend/tests/ -v --cov=backend --cov-fail-under=80 -q; then
    echo -e "${GREEN}✓ Tests OK${NC}"
else
    echo -e "${RED}✗ Tests FAILED${NC}"
    ((ERRORS++))
fi
echo ""

echo "🔐 [4/8] Détection de Secrets..."
if git diff --name-only --cached | xargs -r detect-secrets-hook --baseline .secrets.baseline; then
    echo -e "${GREEN}✓ Aucun secret détecté${NC}"
else
    echo -e "${RED}✗ SECRETS DÉTECTÉS - COMMIT BLOQUÉ${NC}"
    ((ERRORS++))
fi
echo ""

echo "📦 [5/8] Scan de Dépendances..."
if safety check --file requirements.txt --json > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Dépendances sécurisées${NC}"
else
    echo -e "${YELLOW}⚠ Vulnérabilités détectées${NC}"
    safety check --file requirements.txt
    ((WARNINGS++))
fi
echo ""

echo "🛡️ [6/8] Analyse SAST (Semgrep)..."
if command -v semgrep &> /dev/null; then
    if semgrep --config=auto backend/ --severity=ERROR --quiet; then
        echo -e "${GREEN}✓ SAST OK${NC}"
    else
        echo -e "${RED}✗ Vulnérabilités SAST détectées${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠ Semgrep non installé (ignoré)${NC}"
fi
echo ""

echo "🐍 [7/8] Bandit Security Scan..."
if command -v bandit &> /dev/null; then
    if bandit -r backend/ -ll -q; then
        echo -e "${GREEN}✓ Bandit OK${NC}"
    else
        echo -e "${YELLOW}⚠ Problèmes de sécurité détectés${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠ Bandit non installé (ignoré)${NC}"
fi
echo ""

echo "🐳 [8/8] Docker Linting..."
if command -v hadolint &> /dev/null; then
    if find . -name "Dockerfile*" -exec hadolint {} \; 2>&1 | grep -q "error"; then
        echo -e "${YELLOW}⚠ Problèmes Dockerfile détectés${NC}"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓ Dockerfiles OK${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Hadolint non installé (ignoré)${NC}"
fi
echo ""

echo "===================================="
echo "📊 Résumé du Scan"
echo "===================================="
echo -e "Erreurs critiques : ${RED}${ERRORS}${NC}"
echo -e "Avertissements : ${YELLOW}${WARNINGS}${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ SCAN ÉCHOUÉ - Commit bloqué${NC}"
    echo "Corrigez les erreurs critiques avant de commiter."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️ SCAN RÉUSSI AVEC AVERTISSEMENTS${NC}"
    echo "Considérez corriger les avertissements."
    exit 0
else
    echo -e "${GREEN}✅ SCAN RÉUSSI - Code prêt pour commit${NC}"
    exit 0
fi
