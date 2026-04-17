# ============================================================================
# Ocean Sentinel - Déploiement Simple sur VPS
# ============================================================================

$VPS_IP = "76.13.43.3"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "OCEAN SENTINEL - DÉPLOIEMENT SUR VPS $VPS_IP" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Ce script va déployer Ocean Sentinel sur le VPS" -ForegroundColor Yellow
Write-Host "Vous aurez besoin du mot de passe root" -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Continuer ? (o/n)"
if ($continue -ne "o" -and $continue -ne "O") {
    Write-Host "Déploiement annulé" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "DÉPLOIEMENT EN COURS..." -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Connexion au VPS et déploiement..." -ForegroundColor Yellow
Write-Host "Cela peut prendre 3-5 minutes..." -ForegroundColor Yellow
Write-Host ""

# Créer script de déploiement temporaire
$deployScript = @'
#!/bin/bash
set -e

echo "============================================================================"
echo "OCEAN SENTINEL - DÉPLOIEMENT AUTOMATIQUE"
echo "============================================================================"
echo ""

# 1. Installation Docker
echo "=== ÉTAPE 1/5 - Installation Docker ==="
if ! command -v docker &> /dev/null; then
    echo "Installation Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi
apt update && apt install -y docker-compose-plugin git curl jq vim
echo "✅ Docker installé"
echo ""

# 2. Clonage repository
echo "=== ÉTAPE 2/5 - Clonage repository ==="
if [ -d /opt/oceansentinel ]; then
    echo "Sauvegarde ancien répertoire..."
    mv /opt/oceansentinel /opt/oceansentinel.backup.$(date +%Y%m%d_%H%M%S)
fi
mkdir -p /opt/oceansentinel
cd /opt/oceansentinel
git clone https://github.com/oceansentinelle/OS3.0.git .
echo "✅ Repository cloné"
echo ""

# 3. Configuration
echo "=== ÉTAPE 3/5 - Configuration ==="
cp .env.full.example .env

# Générer mots de passe
POSTGRES_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
MINIO_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
API_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

# Configurer .env
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASS/" .env
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$POSTGRES_PASS/" .env
sed -i "s/MINIO_ROOT_PASSWORD=.*/MINIO_ROOT_PASSWORD=$MINIO_PASS/" .env
sed -i "s/API_SECRET_KEY=.*/API_SECRET_KEY=$API_SECRET/" .env

# Activer 2 sources
sed -i 's/ENABLE_ERDDAP_COAST_HF=.*/ENABLE_ERDDAP_COAST_HF=true/' .env
sed -i 's/ENABLE_HUBEAU=.*/ENABLE_HUBEAU=true/' .env
sed -i 's/ENABLE_ERDDAP_SOMLIT=.*/ENABLE_ERDDAP_SOMLIT=false/' .env
sed -i 's/ENABLE_SEANOE_LOADER=.*/ENABLE_SEANOE_LOADER=false/' .env
sed -i 's/ENABLE_SIBA_LOADER=.*/ENABLE_SIBA_LOADER=false/' .env

# Créer répertoires
mkdir -p data/seanoe data_drop/siba/processed alerts grafana/provisioning backups
chmod -R 755 data data_drop alerts grafana backups

# Sauvegarder credentials
cat > /root/.oceansentinel_credentials <<EOF
# Ocean Sentinel Credentials
# Generated: $(date)
POSTGRES_PASSWORD=$POSTGRES_PASS
MINIO_ROOT_PASSWORD=$MINIO_PASS
API_SECRET_KEY=$API_SECRET
EOF
chmod 600 /root/.oceansentinel_credentials

echo "✅ Configuration terminée"
echo ""

# 4. Déploiement
echo "=== ÉTAPE 4/5 - Déploiement application ==="
chmod +x deploy.sh
./deploy.sh
echo "✅ Application déployée"
echo ""

# 5. Validation
echo "=== ÉTAPE 5/5 - Validation ==="
sleep 5
curl -f http://localhost:8000/api/v1/health || echo "⚠️  API pas encore prête"
echo ""

echo "============================================================================"
echo "✅ DÉPLOIEMENT TERMINÉ"
echo "============================================================================"
echo ""
echo "Endpoints:"
echo "  - API Health: http://76.13.43.3:8000/api/v1/health"
echo "  - API Docs: http://76.13.43.3:8000/docs"
echo ""
echo "Credentials sauvegardés dans: /root/.oceansentinel_credentials"
echo ""
'@

# Sauvegarder script localement
$deployScript | Out-File -FilePath "deploy_remote.sh" -Encoding UTF8 -NoNewline

# Transférer et exécuter sur VPS
Write-Host "Transfert du script sur le VPS..." -ForegroundColor Yellow
Get-Content "deploy_remote.sh" | ssh root@$VPS_IP "cat > /tmp/deploy_ocean.sh && chmod +x /tmp/deploy_ocean.sh && /tmp/deploy_ocean.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "✅ DÉPLOIEMENT RÉUSSI !" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "🌊 Ocean Sentinel V3.0 est maintenant en production !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Endpoints:" -ForegroundColor Yellow
    Write-Host "  - API Health:      http://$VPS_IP:8000/api/v1/health" -ForegroundColor Cyan
    Write-Host "  - Pipeline Status: http://$VPS_IP:8000/api/v1/pipeline/status" -ForegroundColor Cyan
    Write-Host "  - API Docs:        http://$VPS_IP:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Test de l'API..." -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod -Uri "http://$VPS_IP:8000/api/v1/health" -TimeoutSec 10
        Write-Host "✅ API opérationnelle: $($health.status)" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  API pas encore accessible (normal, démarrage en cours)" -ForegroundColor Yellow
        Write-Host "Réessayez dans 1-2 minutes: Invoke-RestMethod http://$VPS_IP:8000/api/v1/health" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Credentials sauvegardés sur le VPS dans: /root/.oceansentinel_credentials" -ForegroundColor Green
    Write-Host ""
    Write-Host "Pour récupérer les credentials:" -ForegroundColor Yellow
    Write-Host "  ssh root@$VPS_IP 'cat /root/.oceansentinel_credentials'" -ForegroundColor Cyan
    Write-Host ""
    
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors du déploiement" -ForegroundColor Red
    Write-Host "Vérifiez les logs ci-dessus" -ForegroundColor Yellow
}

# Nettoyer
Remove-Item "deploy_remote.sh" -ErrorAction SilentlyContinue

Write-Host "============================================================================" -ForegroundColor Cyan
