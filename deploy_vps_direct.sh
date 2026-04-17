#!/bin/bash
# ============================================================================
# Ocean Sentinel V3.0 - Déploiement Direct sur VPS
# ============================================================================

set -e

echo "============================================================================"
echo "OCEAN SENTINEL V3.0 - DÉPLOIEMENT AUTOMATIQUE"
echo "============================================================================"
echo ""

# 1. Installation Docker
echo "=== ÉTAPE 1/5 - Installation Docker ==="
if ! command -v docker &> /dev/null; then
    echo "📦 Installation Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installé"
else
    echo "✅ Docker déjà installé"
    docker --version
fi

# Docker Compose
if ! docker compose version &> /dev/null; then
    echo "📦 Installation Docker Compose..."
    apt update
    apt install -y docker-compose-plugin
    echo "✅ Docker Compose installé"
else
    echo "✅ Docker Compose déjà installé"
    docker compose version
fi

# Outils utiles
apt install -y git curl jq vim htop net-tools

echo ""

# 2. Clonage repository
echo "=== ÉTAPE 2/5 - Clonage repository ==="
if [ -d /opt/oceansentinel ]; then
    echo "⚠️  Répertoire existant trouvé, sauvegarde..."
    mv /opt/oceansentinel /opt/oceansentinel.backup.$(date +%Y%m%d_%H%M%S)
fi

mkdir -p /opt/oceansentinel
cd /opt/oceansentinel

echo "📦 Clonage depuis GitHub..."
git clone https://github.com/oceansentinelle/OS3.0.git .

echo "✅ Repository cloné"
ls -la

echo ""

# 3. Configuration
echo "=== ÉTAPE 3/5 - Configuration ==="

# Copier .env
cp .env.full.example .env

# Générer mots de passe sécurisés
echo "🔐 Génération mots de passe sécurisés..."
POSTGRES_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
MINIO_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
API_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

# Configurer .env
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASS/" .env
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$POSTGRES_PASS/" .env
sed -i "s/MINIO_ROOT_PASSWORD=.*/MINIO_ROOT_PASSWORD=$MINIO_PASS/" .env
sed -i "s/API_SECRET_KEY=.*/API_SECRET_KEY=$API_SECRET/" .env

# Activer seulement 2 sources au début
echo "📡 Activation sources (ERDDAP COAST-HF, Hub'Eau)..."
sed -i 's/ENABLE_ERDDAP_COAST_HF=.*/ENABLE_ERDDAP_COAST_HF=true/' .env
sed -i 's/ENABLE_HUBEAU=.*/ENABLE_HUBEAU=true/' .env
sed -i 's/ENABLE_ERDDAP_SOMLIT=.*/ENABLE_ERDDAP_SOMLIT=false/' .env
sed -i 's/ENABLE_SEANOE_LOADER=.*/ENABLE_SEANOE_LOADER=false/' .env
sed -i 's/ENABLE_SIBA_LOADER=.*/ENABLE_SIBA_LOADER=false/' .env
sed -i 's/ENABLE_SHOM_REFERENCE=.*/ENABLE_SHOM_REFERENCE=false/' .env
sed -i 's/ENABLE_INSEE_GEO=.*/ENABLE_INSEE_GEO=false/' .env
sed -i 's/ENABLE_INSEE_SIRENE=.*/ENABLE_INSEE_SIRENE=false/' .env

# Créer répertoires
mkdir -p data/seanoe data_drop/siba/processed alerts grafana/provisioning backups
chmod -R 755 data data_drop alerts grafana backups

# Sauvegarder credentials
cat > /root/.oceansentinel_credentials <<EOF
# ============================================================================
# Ocean Sentinel V3.0 - Credentials
# ============================================================================
# Généré: $(date)
# VPS: 76.13.43.3
# ============================================================================

POSTGRES_PASSWORD=$POSTGRES_PASS
MINIO_ROOT_PASSWORD=$MINIO_PASS
API_SECRET_KEY=$API_SECRET

# ============================================================================
# IMPORTANT: Gardez ce fichier en sécurité !
# ============================================================================
EOF

chmod 600 /root/.oceansentinel_credentials

echo "✅ Configuration terminée"
echo "💾 Credentials sauvegardés dans /root/.oceansentinel_credentials"

echo ""

# 4. Déploiement
echo "=== ÉTAPE 4/5 - Déploiement application ==="
echo "⏳ Cela peut prendre 2-3 minutes..."
echo ""

chmod +x deploy.sh
./deploy.sh

echo ""
echo "✅ Application déployée"

echo ""

# 5. Validation
echo "=== ÉTAPE 5/5 - Validation ==="
echo "⏳ Attente démarrage API (10s)..."
sleep 10

echo ""
echo "Test API Health..."
if curl -f http://localhost:8000/api/v1/health 2>/dev/null; then
    echo "✅ API opérationnelle"
else
    echo "⚠️  API pas encore prête (normal, démarrage en cours)"
    echo "Réessayez dans 1-2 minutes: curl http://localhost:8000/api/v1/health"
fi

echo ""

# 6. Résumé
echo "============================================================================"
echo "✅ DÉPLOIEMENT TERMINÉ !"
echo "============================================================================"
echo ""
echo "🌊 Ocean Sentinel V3.0 est maintenant en production !"
echo ""
echo "Endpoints:"
echo "  - API Health:      http://76.13.43.3:8000/api/v1/health"
echo "  - Pipeline Status: http://76.13.43.3:8000/api/v1/pipeline/status"
echo "  - API Docs:        http://76.13.43.3:8000/docs"
echo "  - MinIO Console:   http://76.13.43.3:9001"
echo ""
echo "Credentials:"
echo "  - Fichier: /root/.oceansentinel_credentials"
echo "  - Commande: cat /root/.oceansentinel_credentials"
echo ""
echo "Commandes utiles:"
echo "  - Logs orchestrateur: docker compose -f docker-compose-full.yml logs -f orchestrator"
echo "  - Logs API: docker compose -f docker-compose-full.yml logs -f api"
echo "  - Status: docker compose -f docker-compose-full.yml ps"
echo "  - Données: docker exec os_postgres psql -U admin -d oceansentinel"
echo ""
echo "Sources activées:"
echo "  ✅ ERDDAP COAST-HF (Arcachon, Ferret)"
echo "  ✅ Hub'Eau (Qualité eau)"
echo ""
echo "⏳ Premières ingestions attendues dans 10-15 minutes"
echo ""
echo "============================================================================"
