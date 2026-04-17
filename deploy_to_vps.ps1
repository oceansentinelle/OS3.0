# ============================================================================
# Ocean Sentinel - Déploiement Direct sur VPS
# ============================================================================

$VPS_IP = "76.13.43.3"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "OCEAN SENTINEL - DÉPLOIEMENT SUR VPS $VPS_IP" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Ce script va:" -ForegroundColor Yellow
Write-Host "  1. Se connecter au VPS" -ForegroundColor White
Write-Host "  2. Installer Docker (si nécessaire)" -ForegroundColor White
Write-Host "  3. Cloner le repository" -ForegroundColor White
Write-Host "  4. Configurer l'environnement" -ForegroundColor White
Write-Host "  5. Déployer l'application" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  Vous aurez besoin du mot de passe root du VPS" -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Continuer ? (o/n)"
if ($continue -ne "o" -and $continue -ne "O") {
    Write-Host "Déploiement annulé" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 1 - INSTALLATION DOCKER" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$installScript = @"
#!/bin/bash
set -e

echo '=== Installation Docker ==='

# Vérifier si Docker est déjà installé
if command -v docker &> /dev/null; then
    echo '✅ Docker déjà installé'
    docker --version
else
    echo '📦 Installation Docker...'
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo '✅ Docker installé'
fi

# Vérifier Docker Compose
if docker compose version &> /dev/null; then
    echo '✅ Docker Compose déjà installé'
    docker compose version
else
    echo '📦 Installation Docker Compose...'
    apt update
    apt install -y docker-compose-plugin
    echo '✅ Docker Compose installé'
fi

# Installer outils utiles
apt install -y git curl wget vim htop jq

echo ''
echo '=== Installation terminée ==='
"@

Write-Host "Installation Docker sur le VPS..." -ForegroundColor Yellow
$installScript | ssh root@$VPS_IP "bash -s"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de l'installation Docker" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 2 - CLONAGE REPOSITORY" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$cloneScript = @"
#!/bin/bash
set -e

echo '=== Clonage repository ==='

# Supprimer ancien répertoire si existe
if [ -d /opt/oceansentinel ]; then
    echo '⚠️  Répertoire existant trouvé, sauvegarde...'
    mv /opt/oceansentinel /opt/oceansentinel.backup.\$(date +%Y%m%d_%H%M%S)
fi

# Créer répertoire
mkdir -p /opt/oceansentinel
cd /opt/oceansentinel

# Cloner
echo '📦 Clonage depuis GitHub...'
git clone https://github.com/oceansentinelle/OS3.0.git .

echo '✅ Repository cloné'
ls -la
"@

Write-Host "Clonage du repository..." -ForegroundColor Yellow
$cloneScript | ssh root@$VPS_IP "bash -s"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du clonage" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 3 - CONFIGURATION" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Génération des mots de passe sécurisés..." -ForegroundColor Yellow

# Générer mots de passe
$POSTGRES_PASSWORD = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$MINIO_PASSWORD = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$API_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

Write-Host "✅ Mots de passe générés" -ForegroundColor Green

$configScript = @"
#!/bin/bash
set -e

cd /opt/oceansentinel

echo '=== Configuration .env ==='

# Copier exemple
cp .env.full.example .env

# Remplacer mots de passe
sed -i 's/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/' .env
sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=$POSTGRES_PASSWORD/' .env
sed -i 's/MINIO_ROOT_PASSWORD=.*/MINIO_ROOT_PASSWORD=$MINIO_PASSWORD/' .env
sed -i 's/API_SECRET_KEY=.*/API_SECRET_KEY=$API_SECRET/' .env

# Activer seulement 2 sources au début
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

echo '✅ Configuration terminée'
"@

Write-Host "Configuration de l'environnement..." -ForegroundColor Yellow
$configScript | ssh root@$VPS_IP "bash -s"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la configuration" -ForegroundColor Red
    exit 1
}

# Sauvegarder mots de passe localement
$passwords = @"
# Ocean Sentinel VPS Credentials
# VPS: $VPS_IP
# Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

POSTGRES_PASSWORD=$POSTGRES_PASSWORD
MINIO_ROOT_PASSWORD=$MINIO_PASSWORD
API_SECRET_KEY=$API_SECRET

# IMPORTANT: Gardez ce fichier en sécurité !
"@

$passwords | Out-File -FilePath ".vps_credentials" -Encoding UTF8
Write-Host "💾 Credentials sauvegardés dans .vps_credentials" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 4 - DÉPLOIEMENT" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$deployScript = @"
#!/bin/bash
set -e

cd /opt/oceansentinel

echo '=== Déploiement Ocean Sentinel ==='

# Rendre deploy.sh exécutable
chmod +x deploy.sh

# Lancer déploiement
./deploy.sh

echo ''
echo '=== Déploiement terminé ==='
"@

Write-Host "Lancement du déploiement..." -ForegroundColor Yellow
Write-Host "⏳ Cela peut prendre 2-3 minutes..." -ForegroundColor Yellow
Write-Host ""

$deployScript | ssh root@$VPS_IP "bash -s"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du déploiement" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "ÉTAPE 5 - VALIDATION" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Test de l'API..." -ForegroundColor Yellow
$healthTest = Invoke-RestMethod -Uri "http://$VPS_IP:8000/api/v1/health" -Method Get -ErrorAction SilentlyContinue

if ($healthTest.status -eq "healthy") {
    Write-Host "✅ API opérationnelle !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Status: $($healthTest.status)" -ForegroundColor White
    Write-Host "Version: $($healthTest.version)" -ForegroundColor White
} else {
    Write-Host "⚠️  API démarrée mais status inconnu" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "✅ DÉPLOIEMENT TERMINÉ !" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🌊 Ocean Sentinel V3.0 est maintenant en production !" -ForegroundColor Green
Write-Host ""
Write-Host "Endpoints:" -ForegroundColor Yellow
Write-Host "  - API Health:     http://$VPS_IP:8000/api/v1/health" -ForegroundColor Cyan
Write-Host "  - Pipeline Status: http://$VPS_IP:8000/api/v1/pipeline/status" -ForegroundColor Cyan
Write-Host "  - API Docs:        http://$VPS_IP:8000/docs" -ForegroundColor Cyan
Write-Host ""

Write-Host "Commandes utiles:" -ForegroundColor Yellow
Write-Host "  - Connexion SSH:" -ForegroundColor White
Write-Host "    ssh root@$VPS_IP" -ForegroundColor Cyan
Write-Host ""
Write-Host "  - Voir logs orchestrateur:" -ForegroundColor White
Write-Host "    ssh root@$VPS_IP 'cd /opt/oceansentinel && docker compose -f docker-compose-full.yml logs -f orchestrator'" -ForegroundColor Cyan
Write-Host ""
Write-Host "  - Vérifier données:" -ForegroundColor White
Write-Host '    ssh root@' -NoNewline -ForegroundColor Cyan
Write-Host $VPS_IP -NoNewline -ForegroundColor Cyan
Write-Host ' "docker exec os_postgres psql -U admin -d oceansentinel -c \"SELECT COUNT(*) FROM raw_ingestion_log;\""' -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Credentials sauvegardés dans .vps_credentials" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
