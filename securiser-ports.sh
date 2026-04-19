#!/bin/bash
# Sécurisation automatique des ports Docker Compose
# Ocean Sentinel - ABACODE 2.0
# Usage: bash securiser-ports.sh

set -e
cd /opt/oceansentinel

echo "=========================================="
echo "SÉCURISATION DES PORTS"
echo "=========================================="
echo ""

# Sauvegarde
echo "📦 Sauvegarde..."
mkdir -p backups
cp docker-compose.yml backups/docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)
echo "✅ Sauvegarde créée"
echo ""

# Afficher avant
echo "🔍 AVANT - Ports exposés:"
grep -n "0.0.0.0:" docker-compose.yml || echo "Aucun"
echo ""

# Sécuriser
echo "🔧 Sécurisation..."
sed -i 's/0\.0\.0\.0:/127.0.0.1:/g' docker-compose.yml
echo "✅ Modifications appliquées"
echo ""

# Afficher après
echo "🔍 APRÈS - Ports sécurisés:"
grep -n "127.0.0.1:" docker-compose.yml | grep -E ":(5432|6379|8000|9000)"
echo ""

# Valider
echo "🔍 Validation YAML..."
docker compose config > /dev/null && echo "✅ Syntaxe valide" || echo "❌ Erreur"
echo ""

# Redémarrer
echo "🔄 Redémarrage des services..."
docker compose down
docker compose up -d
echo ""

# Vérifier
echo "🔍 Vérification des ports:"
netstat -tlnp | grep -E ':(5432|6379|8000|9000)' | awk '{print $4}' | sort -u
echo ""

# Test API
echo "🧪 Test API:"
curl -s http://127.0.0.1:8000/health | jq . || curl http://127.0.0.1:8000/health
echo ""

echo "=========================================="
echo "✅ SÉCURISATION TERMINÉE"
echo "=========================================="
