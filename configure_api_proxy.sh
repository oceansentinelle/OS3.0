#!/bin/bash

# Configuration Nginx pour proxy API HTTPS
# Ce script configure Nginx pour proxifier l'API sur api.oceansentinelle.fr

echo "🔧 Configuration du proxy API HTTPS..."

# Mettre à jour la configuration Nginx
cat > /etc/nginx/sites-available/oceansentinel <<'EOF'
# Redirection HTTP → HTTPS pour le site principal
server {
    listen 80;
    server_name oceansentinelle.fr www.oceansentinelle.fr oceansentinelle.org www.oceansentinelle.org 76.13.43.3;
    
    location / {
        root /opt/oceansentinel/public;
        index index.html;
        try_files $uri $uri/ =404;
    }
}

# Site principal HTTPS
server {
    listen 443 ssl;
    server_name oceansentinelle.fr www.oceansentinelle.fr oceansentinelle.org www.oceansentinelle.org;
    
    ssl_certificate /etc/letsencrypt/live/oceansentinelle.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/oceansentinelle.fr/privkey.pem;
    
    location / {
        root /opt/oceansentinel/public;
        index index.html;
        try_files $uri $uri/ =404;
    }
}

# API HTTP (pour accès direct IP)
server {
    listen 80;
    server_name api.oceansentinelle.fr api.oceansentinelle.org;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# API HTTPS
server {
    listen 443 ssl;
    server_name api.oceansentinelle.fr api.oceansentinelle.org;
    
    ssl_certificate /etc/letsencrypt/live/oceansentinelle.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/oceansentinelle.fr/privkey.pem;
    
    # CORS headers pour permettre les requêtes depuis le site web
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range' always;
    
    location / {
        # Gérer les requêtes OPTIONS (preflight CORS)
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
        
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "✅ Configuration Nginx mise à jour"

# Tester la configuration
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration Nginx valide"
    
    # Recharger Nginx
    systemctl reload nginx
    echo "✅ Nginx rechargé"
    
    echo ""
    echo "🎉 Configuration terminée !"
    echo ""
    echo "L'API est maintenant accessible via :"
    echo "  - https://api.oceansentinelle.fr"
    echo "  - https://api.oceansentinelle.org"
    echo ""
    echo "Testez avec :"
    echo "  curl https://api.oceansentinelle.fr/api/v1/health"
else
    echo "❌ Erreur dans la configuration Nginx"
    exit 1
fi
