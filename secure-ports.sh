#!/bin/bash
#
# Script de Sécurisation des Ports Docker Compose
# Ocean Sentinel - ABACODE 2.0
# 
# Objectif: Remplacer tous les ports 0.0.0.0 par 127.0.0.1
# pour éviter l'exposition publique des services internes
#

set -e

COMPOSE_FILE="/opt/oceansentinel/docker-compose.yml"
BACKUP_FILE="/opt/oceansentinel/docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)"

echo "=========================================="
echo "SÉCURISATION DES PORTS DOCKER COMPOSE"
echo "=========================================="
echo ""

# Vérifier que le fichier existe
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ ERREUR: Fichier $COMPOSE_FILE introuvable"
    exit 1
fi

echo "✅ Fichier trouvé: $COMPOSE_FILE"
echo ""

# Créer une sauvegarde
echo "📦 Création d'une sauvegarde..."
cp "$COMPOSE_FILE" "$BACKUP_FILE"
echo "✅ Sauvegarde créée: $BACKUP_FILE"
echo ""

# Afficher les ports actuels
echo "🔍 Ports actuellement exposés:"
grep -n "0.0.0.0:" "$COMPOSE_FILE" || echo "   Aucun port 0.0.0.0 trouvé"
echo ""

# Compter le nombre de remplacements
COUNT=$(grep -c "0.0.0.0:" "$COMPOSE_FILE" || true)

if [ "$COUNT" -eq 0 ]; then
    echo "✅ Aucune modification nécessaire - Tous les ports sont déjà sécurisés"
    exit 0
fi

echo "⚠️  $COUNT port(s) à sécuriser"
echo ""

# Effectuer le remplacement
echo "🔧 Remplacement de 0.0.0.0 par 127.0.0.1..."
sed -i 's/0\.0\.0\.0:/127.0.0.1:/g' "$COMPOSE_FILE"

# Vérifier le résultat
NEW_COUNT=$(grep -c "0.0.0.0:" "$COMPOSE_FILE" || true)

if [ "$NEW_COUNT" -eq 0 ]; then
    echo "✅ Tous les ports ont été sécurisés avec succès!"
else
    echo "⚠️  Attention: $NEW_COUNT port(s) restent exposés"
fi

echo ""
echo "🔍 Nouveaux ports configurés:"
grep -n "127.0.0.1:" "$COMPOSE_FILE"
echo ""

# Valider la syntaxe YAML
echo "🔍 Validation de la syntaxe YAML..."
if command -v docker &> /dev/null; then
    if docker compose -f "$COMPOSE_FILE" config > /dev/null 2>&1; then
        echo "✅ Syntaxe YAML valide"
    else
        echo "❌ ERREUR: Syntaxe YAML invalide"
        echo "   Restauration de la sauvegarde..."
        cp "$BACKUP_FILE" "$COMPOSE_FILE"
        echo "   Sauvegarde restaurée"
        exit 1
    fi
else
    echo "⚠️  Docker non disponible, validation ignorée"
fi

echo ""
echo "=========================================="
echo "✅ SÉCURISATION TERMINÉE"
echo "=========================================="
echo ""
echo "📋 Résumé:"
echo "   - Ports sécurisés: $COUNT"
echo "   - Sauvegarde: $BACKUP_FILE"
echo ""
echo "🚀 Prochaines étapes:"
echo "   1. Redémarrer les services:"
echo "      cd /opt/oceansentinel"
echo "      docker compose down"
echo "      docker compose up -d"
echo ""
echo "   2. Vérifier les ports:"
echo "      docker compose ps"
echo "      netstat -tlnp | grep -E ':(5432|6379|8000)'"
echo ""
echo "   3. Tester l'API:"
echo "      curl http://127.0.0.1:8000/health"
echo ""
echo "⚠️  IMPORTANT: Configurez Nginx comme reverse proxy"
echo "   pour exposer l'API publiquement de manière sécurisée"
echo ""
