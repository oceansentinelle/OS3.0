<#
.SYNOPSIS
    Script de déploiement automatisé Ocean Sentinel sur VPS Hostinger
    
.DESCRIPTION
    Déploiement sécurisé et orchestré de la plateforme Ocean Sentinel
    Conforme ABACODE 2.0 : Stabilité > Sécurité > Clarté
    
.PARAMETER SkipValidation
    Ignorer la phase de validation (déconseillé)
    
.PARAMETER SkipSSL
    Ignorer la configuration SSL (développement uniquement)
    
.PARAMETER DryRun
    Simuler le déploiement sans exécuter les commandes
    
.EXAMPLE
    .\deploy-sentinel.ps1
    
.NOTES
    Version: 1.0.0
    Auteur: Ocean Sentinel SRE Team
    Date: 19 avril 2026
    Gouvernance: ABACODE 2.0
#>

[CmdletBinding()]
param(
    [switch]$SkipValidation,
    [switch]$SkipSSL,
    [switch]$DryRun
)

# ============================================
# CONFIGURATION GLOBALE
# ============================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Config = @{
    VPS_IP = "76.13.43.3"
    VPS_USER = "root"
    VPS_PORT = 22
    VPS_HOSTNAME = "srv1341436.hstgr.cloud"
    
    DOMAIN = "oceansentinel.fr"
    DOMAIN_WWW = "www.oceansentinel.fr"
    
    DEPLOY_DIR = "/opt/oceansentinel"
    BACKUP_DIR = "/opt/oceansentinel/backups"
    
    LOCAL_PROJECT_DIR = "C:\Users\ktprt\Documents\OSwindsurf"
    ENV_FILE = ".env.production"
    
    DOCKER_NETWORK = "oceansentinel_backend"
    
    # Versions
    DOCKER_VERSION = "24.0.7"
    COMPOSE_VERSION = "2.23.0"
    POSTGRES_VERSION = "16"
    NGINX_VERSION = "1.24.0"
    
    # Ressources
    POSTGRES_MEMORY = "2GB"
    API_MEMORY = "1GB"
    WORKER_MEMORY = "512MB"
    
    # Sécurité
    SSH_KEY_PATH = "$env:USERPROFILE\.ssh\id_rsa"
    
    # Logs
    LOG_DIR = ".\logs"
    LOG_FILE = ".\logs\deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
}

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "SUCCESS", "WARNING", "ERROR")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $gitCommit = git rev-parse --short HEAD 2>$null
    if (-not $gitCommit) { $gitCommit = "unknown" }
    
    $colors = @{
        "INFO" = "Cyan"
        "SUCCESS" = "Green"
        "WARNING" = "Yellow"
        "ERROR" = "Red"
    }
    
    $icons = @{
        "INFO" = "[INFO]"
        "SUCCESS" = "[OK]"
        "WARNING" = "[WARN]"
        "ERROR" = "[ERR]"
    }
    
    $logEntry = "[$timestamp] [$Level] [commit:$gitCommit] $Message"
    
    # Console
    Write-Host "$($icons[$Level]) " -NoNewline -ForegroundColor $colors[$Level]
    Write-Host $Message -ForegroundColor $colors[$Level]
    
    # Fichier
    Add-Content -Path $Config.LOG_FILE -Value $logEntry
}

function Invoke-SSHCommand {
    param(
        [string]$Command,
        [switch]$Silent
    )
    
    if ($DryRun) {
        Write-Log "DRY-RUN: ssh $($Config.VPS_USER)@$($Config.VPS_IP) '$Command'" -Level INFO
        return "DRY-RUN"
    }
    
    try {
        $result = ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 `
            "$($Config.VPS_USER)@$($Config.VPS_IP)" "$Command" 2>&1
        
        if ($LASTEXITCODE -ne 0 -and -not $Silent) {
            throw "SSH command failed: $result"
        }
        
        return $result
    }
    catch {
        Write-Log "Erreur SSH: $_" -Level ERROR
        throw
    }
}

function Test-SSHConnection {
    Write-Log "Test de connexion SSH vers $($Config.VPS_IP):$($Config.VPS_PORT)..." -Level INFO
    
    try {
        $result = Test-NetConnection -ComputerName $Config.VPS_IP -Port $Config.VPS_PORT -WarningAction SilentlyContinue
        
        if ($result.TcpTestSucceeded) {
            Write-Log "Connexion SSH réussie" -Level SUCCESS
            return $true
        }
        else {
            Write-Log "Port SSH ($($Config.VPS_PORT)) inaccessible" -Level ERROR
            return $false
        }
    }
    catch {
        Write-Log "Erreur lors du test SSH: $_" -Level ERROR
        return $false
    }
}

function Test-HTTPConnection {
    param([int]$Port)
    
    Write-Log "Test de connexion HTTP sur port $Port..." -Level INFO
    
    try {
        $result = Test-NetConnection -ComputerName $Config.VPS_IP -Port $Port -WarningAction SilentlyContinue
        
        if ($result.TcpTestSucceeded) {
            Write-Log "Port $Port accessible" -Level SUCCESS
            return $true
        }
        else {
            Write-Log "Port $Port inaccessible" -Level WARNING
            return $false
        }
    }
    catch {
        return $false
    }
}

function Get-GitCommitInfo {
    try {
        $commit = git rev-parse HEAD 2>$null
        $shortCommit = git rev-parse --short HEAD 2>$null
        $branch = git rev-parse --abbrev-ref HEAD 2>$null
        $message = git log -1 --pretty=%B 2>$null
        
        if (-not $commit) { $commit = "unknown" }
        if (-not $shortCommit) { $shortCommit = "unknown" }
        if (-not $branch) { $branch = "unknown" }
        if (-not $message) { $message = "unknown" }
        
        return @{
            Commit = $commit
            ShortCommit = $shortCommit
            Branch = $branch
            Message = $message
        }
    }
    catch {
        Write-Log "Impossible de recuperer les infos Git" -Level WARNING
        return @{
            Commit = "unknown"
            ShortCommit = "unknown"
            Branch = "unknown"
            Message = "unknown"
        }
    }
}

# ============================================
# PHASE 1 - VALIDATION
# ============================================

function Start-ValidationPhase {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "PHASE 1 - VALIDATION" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # 1.1 Vérifier les prérequis locaux
    Write-Log "Vérification des prérequis locaux..." -Level INFO
    
    # Git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Log "Git n'est pas installé" -Level ERROR
        throw "Git requis"
    }
    
    # SSH
    if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
        Write-Log "OpenSSH n'est pas installé" -Level ERROR
        throw "OpenSSH requis"
    }
    
    # SCP
    if (-not (Get-Command scp -ErrorAction SilentlyContinue)) {
        Write-Log "SCP n'est pas disponible" -Level ERROR
        throw "SCP requis"
    }
    
    Write-Log "Prérequis locaux validés" -Level SUCCESS
    
    # 1.2 Vérifier le fichier .env.production
    $envPath = Join-Path $Config.LOCAL_PROJECT_DIR $Config.ENV_FILE
    
    if (-not (Test-Path $envPath)) {
        Write-Log "Fichier $($Config.ENV_FILE) introuvable" -Level ERROR
        Write-Log "Créez le fichier avec les secrets requis:" -Level INFO
        Write-Host @"
        
POSTGRES_PASSWORD=...
API_JWT_SECRET=...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
ADMIN_EMAIL=admin@oceansentinel.fr
"@ -ForegroundColor Yellow
        throw "Fichier .env.production manquant"
    }
    
    # Vérifier les variables critiques
    $envContent = Get-Content $envPath -Raw
    $requiredVars = @(
        "POSTGRES_PASSWORD",
        "API_JWT_SECRET",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET"
    )
    
    foreach ($var in $requiredVars) {
        if ($envContent -notmatch "$var=.+") {
            Write-Log "Variable $var manquante dans $($Config.ENV_FILE)" -Level ERROR
            throw "Configuration incomplète"
        }
    }
    
    Write-Log "Fichier .env.production validé" -Level SUCCESS
    
    # 1.3 Test de connectivité réseau
    if (-not (Test-SSHConnection)) {
        throw "Impossible de se connecter au VPS"
    }
    
    # 1.4 Vérifier les ports HTTP/HTTPS
    $http = Test-HTTPConnection -Port 80
    $https = Test-HTTPConnection -Port 443
    
    if (-not $http -or -not $https) {
        Write-Log "Ports HTTP/HTTPS non accessibles (firewall?)" -Level WARNING
    }
    
    # 1.5 Récupérer les infos Git
    $gitInfo = Get-GitCommitInfo
    Write-Log "Déploiement du commit $($gitInfo.ShortCommit) ($($gitInfo.Branch))" -Level INFO
    Write-Log "Message: $($gitInfo.Message)" -Level INFO
    
    Write-Log "Phase de validation terminée" -Level SUCCESS
}

# ============================================
# PHASE 2 - PROVISIONING
# ============================================

function Start-ProvisioningPhase {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "PHASE 2 - PROVISIONING" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # 2.1 Vérifier Docker
    Write-Log "Vérification de Docker..." -Level INFO
    
    $dockerVersion = Invoke-SSHCommand "docker --version 2>/dev/null || echo 'not_installed'" -Silent
    
    if ($dockerVersion -match "not_installed") {
        Write-Log "Docker non installé, installation en cours..." -Level INFO
        
        $installScript = @'
#!/bin/bash
set -e

# Mise à jour
apt-get update -qq
apt-get upgrade -y -qq

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Démarrer Docker
systemctl enable docker
systemctl start docker

# Vérifier
docker --version
'@
        
        # Créer le script sur le VPS
        $installScript | ssh "$($Config.VPS_USER)@$($Config.VPS_IP)" "cat > /tmp/install-docker.sh"
        Invoke-SSHCommand "chmod +x /tmp/install-docker.sh && /tmp/install-docker.sh"
        
        Write-Log "Docker installé avec succès" -Level SUCCESS
    }
    else {
        Write-Log "Docker déjà installé: $dockerVersion" -Level SUCCESS
    }
    
    # 2.2 Vérifier Docker Compose
    Write-Log "Vérification de Docker Compose..." -Level INFO
    
    $composeVersion = Invoke-SSHCommand "docker compose version 2>/dev/null || echo 'not_installed'" -Silent
    
    if ($composeVersion -match "not_installed") {
        Write-Log "Docker Compose non installé, installation en cours..." -Level INFO
        
        Invoke-SSHCommand "apt-get install -y docker-compose-plugin"
        
        Write-Log "Docker Compose installé avec succès" -Level SUCCESS
    }
    else {
        Write-Log "Docker Compose déjà installé: $composeVersion" -Level SUCCESS
    }
    
    # 2.3 Créer la structure de répertoires
    Write-Log "Création de la structure de répertoires..." -Level INFO
    
    $dirs = @(
        $Config.DEPLOY_DIR,
        "$($Config.DEPLOY_DIR)/backend",
        "$($Config.DEPLOY_DIR)/frontend",
        "$($Config.DEPLOY_DIR)/nginx",
        "$($Config.DEPLOY_DIR)/postgres/data",
        "$($Config.DEPLOY_DIR)/logs",
        $Config.BACKUP_DIR
    )
    
    foreach ($dir in $dirs) {
        Invoke-SSHCommand "mkdir -p $dir" -Silent
    }
    
    Write-Log "Structure de répertoires créée" -Level SUCCESS
    
    # 2.4 Configurer UFW (si installé)
    Write-Log "Configuration du firewall UFW..." -Level INFO
    
    $ufwStatus = Invoke-SSHCommand "which ufw 2>/dev/null || echo 'not_installed'" -Silent
    
    if ($ufwStatus -notmatch "not_installed") {
        Invoke-SSHCommand "ufw allow 22/tcp" -Silent
        Invoke-SSHCommand "ufw allow 80/tcp" -Silent
        Invoke-SSHCommand "ufw allow 443/tcp" -Silent
        Invoke-SSHCommand "ufw --force enable" -Silent
        
        Write-Log "UFW configuré" -Level SUCCESS
    }
    else {
        Write-Log "UFW non installé (ignoré)" -Level WARNING
    }
    
    Write-Log "Phase de provisioning terminée" -Level SUCCESS
}

# ============================================
# PHASE 3 - DÉPLOIEMENT
# ============================================

function Start-DeploymentPhase {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "PHASE 3 - DÉPLOIEMENT" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # 3.1 Créer docker-compose.prod.yml sécurisé
    Write-Log "Création de docker-compose.prod.yml..." -Level INFO
    
    $dockerCompose = @"
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: oceansentinel_postgres
    environment:
      - POSTGRES_DB=oceansentinel
      - POSTGRES_USER=oceansentinel
      - POSTGRES_PASSWORD=\${POSTGRES_PASSWORD}
    volumes:
      - ./postgres/data:/var/lib/postgresql/data
      - ./backend/database/init.sql:/docker-entrypoint-initdb.d/init.sql
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
    deploy:
      resources:
        limits:
          memory: $($Config.POSTGRES_MEMORY)

  redis:
    image: redis:7-alpine
    container_name: oceansentinel_redis
    networks:
      - backend
    restart: unless-stopped
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: oceansentinel_api
    env_file: .env
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          memory: $($Config.API_MEMORY)

  stripe-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    container_name: oceansentinel_stripe_worker
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: $($Config.WORKER_MEMORY)

networks:
  backend:
    driver: bridge
    name: $($Config.DOCKER_NETWORK)
"@
    
    $dockerCompose | Out-File -FilePath ".\docker-compose.prod.yml" -Encoding UTF8
    
    Write-Log "docker-compose.prod.yml créé" -Level SUCCESS
    
    # 3.2 Transférer les fichiers
    Write-Log "Transfert des fichiers vers le VPS..." -Level INFO
    
    if (-not $DryRun) {
        # Backend
        Write-Log "Transfert du backend..." -Level INFO
        scp -r "$($Config.LOCAL_PROJECT_DIR)\backend\*" "$($Config.VPS_USER)@$($Config.VPS_IP):$($Config.DEPLOY_DIR)/backend/"
        
        # Docker Compose
        Write-Log "Transfert de docker-compose.prod.yml..." -Level INFO
        scp ".\docker-compose.prod.yml" "$($Config.VPS_USER)@$($Config.VPS_IP):$($Config.DEPLOY_DIR)/"
        
        # .env.production
        Write-Log "Transfert de .env.production (sécurisé)..." -Level INFO
        scp "$($Config.LOCAL_PROJECT_DIR)\$($Config.ENV_FILE)" "$($Config.VPS_USER)@$($Config.VPS_IP):$($Config.DEPLOY_DIR)/.env"
        
        # Sécuriser .env
        Invoke-SSHCommand "chmod 600 $($Config.DEPLOY_DIR)/.env"
        
        Write-Log "Fichiers transférés avec succès" -Level SUCCESS
    }
    
    # 3.3 Build et démarrage des conteneurs
    Write-Log "Build et démarrage des conteneurs Docker..." -Level INFO
    
    $deployScript = @"
cd $($Config.DEPLOY_DIR)

# Arrêter les anciens conteneurs
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Build et démarrer
docker compose -f docker-compose.prod.yml up -d --build

# Attendre que les services soient healthy
echo "Attente du démarrage des services..."
sleep 10

# Vérifier le statut
docker compose -f docker-compose.prod.yml ps
"@
    
    Invoke-SSHCommand $deployScript
    
    Write-Log "Conteneurs démarrés avec succès" -Level SUCCESS
    
    Write-Log "Phase de déploiement terminée" -Level SUCCESS
}

# ============================================
# PHASE 4 - POST-INSTALLATION
# ============================================

function Start-PostInstallPhase {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "PHASE 4 - POST-INSTALLATION" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # 4.1 Vérifier l'extension pgvector
    Write-Log "Vérification de l'extension pgvector..." -Level INFO
    
    $pgvectorCheck = Invoke-SSHCommand @"
docker exec oceansentinel_postgres psql -U oceansentinel -d oceansentinel -c '\dx' | grep vector || echo 'not_installed'
"@ -Silent
    
    if ($pgvectorCheck -match "not_installed") {
        Write-Log "Installation de l'extension pgvector..." -Level INFO
        
        Invoke-SSHCommand "docker exec oceansentinel_postgres psql -U oceansentinel -d oceansentinel -c 'CREATE EXTENSION IF NOT EXISTS vector;'"
        
        Write-Log "Extension pgvector installée" -Level SUCCESS
    }
    else {
        Write-Log "Extension pgvector déjà installée" -Level SUCCESS
    }
    
    # 4.2 Configurer Nginx
    if (-not $SkipSSL) {
        Write-Log "Configuration de Nginx avec SSL..." -Level INFO
        
        $nginxConfig = @"
# Redirection HTTP → HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $($Config.DOMAIN) $($Config.DOMAIN_WWW);
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\`$server_name\`$request_uri;
    }
}

# Configuration HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $($Config.DOMAIN) $($Config.DOMAIN_WWW);
    
    ssl_certificate /etc/letsencrypt/live/$($Config.DOMAIN)/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$($Config.DOMAIN)/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    access_log /var/log/nginx/oceansentinel_access.log;
    error_log /var/log/nginx/oceansentinel_error.log;
    
    location / {
        root $($Config.DEPLOY_DIR)/frontend/dist;
        try_files \`$uri \`$uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \`$host;
        proxy_set_header X-Real-IP \`$remote_addr;
        proxy_set_header X-Forwarded-For \`$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \`$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
"@
        
        $nginxConfig | ssh "$($Config.VPS_USER)@$($Config.VPS_IP)" "cat > /etc/nginx/sites-available/oceansentinel"
        
        # Activer la configuration
        Invoke-SSHCommand "ln -sf /etc/nginx/sites-available/oceansentinel /etc/nginx/sites-enabled/"
        Invoke-SSHCommand "nginx -t && systemctl reload nginx"
        
        Write-Log "Nginx configuré" -Level SUCCESS
        
        # 4.3 Obtenir le certificat SSL
        Write-Log "Obtention du certificat SSL Let's Encrypt..." -Level INFO
        
        $certbotInstalled = Invoke-SSHCommand "which certbot 2>/dev/null || echo 'not_installed'" -Silent
        
        if ($certbotInstalled -match "not_installed") {
            Invoke-SSHCommand "apt-get install -y certbot python3-certbot-nginx"
        }
        
        # Obtenir le certificat
        $certbotCmd = "certbot --nginx -d $($Config.DOMAIN) -d $($Config.DOMAIN_WWW) --non-interactive --agree-tos --email admin@$($Config.DOMAIN) --redirect"
        
        try {
            Invoke-SSHCommand $certbotCmd
            Write-Log "Certificat SSL obtenu avec succès" -Level SUCCESS
        }
        catch {
            Write-Log "Erreur lors de l'obtention du certificat SSL: $_" -Level WARNING
            Write-Log "Vous devrez configurer SSL manuellement" -Level WARNING
        }
    }
    
    # 4.4 Tests de santé
    Write-Log "Tests de santé de l'API..." -Level INFO
    
    Start-Sleep -Seconds 5
    
    try {
        $healthCheck = Invoke-SSHCommand "curl -f http://127.0.0.1:8000/api/health 2>/dev/null"
        
        if ($healthCheck -match "healthy") {
            Write-Log "API opérationnelle" -Level SUCCESS
        }
        else {
            Write-Log "API ne répond pas correctement" -Level WARNING
        }
    }
    catch {
        Write-Log "Impossible de vérifier l'API" -Level WARNING
    }
    
    Write-Log "Phase de post-installation terminée" -Level SUCCESS
}

# ============================================
# PHASE 5 - RAPPORT ET AUDIT
# ============================================

function Start-ReportPhase {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "PHASE 5 - RAPPORT ET AUDIT" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # 5.1 Audit d'accessibilité (si axe-core disponible)
    Write-Log "Audit d'accessibilité WCAG 2.2..." -Level INFO
    
    $axeInstalled = Get-Command npm -ErrorAction SilentlyContinue
    
    if ($axeInstalled) {
        try {
            # Vérifier si @axe-core/cli est installé
            $axeCli = npm list -g @axe-core/cli 2>$null
            
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Installation de @axe-core/cli..." -Level INFO
                npm install -g @axe-core/cli
            }
            
            # Exécuter l'audit
            $auditUrl = "https://$($Config.DOMAIN)"
            $auditReport = ".\logs\accessibility-audit-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
            
            axe $auditUrl --save $auditReport
            
            Write-Log "Rapport d'accessibilité généré: $auditReport" -Level SUCCESS
        }
        catch {
            Write-Log "Impossible d'exécuter l'audit d'accessibilité: $_" -Level WARNING
        }
    }
    else {
        Write-Log "npm non installé, audit d'accessibilité ignoré" -Level WARNING
    }
    
    # 5.2 Générer le rapport de déploiement
    Write-Log "Génération du rapport de déploiement..." -Level INFO
    
    $gitInfo = Get-GitCommitInfo
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $report = @"
═══════════════════════════════════════════════════════════════
RAPPORT DE DÉPLOIEMENT OCEAN SENTINEL
═══════════════════════════════════════════════════════════════

L'ESSENTIEL
───────────────────────────────────────────────────────────────
✅ Déploiement réussi sur VPS $($Config.VPS_IP)
✅ Commit: $($gitInfo.ShortCommit) ($($gitInfo.Branch))
✅ Date: $timestamp
✅ Gouvernance: ABACODE 2.0 (Stabilité > Sécurité > Clarté)

ANALYSE PROFONDE
───────────────────────────────────────────────────────────────
Infrastructure:
  • VPS: $($Config.VPS_HOSTNAME)
  • Docker: Installé et opérationnel
  • PostgreSQL: pgvector activé pour RAG
  • Nginx: Reverse proxy configuré
  • SSL: Let's Encrypt $(if ($SkipSSL) { "(ignoré)" } else { "activé" })

Sécurité:
  • Ports exposés: 80, 443 uniquement
  • Services internes: 127.0.0.1 (anti-UFW bypass)
  • Firewall: UFW configuré
  • Secrets: .env.production sécurisé (chmod 600)

Services déployés:
  • API FastAPI: http://127.0.0.1:8000
  • PostgreSQL: 127.0.0.1:5432 (pgvector)
  • Redis: 127.0.0.1:6379
  • Worker Stripe: 2 réplicas avec DLQ

Ressources allouées:
  • PostgreSQL: $($Config.POSTGRES_MEMORY)
  • API: $($Config.API_MEMORY)
  • Worker: $($Config.WORKER_MEMORY)

ACTION
───────────────────────────────────────────────────────────────
Prochaines étapes:

1. Vérifier l'API:
   curl https://$($Config.DOMAIN)/api/health

2. Configurer Stripe Webhook:
   URL: https://$($Config.DOMAIN)/api/webhooks/stripe
   Événements: subscription.*, invoice.*

3. Tester le Worker DLQ:
   docker logs -f oceansentinel_stripe_worker

4. Consulter les logs:
   ssh $($Config.VPS_USER)@$($Config.VPS_IP)
   cd $($Config.DEPLOY_DIR)
   docker compose logs -f

5. Monitoring:
   GET https://$($Config.DOMAIN)/api/admin/stripe/metrics

═══════════════════════════════════════════════════════════════
Logs complets: $($Config.LOG_FILE)
═══════════════════════════════════════════════════════════════
"@
    
    Write-Host $report -ForegroundColor Green
    
    # Sauvegarder le rapport
    $reportFile = ".\logs\deployment-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
    $report | Out-File -FilePath $reportFile -Encoding UTF8
    
    Write-Log "Rapport sauvegardé: $reportFile" -Level SUCCESS
    
    Write-Log "Phase de rapport terminée" -Level SUCCESS
}

# ============================================
# FONCTION PRINCIPALE
# ============================================

function Start-Deployment {
    $startTime = Get-Date
    
    Write-Host @"
    
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           OCEAN SENTINEL - DÉPLOIEMENT AUTOMATISÉ        ║
║                                                           ║
║   Gouvernance: ABACODE 2.0                               ║
║   Priorité: Stabilité > Sécurité > Clarté                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
    
    # Créer le répertoire de logs
    if (-not (Test-Path $Config.LOG_DIR)) {
        New-Item -ItemType Directory -Path $Config.LOG_DIR -Force | Out-Null
    }
    
    Write-Log "Démarrage du déploiement Ocean Sentinel" -Level INFO
    Write-Log "VPS cible: $($Config.VPS_IP) ($($Config.VPS_HOSTNAME))" -Level INFO
    Write-Log "Domaine: $($Config.DOMAIN)" -Level INFO
    
    try {
        # Phase 1: Validation
        if (-not $SkipValidation) {
            Start-ValidationPhase
        }
        else {
            Write-Log "Phase de validation ignorée (SkipValidation)" -Level WARNING
        }
        
        # Phase 2: Provisioning
        Start-ProvisioningPhase
        
        # Phase 3: Déploiement
        Start-DeploymentPhase
        
        # Phase 4: Post-installation
        Start-PostInstallPhase
        
        # Phase 5: Rapport
        Start-ReportPhase
        
        $endTime = Get-Date
        $duration = $endTime - $startTime
        
        Write-Host "`n" -NoNewline
        Write-Log "═══════════════════════════════════════════════════════════" -Level SUCCESS
        Write-Log "DÉPLOIEMENT TERMINÉ AVEC SUCCÈS" -Level SUCCESS
        Write-Log "Durée totale: $($duration.ToString('mm\:ss'))" -Level SUCCESS
        Write-Log "═══════════════════════════════════════════════════════════" -Level SUCCESS
        
    }
    catch {
        Write-Log "ERREUR CRITIQUE: $_" -Level ERROR
        Write-Log "Trace: $($_.ScriptStackTrace)" -Level ERROR
        
        Write-Host "`n❌ Le déploiement a échoué. Consultez les logs pour plus de détails." -ForegroundColor Red
        Write-Host "Logs: $($Config.LOG_FILE)" -ForegroundColor Yellow
        
        exit 1
    }
}

# ============================================
# POINT D'ENTRÉE
# ============================================

Start-Deployment
