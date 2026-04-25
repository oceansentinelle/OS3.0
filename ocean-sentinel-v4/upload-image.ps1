# Script d'upload de l'image hero vers le VPS
# Ocean Sentinel - Bassin d'Arcachon

Write-Host "=== UPLOAD IMAGE HERO VERS VPS ===" -ForegroundColor Cyan
Write-Host ""

# Demander le chemin de l'image
$imagePath = Read-Host "Entrez le chemin complet de votre image (ou glissez-déposez le fichier ici)"

# Nettoyer le chemin (enlever les guillemets si présents)
$imagePath = $imagePath.Trim('"')

# Vérifier que le fichier existe
if (-not (Test-Path $imagePath)) {
    Write-Host "ERREUR : Fichier introuvable : $imagePath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Assurez-vous que :" -ForegroundColor Yellow
    Write-Host "  1. Le fichier existe bien" -ForegroundColor Yellow
    Write-Host "  2. Le chemin est correct" -ForegroundColor Yellow
    Write-Host "  3. Vous avez les droits de lecture" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Fichier trouvé : $imagePath" -ForegroundColor Green

# Obtenir la taille du fichier
$fileSize = (Get-Item $imagePath).Length
$fileSizeMB = [math]::Round($fileSize / 1MB, 2)
Write-Host "✓ Taille : $fileSizeMB MB" -ForegroundColor Green

# Confirmer l'upload
Write-Host ""
Write-Host "Destination : root@76.13.43.3:/var/www/oceansentinelle/images/bassin-arcachon-hero.jpg" -ForegroundColor Cyan
$confirm = Read-Host "Confirmer l'upload ? (O/N)"

if ($confirm -ne "O" -and $confirm -ne "o") {
    Write-Host "Upload annulé." -ForegroundColor Yellow
    exit 0
}

# Upload via SCP
Write-Host ""
Write-Host "Upload en cours..." -ForegroundColor Cyan
scp "$imagePath" root@76.13.43.3:/var/www/oceansentinelle/images/bassin-arcachon-hero.jpg

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ IMAGE UPLOADÉE AVEC SUCCÈS !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Prochaines étapes :" -ForegroundColor Cyan
    Write-Host "  1. Modifier le code pour utiliser .jpg au lieu de .svg" -ForegroundColor White
    Write-Host "  2. npm run build" -ForegroundColor White
    Write-Host "  3. scp -r dist/* root@76.13.43.3:/var/www/oceansentinelle/" -ForegroundColor White
    Write-Host "  4. Rafraîchir https://oceansentinelle.fr (Ctrl + Shift + R)" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "✗ ERREUR lors de l'upload" -ForegroundColor Red
    Write-Host "Vérifiez votre connexion SSH et réessayez." -ForegroundColor Yellow
}
