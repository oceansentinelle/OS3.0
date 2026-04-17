# ============================================================================
# Ocean Sentinel V3.0 - Déploiement Proxy Sentinel-3
# ============================================================================

$VPS_IP = "76.13.43.3"
$VPS_USER = "root"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "DÉPLOIEMENT PROXY SENTINEL-3 - OCEAN SENTINEL V3.0" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Transfert du script d'ingestion
Write-Host "1. Transfert du script d'ingestion..." -ForegroundColor Yellow
scp scripts/ingestion_sentinel3.py ${VPS_USER}@${VPS_IP}:/opt/oceansentinel/scripts/

# 2. Transfert des requirements
Write-Host "2. Transfert des dépendances..." -ForegroundColor Yellow
scp requirements-sentinel3.txt ${VPS_USER}@${VPS_IP}:/opt/oceansentinel/

# 3. Transfert du guide
Write-Host "3. Transfert du guide..." -ForegroundColor Yellow
scp SENTINEL3_PROXY_GUIDE.md ${VPS_USER}@${VPS_IP}:/opt/oceansentinel/

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FICHIERS TRANSFÉRÉS AVEC SUCCÈS" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Prochaines étapes (sur le VPS):" -ForegroundColor Yellow
Write-Host ""
Write-Host "ssh ${VPS_USER}@${VPS_IP}" -ForegroundColor White
Write-Host "cd /opt/oceansentinel" -ForegroundColor White
Write-Host "pip3 install -r requirements-sentinel3.txt" -ForegroundColor White
Write-Host "python3 scripts/ingestion_sentinel3.py" -ForegroundColor White
Write-Host ""
Write-Host "Puis rafraîchissez Grafana: http://${VPS_IP}:3000" -ForegroundColor White
Write-Host ""
