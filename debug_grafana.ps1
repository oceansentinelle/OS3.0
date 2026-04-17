# ============================================================================
# Script de Debug Grafana - Ocean Sentinel V3.0
# ============================================================================

$VPS_IP = "76.13.43.3"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "DEBUG GRAFANA - OCEAN SENTINEL V3.0" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier les données dans TimescaleDB
Write-Host "1. Vérification des données dans TimescaleDB..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Commande à exécuter sur le VPS:" -ForegroundColor Green
Write-Host "ssh root@$VPS_IP" -ForegroundColor White
Write-Host ""
Write-Host "Puis:" -ForegroundColor Green
Write-Host "docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c `"SELECT COUNT(*), MIN(time), MAX(time) FROM ocean_data;`"" -ForegroundColor White
Write-Host ""

# 2. Vérifier l'UID de la datasource
Write-Host "2. Vérification de l'UID de la datasource Grafana..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Commande à exécuter sur le VPS:" -ForegroundColor Green
Write-Host "docker compose -f /opt/oceansentinel/docker-compose-vps.yml logs grafana | grep -i `"datasource`"" -ForegroundColor White
Write-Host ""

# 3. Tester l'API REST
Write-Host "3. Test de l'API REST..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Commande:" -ForegroundColor Green
Write-Host "curl http://$VPS_IP:8000/api/v1/station/VPS_PROD/latest" -ForegroundColor White
Write-Host ""

# 4. Instructions pour corriger l'UID
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "INSTRUCTIONS DE CORRECTION" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Si l'UID de la datasource est différent de celui dans le dashboard:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Connectez-vous à Grafana: http://$VPS_IP:3000" -ForegroundColor White
Write-Host "2. Allez dans Connections > Data sources > TimescaleDB" -ForegroundColor White
Write-Host "3. Notez l'UID dans l'URL (ex: P6E30C3D4FAD99E12)" -ForegroundColor White
Write-Host "4. Éditez le dashboard et remplacez l'UID dans chaque panneau" -ForegroundColor White
Write-Host ""
Write-Host "OU" -ForegroundColor Yellow
Write-Host ""
Write-Host "Modifiez le fichier grafana/provisioning/dashboards/ocean_sentinel.json" -ForegroundColor White
Write-Host "Remplacez toutes les occurrences de l'ancien UID par le nouveau" -ForegroundColor White
Write-Host "Puis redémarrez Grafana:" -ForegroundColor White
Write-Host "docker compose -f /opt/oceansentinel/docker-compose-vps.yml restart grafana" -ForegroundColor White
Write-Host ""
