# ============================================================================
# Ocean Sentinel V3.0 - Script de Déploiement Mission 9 (PowerShell)
# ============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "OCEAN SENTINEL V3.0 - DÉPLOIEMENT MISSION 9" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$VPS_IP = "76.13.43.3"
$SSH_PORT = "22"
$SSH_USER = "root"
$REMOTE_DIR = "/opt/oceansentinel"

Write-Host "Configuration:" -ForegroundColor Blue
Write-Host "  VPS IP: $VPS_IP"
Write-Host "  SSH Port: $SSH_PORT"
Write-Host "  Remote Dir: $REMOTE_DIR"
Write-Host ""

# Vérifier que nous sommes dans le bon répertoire
if (-not (Test-Path "docker-compose-vps-full.yml")) {
    Write-Host "❌ Erreur: docker-compose-vps-full.yml introuvable" -ForegroundColor Red
    Write-Host "   Assurez-vous d'être dans C:\Users\ktprt\Documents\OSwindsurf" -ForegroundColor Yellow
    exit 1
}

Write-Host "▶ Transfert des fichiers vers le VPS..." -ForegroundColor Blue
Write-Host ""

# Transférer docker-compose-vps-full.yml
Write-Host "  - Transfert de docker-compose-vps-full.yml" -ForegroundColor White
scp -P $SSH_PORT docker-compose-vps-full.yml ${SSH_USER}@${VPS_IP}:${REMOTE_DIR}/

# Transférer Dockerfile.api
Write-Host "  - Transfert de Dockerfile.api" -ForegroundColor White
scp -P $SSH_PORT Dockerfile.api ${SSH_USER}@${VPS_IP}:${REMOTE_DIR}/

# Transférer le dossier api/
Write-Host "  - Transfert du dossier api/" -ForegroundColor White
scp -P $SSH_PORT -r api ${SSH_USER}@${VPS_IP}:${REMOTE_DIR}/

# Transférer le dossier grafana/
Write-Host "  - Transfert du dossier grafana/" -ForegroundColor White
scp -P $SSH_PORT -r grafana ${SSH_USER}@${VPS_IP}:${REMOTE_DIR}/

Write-Host ""
Write-Host "✅ Fichiers transférés avec succès !" -ForegroundColor Green
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PROCHAINES ÉTAPES" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connectez-vous au VPS et exécutez:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ssh root@76.13.43.3" -ForegroundColor White
Write-Host "  cd /opt/oceansentinel" -ForegroundColor White
Write-Host "  docker compose -f docker-compose-vps.yml down" -ForegroundColor White
Write-Host "  cp docker-compose-vps-full.yml docker-compose-vps.yml" -ForegroundColor White
Write-Host "  docker compose -f docker-compose-vps.yml build api" -ForegroundColor White
Write-Host "  docker compose -f docker-compose-vps.yml up -d" -ForegroundColor White
Write-Host "  docker compose -f docker-compose-vps.yml ps" -ForegroundColor White
Write-Host ""
