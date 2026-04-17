# ============================================================================
# Ocean Sentinel - Vérification Connexion VPS
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "OCEAN SENTINEL - VÉRIFICATION CONNEXION VPS" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Demander l'IP du VPS
$VPS_IP = Read-Host "Entrez l'IP du VPS Hostinger"

if ([string]::IsNullOrWhiteSpace($VPS_IP)) {
    Write-Host "❌ IP VPS requise" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Vérification connexion à $VPS_IP..." -ForegroundColor Yellow
Write-Host ""

# ============================================================================
# 1. Test Ping
# ============================================================================

Write-Host "1. Test ping..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $VPS_IP -Count 2 -Quiet

if ($pingResult) {
    Write-Host "   ✅ VPS accessible (ping OK)" -ForegroundColor Green
} else {
    Write-Host "   ❌ VPS inaccessible (ping failed)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifiez:" -ForegroundColor Yellow
    Write-Host "  - L'IP est correcte" -ForegroundColor Yellow
    Write-Host "  - Le VPS est démarré" -ForegroundColor Yellow
    Write-Host "  - Le firewall autorise ICMP" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# 2. Test Port SSH (22)
# ============================================================================

Write-Host "2. Test port SSH (22)..." -ForegroundColor Yellow
$sshTest = Test-NetConnection -ComputerName $VPS_IP -Port 22 -WarningAction SilentlyContinue

if ($sshTest.TcpTestSucceeded) {
    Write-Host "   ✅ Port SSH ouvert" -ForegroundColor Green
} else {
    Write-Host "   ❌ Port SSH fermé" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifiez:" -ForegroundColor Yellow
    Write-Host "  - SSH est installé sur le VPS" -ForegroundColor Yellow
    Write-Host "  - Le firewall autorise le port 22" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# 3. Informations SSH
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "CONNEXION SSH" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Commande de connexion:" -ForegroundColor Yellow
Write-Host "  ssh root@$VPS_IP" -ForegroundColor White
Write-Host ""

Write-Host "Si vous utilisez une clé SSH:" -ForegroundColor Yellow
Write-Host "  ssh -i ~/.ssh/id_rsa root@$VPS_IP" -ForegroundColor White
Write-Host ""

# ============================================================================
# 4. Test Connexion SSH (optionnel)
# ============================================================================

Write-Host "Voulez-vous tester la connexion SSH maintenant ? (o/n)" -ForegroundColor Yellow
$testSSH = Read-Host

if ($testSSH -eq "o" -or $testSSH -eq "O") {
    Write-Host ""
    Write-Host "Tentative de connexion SSH..." -ForegroundColor Yellow
    Write-Host "Entrez le mot de passe root quand demandé" -ForegroundColor Yellow
    Write-Host ""
    
    # Tester avec ssh (nécessite OpenSSH installé sur Windows)
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$VPS_IP "echo 'Connexion SSH réussie' && uname -a"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Connexion SSH validée !" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Connexion SSH échouée" -ForegroundColor Red
        Write-Host ""
        Write-Host "Vérifiez:" -ForegroundColor Yellow
        Write-Host "  - Le mot de passe root est correct" -ForegroundColor Yellow
        Write-Host "  - L'authentification par mot de passe est activée" -ForegroundColor Yellow
        Write-Host "  - Vous avez OpenSSH installé sur Windows" -ForegroundColor Yellow
    }
}

# ============================================================================
# 5. Vérification Prérequis VPS
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "VÉRIFICATION PRÉREQUIS VPS" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Voulez-vous vérifier les prérequis sur le VPS ? (o/n)" -ForegroundColor Yellow
$checkPrereq = Read-Host

if ($checkPrereq -eq "o" -or $checkPrereq -eq "O") {
    Write-Host ""
    Write-Host "Vérification prérequis..." -ForegroundColor Yellow
    Write-Host ""
    
    # Script de vérification à exécuter sur le VPS
    $checkScript = @"
echo '=== Système ==='
uname -a
echo ''
echo '=== Mémoire ==='
free -h
echo ''
echo '=== Disque ==='
df -h /
echo ''
echo '=== Docker ==='
if command -v docker &> /dev/null; then
    docker --version
else
    echo 'Docker non installé'
fi
echo ''
echo '=== Docker Compose ==='
if docker compose version &> /dev/null; then
    docker compose version
else
    echo 'Docker Compose non installé'
fi
echo ''
echo '=== Git ==='
if command -v git &> /dev/null; then
    git --version
else
    echo 'Git non installé'
fi
"@
    
    # Exécuter sur le VPS
    $checkScript | ssh root@$VPS_IP "bash -s"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Vérification terminée" -ForegroundColor Green
    }
}

# ============================================================================
# 6. Résumé
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "RÉSUMÉ" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "VPS: $VPS_IP" -ForegroundColor White
Write-Host "Status: ✅ Accessible" -ForegroundColor Green
Write-Host ""

Write-Host "Prochaines étapes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Connexion SSH:" -ForegroundColor White
Write-Host "   ssh root@$VPS_IP" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Installation Docker (si nécessaire):" -ForegroundColor White
Write-Host "   curl -fsSL https://get.docker.com | sh" -ForegroundColor Cyan
Write-Host "   apt install -y docker-compose-plugin" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Clonage repository:" -ForegroundColor White
Write-Host "   git clone https://github.com/oceansentinelle/OS3.0.git /opt/oceansentinel" -ForegroundColor Cyan
Write-Host "   cd /opt/oceansentinel" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Configuration:" -ForegroundColor White
Write-Host "   cp .env.full.example .env" -ForegroundColor Cyan
Write-Host "   vim .env  # Éditer mots de passe" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Déploiement:" -ForegroundColor White
Write-Host "   chmod +x deploy.sh" -ForegroundColor Cyan
Write-Host "   ./deploy.sh" -ForegroundColor Cyan
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Sauvegarder l'IP pour usage futur
$VPS_IP | Out-File -FilePath ".vps_ip" -Encoding UTF8
Write-Host "💾 IP VPS sauvegardée dans .vps_ip" -ForegroundColor Green
Write-Host ""
