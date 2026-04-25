#!/bin/bash
# Fix audio permissions after deployment
# Run this on the server after each scp deployment

echo "🔧 Fixing audio permissions..."

# Set directory permissions
chmod 755 /var/www/oceansentinelle/audio
echo "✅ Directory: 755"

# Set file permissions
chmod 644 /var/www/oceansentinelle/audio/*.mp3
echo "✅ Files: 644"

# Set ownership
chown -R www-data:www-data /var/www/oceansentinelle/audio
echo "✅ Owner: www-data:www-data"

# Verify
echo ""
echo "📊 Verification:"
ls -lah /var/www/oceansentinelle/audio/

echo ""
echo "✅ Audio permissions fixed!"
