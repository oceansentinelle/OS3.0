# ============================================================================
# Script de Déploiement UI Ocean Sentinelle V3.1
# Conforme M-23-22 (Zero Trust, auto-hébergement)
# ============================================================================

param(
    [switch]$DryRun,
    [switch]$SkipBackup
)

$VPS_HOST = "root@76.13.43.3"
$VPS_PATH = "/opt/oceansentinel/frontend"
$LOCAL_PATH = "C:\Users\ktprt\Documents\OSwindsurf\public"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "DÉPLOIEMENT UI OCEAN SENTINELLE V3.1" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Vérification fichiers locaux
Write-Host "[1/6] Vérification fichiers locaux..." -ForegroundColor Yellow
$requiredFiles = @(
    "index.new.html",
    "about.new.html",
    "api.new.html",
    "tailwind.config.js",
    "assets/css/input.css",
    "assets/images/favicon.svg"
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $LOCAL_PATH $file
    if (-not (Test-Path $fullPath)) {
        Write-Host "❌ Fichier manquant: $file" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Tous les fichiers requis sont présents" -ForegroundColor Green
Write-Host ""

# Backup production (si demandé)
if (-not $SkipBackup) {
    Write-Host "[2/6] Backup production..." -ForegroundColor Yellow
    $backupDate = Get-Date -Format "yyyyMMdd_HHmmss"
    ssh $VPS_HOST "cp -r $VPS_PATH ${VPS_PATH}.backup.$backupDate"
    Write-Host "✅ Backup créé: ${VPS_PATH}.backup.$backupDate" -ForegroundColor Green
} else {
    Write-Host "[2/6] Backup ignoré (--SkipBackup)" -ForegroundColor Gray
}
Write-Host ""

# Copie fichiers HTML
Write-Host "[3/6] Copie fichiers HTML..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "[DRY-RUN] scp index.new.html → $VPS_HOST:$VPS_PATH/index.html" -ForegroundColor Gray
    Write-Host "[DRY-RUN] scp about.new.html → $VPS_HOST:$VPS_PATH/about.html" -ForegroundColor Gray
    Write-Host "[DRY-RUN] scp api.new.html → $VPS_HOST:$VPS_PATH/api.html" -ForegroundColor Gray
} else {
    scp "$LOCAL_PATH\index.new.html" "${VPS_HOST}:${VPS_PATH}/index.html"
    scp "$LOCAL_PATH\about.new.html" "${VPS_HOST}:${VPS_PATH}/about.html"
    scp "$LOCAL_PATH\api.new.html" "${VPS_HOST}:${VPS_PATH}/api.html"
    Write-Host "✅ Fichiers HTML copiés" -ForegroundColor Green
}
Write-Host ""

# Copie assets
Write-Host "[4/6] Copie assets..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "[DRY-RUN] scp -r assets → $VPS_HOST:$VPS_PATH/" -ForegroundColor Gray
    Write-Host "[DRY-RUN] scp tailwind.config.js → $VPS_HOST:$VPS_PATH/" -ForegroundColor Gray
} else {
    scp -r "$LOCAL_PATH\assets" "${VPS_HOST}:${VPS_PATH}/"
    scp "$LOCAL_PATH\tailwind.config.js" "${VPS_HOST}:${VPS_PATH}/"
    Write-Host "✅ Assets copiés" -ForegroundColor Green
}
Write-Host ""

# Compilation Tailwind CSS sur VPS
Write-Host "[5/6] Compilation Tailwind CSS..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "[DRY-RUN] ssh $VPS_HOST 'cd $VPS_PATH && tailwindcss ...'" -ForegroundColor Gray
} else {
    ssh $VPS_HOST "cd $VPS_PATH && tailwindcss -i ./assets/css/input.css -o ./assets/css/main.css --minify"
    Write-Host "✅ CSS compilé et minifié" -ForegroundColor Green
}
Write-Host ""

# Permissions
Write-Host "[6/6] Correction permissions..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "[DRY-RUN] chown -R www-data:www-data $VPS_PATH" -ForegroundColor Gray
} else {
    ssh $VPS_HOST "chown -R www-data:www-data $VPS_PATH && chmod -R 755 $VPS_PATH"
    Write-Host "✅ Permissions corrigées" -ForegroundColor Green
}
Write-Host ""

# Validation
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "VALIDATION DÉPLOIEMENT" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $DryRun) {
    Write-Host "Vérification fichiers déployés..." -ForegroundColor Yellow
    ssh $VPS_HOST "ls -lh $VPS_PATH/*.html $VPS_PATH/assets/css/main.css"
    Write-Host ""
    
    Write-Host "Taille CSS compilé:" -ForegroundColor Yellow
    ssh $VPS_HOST "du -h $VPS_PATH/assets/css/main.css"
    Write-Host ""
    
    Write-Host "✅ DÉPLOIEMENT TERMINÉ !" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Testez sur: https://oceansentinelle.fr" -ForegroundColor Cyan
    Write-Host "📊 Lighthouse: https://pagespeed.web.dev/?url=https://oceansentinelle.fr" -ForegroundColor Cyan
} else {
    Write-Host "✅ DRY-RUN TERMINÉ (aucune modification)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour déployer réellement, relancez sans --DryRun" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
