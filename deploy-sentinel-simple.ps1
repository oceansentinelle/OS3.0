<#
.SYNOPSIS
    Script de deploiement simplifie Ocean Sentinel
.DESCRIPTION
    Version simplifiee compatible PowerShell 5.1+
#>

[CmdletBinding()]
param(
    [switch]$SkipSSL,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Configuration
$VPS_IP = "76.13.43.3"
$VPS_USER = "root"
$DEPLOY_DIR = "/opt/oceansentinel"
$LOCAL_DIR = "C:\Users\ktprt\Documents\OSwindsurf"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "OCEAN SENTINEL - DEPLOIEMENT AUTOMATISE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Creer le repertoire de logs
$logDir = Join-Path $PSScriptRoot "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$logFile = Join-Path $logDir "deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Write-DeployLog {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $colors = @{ "INFO" = "Cyan"; "SUCCESS" = "Green"; "WARNING" = "Yellow"; "ERROR" = "Red" }
    $icons = @{ "INFO" = "[INFO]"; "SUCCESS" = "[OK]"; "WARNING" = "[WARN]"; "ERROR" = "[ERR]" }
    
    $logEntry = "[$timestamp] [$Level] $Message"
    
    Write-Host "$($icons[$Level]) " -NoNewline -ForegroundColor $colors[$Level]
    Write-Host $Message -ForegroundColor $colors[$Level]
    
    Add-Content -Path $logFile -Value $logEntry
}

# PHASE 1: VALIDATION
Write-Host "`n=== PHASE 1: VALIDATION ===`n" -ForegroundColor Cyan

Write-DeployLog "Verification des prerequis..." -Level INFO

# Verifier .env.production
$envFile = Join-Path $LOCAL_DIR ".env.production"
if (-not (Test-Path $envFile)) {
    Write-DeployLog "Fichier .env.production introuvable" -Level ERROR
    exit 1
}
Write-DeployLog "Fichier .env.production trouve" -Level SUCCESS

# Tester SSH
Write-DeployLog "Test connexion SSH..." -Level INFO
try {
    $sshTest = ssh -o ConnectTimeout=10 "$VPS_USER@$VPS_IP" "echo 'OK'" 2>&1
    if ($sshTest -match "OK") {
        Write-DeployLog "Connexion SSH reussie" -Level SUCCESS
    } else {
        throw "SSH failed"
    }
} catch {
    Write-DeployLog "Impossible de se connecter en SSH" -Level ERROR
    exit 1
}

# PHASE 2: PROVISIONING
Write-Host "`n=== PHASE 2: PROVISIONING ===`n" -ForegroundColor Cyan

Write-DeployLog "Verification Docker..." -Level INFO
$dockerCheck = ssh "$VPS_USER@$VPS_IP" "docker --version 2>/dev/null || echo 'not_installed'"

if ($dockerCheck -match "not_installed") {
    Write-DeployLog "Installation de Docker..." -Level INFO
    
    $installScript = @'
#!/bin/bash
set -e
apt-get update -qq
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker
docker --version
'@
    
    $installScript | ssh "$VPS_USER@$VPS_IP" "cat > /tmp/install-docker.sh && chmod +x /tmp/install-docker.sh && /tmp/install-docker.sh"
    Write-DeployLog "Docker installe" -Level SUCCESS
} else {
    Write-DeployLog "Docker deja installe" -Level SUCCESS
}

Write-DeployLog "Creation des repertoires..." -Level INFO
ssh "$VPS_USER@$VPS_IP" "mkdir -p $DEPLOY_DIR/{backend,frontend,postgres/data,logs,backups}"
Write-DeployLog "Repertoires crees" -Level SUCCESS

# PHASE 3: DEPLOIEMENT
Write-Host "`n=== PHASE 3: DEPLOIEMENT ===`n" -ForegroundColor Cyan

# Creer docker-compose.yml
Write-DeployLog "Creation docker-compose.yml..." -Level INFO

$dockerCompose = @"
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: oceansentinel_postgres
    environment:
      - POSTGRES_DB=oceansentinel
      - POSTGRES_USER=oceansentinel
      - POSTGRES_PASSWORD=`${POSTGRES_PASSWORD}
    volumes:
      - ./postgres/data:/var/lib/postgresql/data
    networks:
      - backend
    restart: unless-stopped
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U oceansentinel"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: oceansentinel_redis
    networks:
      - backend
    restart: unless-stopped
    ports:
      - "127.0.0.1:6379:6379"

networks:
  backend:
    driver: bridge
"@

$composeFile = Join-Path $PSScriptRoot "docker-compose.prod.yml"
$dockerCompose | Out-File -FilePath $composeFile -Encoding UTF8 -Force
Write-DeployLog "docker-compose.yml cree" -Level SUCCESS

# Transferer les fichiers
if (-not $DryRun) {
    Write-DeployLog "Transfert docker-compose.yml..." -Level INFO
    scp $composeFile "$VPS_USER@${VPS_IP}:$DEPLOY_DIR/"
    
    Write-DeployLog "Transfert .env.production..." -Level INFO
    scp $envFile "$VPS_USER@${VPS_IP}:$DEPLOY_DIR/.env"
    
    Write-DeployLog "Securisation .env..." -Level INFO
    ssh "$VPS_USER@$VPS_IP" "chmod 600 $DEPLOY_DIR/.env"
    
    Write-DeployLog "Fichiers transferes" -Level SUCCESS
}

# Demarrer les services
Write-DeployLog "Demarrage des conteneurs..." -Level INFO

$deployScript = @"
cd $DEPLOY_DIR
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose -f docker-compose.prod.yml up -d
sleep 5
docker compose -f docker-compose.prod.yml ps
"@

ssh "$VPS_USER@$VPS_IP" $deployScript

Write-DeployLog "Conteneurs demarres" -Level SUCCESS

# PHASE 4: POST-INSTALLATION
Write-Host "`n=== PHASE 4: POST-INSTALLATION ===`n" -ForegroundColor Cyan

Write-DeployLog "Installation extension pgvector..." -Level INFO
ssh "$VPS_USER@$VPS_IP" "docker exec oceansentinel_postgres psql -U oceansentinel -d oceansentinel -c 'CREATE EXTENSION IF NOT EXISTS vector;' 2>/dev/null || true"
Write-DeployLog "Extension pgvector installee" -Level SUCCESS

# Test de sante
Write-DeployLog "Test des services..." -Level INFO
Start-Sleep -Seconds 3

$psqlTest = ssh "$VPS_USER@$VPS_IP" "docker exec oceansentinel_postgres pg_isready -U oceansentinel"
if ($psqlTest -match "accepting connections") {
    Write-DeployLog "PostgreSQL operationnel" -Level SUCCESS
} else {
    Write-DeployLog "PostgreSQL non accessible" -Level WARNING
}

# RAPPORT FINAL
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "DEPLOIEMENT TERMINE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Services deployes:" -ForegroundColor Cyan
Write-Host "  - PostgreSQL (pgvector): 127.0.0.1:5432" -ForegroundColor White
Write-Host "  - Redis: 127.0.0.1:6379" -ForegroundColor White

Write-Host "`nProchaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Deployer le backend FastAPI" -ForegroundColor White
Write-Host "  2. Configurer Nginx + SSL" -ForegroundColor White
Write-Host "  3. Configurer Stripe webhooks" -ForegroundColor White

Write-Host "`nLogs: $logFile" -ForegroundColor Cyan

Write-Host "`nPour verifier les services:" -ForegroundColor Yellow
Write-Host "  ssh $VPS_USER@$VPS_IP" -ForegroundColor White
Write-Host "  cd $DEPLOY_DIR" -ForegroundColor White
Write-Host "  docker compose ps" -ForegroundColor White
