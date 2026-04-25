# Script de mise à jour des headers sur toutes les pages
# Ocean Sentinel V3.2

$pages = @('index', 'about', 'api', 'podcast')
$headerContent = Get-Content "C:\Users\ktprt\Documents\OSwindsurf\header-unified.html" -Raw

foreach ($page in $pages) {
    Write-Host "Mise à jour de $page.html..." -ForegroundColor Cyan
    
    # Télécharger la page actuelle
    ssh root@76.13.43.3 "cat /opt/oceansentinel/frontend/$page.html" > "C:\Users\ktprt\Documents\OSwindsurf\$page-temp.html"
    
    $content = Get-Content "C:\Users\ktprt\Documents\OSwindsurf\$page-temp.html" -Raw
    
    # Remplacer l'ancien header par le nouveau
    $content = $content -replace '(?s)<header class="header">.*?</header>', $headerContent
    
    # Sauvegarder
    Set-Content -Path "C:\Users\ktprt\Documents\OSwindsurf\$page-updated.html" -Value $content -Encoding UTF8
    
    # Uploader
    scp "C:\Users\ktprt\Documents\OSwindsurf\$page-updated.html" "root@76.13.43.3:/opt/oceansentinel/frontend/$page.html"
    
    Write-Host "✅ $page.html mis à jour" -ForegroundColor Green
}

Write-Host "`n🎉 Toutes les pages ont été mises à jour!" -ForegroundColor Green
