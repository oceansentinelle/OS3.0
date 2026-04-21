#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Déploiement rapide Ocean Sentinel sur VPS
.DESCRIPTION
    Synchronise code local → VPS et redémarre services
.PARAMETER Component
    Composant à déployer : workers, api, frontend, all
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('workers', 'api', 'frontend', 'all')]
    [string]$Component = 'workers'
)

$VPS_HOST = "root@76.13.43.3"
$VPS_PATH = "/opt/oceansentinel"
$LOCAL_PATH = "C:\Users\ktprt\Documents\OSwindsurf"

Write-Host "🚀 Ocean Sentinel - Déploiement $Component" -ForegroundColor Cyan

switch ($Component) {
    'workers' {
        Write-Host "📦 Synchronisation workers..." -ForegroundColor Yellow
        scp -r "$LOCAL_PATH\workers" "${VPS_HOST}:${VPS_PATH}/"
        
        Write-Host "🔨 Rebuild orchestrator..." -ForegroundColor Yellow
        ssh $VPS_HOST "cd $VPS_PATH && docker compose build orchestrator"
        
        Write-Host "♻️ Redémarrage orchestrator..." -ForegroundColor Yellow
        ssh $VPS_HOST "cd $VPS_PATH && docker compose restart orchestrator"
    }
    
    'api' {
        Write-Host "📦 Synchronisation API..." -ForegroundColor Yellow
        scp -r "$LOCAL_PATH\api" "${VPS_HOST}:${VPS_PATH}/"
        
        Write-Host "🔨 Rebuild API..." -ForegroundColor Yellow
        ssh $VPS_HOST "cd $VPS_PATH && docker compose build api"
        
        Write-Host "♻️ Redémarrage API..." -ForegroundColor Yellow
        ssh $VPS_HOST "cd $VPS_PATH && docker compose restart api"
    }
    
    'frontend' {
        Write-Host "📦 Synchronisation frontend..." -ForegroundColor Yellow
        scp -r "$LOCAL_PATH\frontend" "${VPS_HOST}:${VPS_PATH}/"
        
        Write-Host "♻️ Reload Nginx..." -ForegroundColor Yellow
        ssh $VPS_HOST "nginx -s reload"
    }
    
    'all' {
        Write-Host "📦 Synchronisation complète..." -ForegroundColor Yellow
        scp -r "$LOCAL_PATH\workers" "${VPS_HOST}:${VPS_PATH}/"
        scp -r "$LOCAL_PATH\api" "${VPS_HOST}:${VPS_PATH}/"
        scp -r "$LOCAL_PATH\frontend" "${VPS_HOST}:${VPS_PATH}/"
        
        Write-Host "🔨 Rebuild services..." -ForegroundColor Yellow
        ssh $VPS_HOST "cd $VPS_PATH && docker compose build"
        
        Write-Host "♻️ Redémarrage services..." -ForegroundColor Yellow
        ssh $VPS_HOST "cd $VPS_PATH && docker compose restart"
    }
}

Write-Host ""
Write-Host "✅ Déploiement terminé !" -ForegroundColor Green
Write-Host ""
Write-Host "📊 État services :" -ForegroundColor Cyan
ssh $VPS_HOST "docker ps --format 'table {{.Names}}\t{{.Status}}'"

Write-Host ""
Write-Host "📈 Dernières ingestions :" -ForegroundColor Cyan
ssh $VPS_HOST "docker exec os_postgres psql -U admin -d oceansentinel -c 'SELECT source_name, status, fetched_at FROM raw_ingestion_log ORDER BY fetched_at DESC LIMIT 5;'"
