# Script de redimensionnement d'images pour mobile
# Cible : 800x600 pixels (standard mobile 2x retina)

Add-Type -AssemblyName System.Drawing

$sourceDir = "public\images\news"
$targetWidth = 800
$targetHeight = 600
$quality = 85

Get-ChildItem $sourceDir -Filter *.jpg | Where-Object { $_.Length -gt 100KB } | ForEach-Object {
    try {
        $sourcePath = $_.FullName
        $img = [System.Drawing.Image]::FromFile($sourcePath)
        
        # Skip if already correct size
        if ($img.Width -le $targetWidth -and $img.Height -le $targetHeight) {
            Write-Host "Skip: $($_.Name) (already optimized)" -ForegroundColor Yellow
            $img.Dispose()
            return
        }
        
        Write-Host "Processing: $($_.Name) ($($img.Width)x$($img.Height))" -ForegroundColor Cyan
        
        # Create new bitmap
        $newImg = New-Object System.Drawing.Bitmap($targetWidth, $targetHeight)
        $graphics = [System.Drawing.Graphics]::FromImage($newImg)
        
        # High quality settings
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
        $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        
        # Draw resized image
        $graphics.DrawImage($img, 0, 0, $targetWidth, $targetHeight)
        
        # Save with quality
        $encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
        $encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter(
            [System.Drawing.Imaging.Encoder]::Quality, $quality
        )
        
        $jpegCodec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | 
            Where-Object { $_.MimeType -eq 'image/jpeg' }
        
        # Backup original
        $backupPath = $sourcePath -replace '\.jpg$', '.original.jpg'
        if (-not (Test-Path $backupPath)) {
            Copy-Item $sourcePath $backupPath
        }
        
        # Save optimized
        $newImg.Save($sourcePath, $jpegCodec, $encoderParams)
        
        $newSize = (Get-Item $sourcePath).Length
        Write-Host "Saved: $($_.Name) (${targetWidth}x${targetHeight}, $([math]::Round($newSize/1KB,2)) KB)" -ForegroundColor Green
        
        # Cleanup
        $graphics.Dispose()
        $newImg.Dispose()
        $img.Dispose()
        
    } catch {
        Write-Host "Error: $($_.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nDone! Original images backed up as *.original.jpg" -ForegroundColor Green
