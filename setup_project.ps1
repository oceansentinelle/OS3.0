# ============================================================================
# Ocean Sentinel V3.0 - Script d'Installation Automatique (Windows)
# ============================================================================
# Crée l'arborescence complète du projet et vérifie les fichiers
# Usage: .\setup_project.ps1
# ============================================================================

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""
Write-Host "  🌊 OCEAN SENTINEL V3.0 - INSTALLATION AUTOMATIQUE 🌊" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Répertoire racine du projet
$PROJECT_ROOT = $PSScriptRoot
Write-Host "📁 Répertoire du projet: " -NoNewline
Write-Host $PROJECT_ROOT -ForegroundColor Yellow
Write-Host ""

# ============================================================================
# ÉTAPE 1: CRÉATION DE L'ARBORESCENCE
# ============================================================================

Write-Host "═══ [1/5] Création de l'arborescence des dossiers ═══" -ForegroundColor Green
Write-Host ""

$directories = @(
    "data",
    "data/netcdf",
    "data/csv",
    "data/grib2",
    "logs",
    "logs/ingestion",
    "logs/ml",
    "models",
    "models/lstm",
    "models/isolation_forest",
    "backups",
    "scripts",
    "monitoring",
    "monitoring/grafana",
    "monitoring/grafana/dashboards",
    "monitoring/grafana/datasources",
    "nginx",
    "nginx/ssl",
    ".windsurf",
    ".windsurf/skills"
)

$created = 0
$existing = 0

foreach ($dir in $directories) {
    $fullPath = Join-Path $PROJECT_ROOT $dir
    
    if (-Not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  ✓ Créé:    " -ForegroundColor Green -NoNewline
        Write-Host $dir
        $created++
    } else {
        Write-Host "  ○ Existe:  " -ForegroundColor Gray -NoNewline
        Write-Host $dir
        $existing++
    }
}

Write-Host ""
Write-Host "  📊 Résumé: " -NoNewline
Write-Host "$created créé(s), $existing existant(s)" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# ÉTAPE 2: VÉRIFICATION DES FICHIERS CRITIQUES
# ============================================================================

Write-Host "═══ [2/5] Vérification des fichiers critiques ═══" -ForegroundColor Green
Write-Host ""

$criticalFiles = @{
    "docker-compose-v3.yml" = "Configuration Docker Compose V3"
    "docker-compose.yml" = "Configuration Docker Compose (existante)"
    ".env.example" = "Template variables d'environnement"
    "scripts/ingestion_stream.py" = "Script d'ingestion streaming"
    "scripts/ml_pipeline.py" = "Pipeline Machine Learning"
    "scripts/harden_vps.sh" = "Script durcissement VPS"
    "scripts/query.py" = "Script de requêtes SQL"
    "scripts/inspect_netcdf.py" = "Script d'inspection NetCDF"
    ".windsurf/skills/project-context.md" = "Constitution SACS"
    "requirements.txt" = "Dépendances Python (base)"
    "requirements-ingestion.txt" = "Dépendances ingestion"
    "requirements-ml.txt" = "Dépendances ML"
}

$found = 0
$missing = 0
$missingList = @()

foreach ($file in $criticalFiles.Keys) {
    $fullPath = Join-Path $PROJECT_ROOT $file
    
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        $sizeKB = [math]::Round($size / 1KB, 2)
        Write-Host "  ✓ OK:      " -ForegroundColor Green -NoNewline
        Write-Host "$file " -NoNewline
        Write-Host "($sizeKB Ko)" -ForegroundColor Gray
        $found++
    } else {
        Write-Host "  ✗ MANQUE:  " -ForegroundColor Red -NoNewline
        Write-Host "$file - $($criticalFiles[$file])"
        $missing++
        $missingList += $file
    }
}

Write-Host ""
Write-Host "  📊 Résumé: " -NoNewline
Write-Host "$found trouvé(s), " -ForegroundColor Green -NoNewline
Write-Host "$missing manquant(s)" -ForegroundColor $(if ($missing -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($missing -gt 0) {
    Write-Host "  ⚠️  ATTENTION: Fichiers manquants détectés!" -ForegroundColor Yellow
    Write-Host "  Assurez-vous que tous les fichiers ont été générés." -ForegroundColor Yellow
    Write-Host ""
}

# ============================================================================
# ÉTAPE 3: CRÉATION DU FICHIER .env
# ============================================================================

Write-Host "═══ [3/5] Configuration du fichier .env ═══" -ForegroundColor Green
Write-Host ""

$envPath = Join-Path $PROJECT_ROOT ".env"
$envExamplePath = Join-Path $PROJECT_ROOT ".env.example"

if (Test-Path $envPath) {
    Write-Host "  ○ Fichier .env existe déjà" -ForegroundColor Gray
    Write-Host "  Voulez-vous le recréer? (o/N): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -ne "o" -and $response -ne "O") {
        Write-Host "  → Conservation du fichier existant" -ForegroundColor Cyan
    } else {
        Remove-Item $envPath
        Write-Host "  ✓ Ancien fichier supprimé" -ForegroundColor Green
        $createEnv = $true
    }
} else {
    $createEnv = $true
}

if ($createEnv) {
    if (Test-Path $envExamplePath) {
        Copy-Item $envExamplePath $envPath
        Write-Host "  ✓ Fichier .env créé depuis .env.example" -ForegroundColor Green
        
        # Génération d'un mot de passe fort
        $password = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        
        # Remplacement du placeholder
        (Get-Content $envPath) -replace 'POSTGRES_PASSWORD=.*', "POSTGRES_PASSWORD=$password" | Set-Content $envPath
        
        Write-Host "  ✓ Mot de passe généré automatiquement" -ForegroundColor Green
        Write-Host ""
        Write-Host "  🔐 IMPORTANT: Mot de passe PostgreSQL généré:" -ForegroundColor Yellow
        Write-Host "     $password" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  ⚠️  Sauvegardez ce mot de passe dans un gestionnaire sécurisé!" -ForegroundColor Red
        Write-Host ""
    } else {
        Write-Host "  ✗ ERREUR: .env.example introuvable" -ForegroundColor Red
        Write-Host "  Création manuelle requise" -ForegroundColor Yellow
    }
}

# ============================================================================
# ÉTAPE 4: CRÉATION DES FICHIERS DE CONFIGURATION
# ============================================================================

Write-Host "═══ [4/5] Création des fichiers de configuration ═══" -ForegroundColor Green
Write-Host ""

# Prometheus configuration
$prometheusConfig = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'timescaledb'
    static_configs:
      - targets: ['timescaledb:5432']

  - job_name: 'oceansentinel_api'
    static_configs:
      - targets: ['api:8000']
"@

$prometheusPath = Join-Path $PROJECT_ROOT "monitoring/prometheus.yml"
if (-Not (Test-Path $prometheusPath)) {
    $prometheusConfig | Out-File -FilePath $prometheusPath -Encoding UTF8
    Write-Host "  ✓ Créé: monitoring/prometheus.yml" -ForegroundColor Green
} else {
    Write-Host "  ○ Existe: monitoring/prometheus.yml" -ForegroundColor Gray
}

# Nginx basic config
$nginxConfig = @"
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream grafana {
        server grafana:3000;
    }

    server {
        listen 80;
        server_name _;

        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
        }

        location /grafana/ {
            proxy_pass http://grafana/;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
        }

        location / {
            return 301 /grafana/;
        }
    }
}
"@

$nginxPath = Join-Path $PROJECT_ROOT "nginx/nginx.conf"
if (-Not (Test-Path $nginxPath)) {
    $nginxConfig | Out-File -FilePath $nginxPath -Encoding UTF8
    Write-Host "  ✓ Créé: nginx/nginx.conf" -ForegroundColor Green
} else {
    Write-Host "  ○ Existe: nginx/nginx.conf" -ForegroundColor Gray
}

# .gitignore
$gitignoreContent = @"
# Ocean Sentinel V3.0 - .gitignore

# Environnement
.env
*.env
!.env.example

# Données
data/
!data/.gitkeep
*.nc
*.nc4
*.grb
*.grb2
*.csv

# Logs
logs/
*.log

# Backups
backups/
*.dump
*.sql

# Modèles ML
models/
*.h5
*.pkl
*.joblib

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml

# SSL
nginx/ssl/*.key
nginx/ssl/*.crt
nginx/ssl/*.pem
"@

$gitignorePath = Join-Path $PROJECT_ROOT ".gitignore"
if (-Not (Test-Path $gitignorePath)) {
    $gitignoreContent | Out-File -FilePath $gitignorePath -Encoding UTF8
    Write-Host "  ✓ Créé: .gitignore" -ForegroundColor Green
} else {
    Write-Host "  ○ Existe: .gitignore" -ForegroundColor Gray
}

Write-Host ""

# ============================================================================
# ÉTAPE 5: CRÉATION DES FICHIERS .gitkeep
# ============================================================================

Write-Host "═══ [5/5] Création des fichiers .gitkeep ═══" -ForegroundColor Green
Write-Host ""

$gitkeepDirs = @(
    "data/netcdf",
    "data/csv",
    "data/grib2",
    "logs/ingestion",
    "logs/ml",
    "models/lstm",
    "models/isolation_forest",
    "backups"
)

foreach ($dir in $gitkeepDirs) {
    $gitkeepPath = Join-Path $PROJECT_ROOT "$dir/.gitkeep"
    if (-Not (Test-Path $gitkeepPath)) {
        "" | Out-File -FilePath $gitkeepPath -Encoding UTF8
        Write-Host "  ✓ Créé: $dir/.gitkeep" -ForegroundColor Green
    }
}

Write-Host ""

# ============================================================================
# RAPPORT FINAL
# ============================================================================

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""
Write-Host "  ✅ INSTALLATION TERMINÉE AVEC SUCCÈS" -ForegroundColor Green
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 RÉSUMÉ DE L'INSTALLATION:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  • Dossiers créés:     $created" -ForegroundColor Green
Write-Host "  • Fichiers vérifiés:  $found/$($criticalFiles.Count)" -ForegroundColor $(if ($missing -eq 0) { "Green" } else { "Yellow" })
Write-Host "  • Configuration .env: " -NoNewline
if (Test-Path $envPath) {
    Write-Host "✓ OK" -ForegroundColor Green
} else {
    Write-Host "✗ MANQUANT" -ForegroundColor Red
}
Write-Host ""

Write-Host "📁 STRUCTURE DU PROJET:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  OSwindsurf/" -ForegroundColor Yellow
Write-Host "  ├── data/              " -NoNewline; Write-Host "(Fichiers NetCDF, CSV, GRIB2)" -ForegroundColor Gray
Write-Host "  ├── logs/              " -NoNewline; Write-Host "(Logs d'ingestion et ML)" -ForegroundColor Gray
Write-Host "  ├── models/            " -NoNewline; Write-Host "(Modèles ML entraînés)" -ForegroundColor Gray
Write-Host "  ├── backups/           " -NoNewline; Write-Host "(Backups TimescaleDB)" -ForegroundColor Gray
Write-Host "  ├── scripts/           " -NoNewline; Write-Host "(Scripts Python et Shell)" -ForegroundColor Gray
Write-Host "  ├── monitoring/        " -NoNewline; Write-Host "(Prometheus, Grafana)" -ForegroundColor Gray
Write-Host "  ├── nginx/             " -NoNewline; Write-Host "(Reverse proxy)" -ForegroundColor Gray
Write-Host "  ├── .windsurf/skills/  " -NoNewline; Write-Host "(Constitution SACS)" -ForegroundColor Gray
Write-Host "  ├── .env               " -NoNewline; Write-Host "(Variables d'environnement)" -ForegroundColor Gray
Write-Host "  └── docker-compose-v3.yml" -ForegroundColor Yellow
Write-Host ""

Write-Host "🚀 PROCHAINES ÉTAPES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Vérifier le fichier .env:" -ForegroundColor Yellow
Write-Host "     notepad .env" -ForegroundColor White
Write-Host ""
Write-Host "  2. (Optionnel) Tester localement avec Docker:" -ForegroundColor Yellow
Write-Host "     docker compose -f docker-compose.yml up -d" -ForegroundColor White
Write-Host ""
Write-Host "  3. Transférer sur le VPS:" -ForegroundColor Yellow
Write-Host "     # Méthode Git (recommandée)" -ForegroundColor Gray
Write-Host "     git init" -ForegroundColor White
Write-Host "     git add ." -ForegroundColor White
Write-Host "     git commit -m 'Ocean Sentinel V3.0 - Initial commit'" -ForegroundColor White
Write-Host "     git remote add origin VOTRE_REPO_GIT" -ForegroundColor White
Write-Host "     git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "     # Puis sur le VPS:" -ForegroundColor Gray
Write-Host "     ssh root@VOTRE_IP_VPS" -ForegroundColor White
Write-Host "     git clone VOTRE_REPO_GIT ~/oceansentinel" -ForegroundColor White
Write-Host ""
Write-Host "  4. Durcir le VPS:" -ForegroundColor Yellow
Write-Host "     cd ~/oceansentinel" -ForegroundColor White
Write-Host "     sudo bash scripts/harden_vps.sh" -ForegroundColor White
Write-Host ""
Write-Host "  5. Lancer Ocean Sentinel V3.0:" -ForegroundColor Yellow
Write-Host "     docker compose -f docker-compose-v3.yml up -d" -ForegroundColor White
Write-Host ""

Write-Host "📚 DOCUMENTATION:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  • Guide complet:        OCEAN_SENTINEL_V3_README.md" -ForegroundColor White
Write-Host "  • Constitution SACS:    .windsurf/skills/project-context.md" -ForegroundColor White
Write-Host "  • Guide NetCDF:         GUIDE_NETCDF_COAST_HF.md" -ForegroundColor White
Write-Host "  • Déploiement:          DEPLOYMENT.md" -ForegroundColor White
Write-Host "  • Backups:              BACKUP_GUIDE.md" -ForegroundColor White
Write-Host ""

if ($missing -gt 0) {
    Write-Host "⚠️  ATTENTION:" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Fichiers manquants détectés:" -ForegroundColor Yellow
    foreach ($file in $missingList) {
        Write-Host "    • $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "  Veuillez générer ces fichiers avant de continuer." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""
Write-Host "  🌊 Ocean Sentinel V3.0 est prêt pour le déploiement! 🌊" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Pause finale
Write-Host "Appuyez sur une touche pour continuer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
