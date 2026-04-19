# Guide de Déploiement Production - Ocean Sentinel

## ✅ Prérequis Validés

**VPS Hostinger (76.13.43.3)** :
- ✅ SSH accessible (port 22)
- ✅ HTTP accessible (port 80) - Nginx 1.24.0
- ✅ HTTPS accessible (port 443) - Certificat à configurer
- ✅ Firewall configuré (OceanSentinel-Web synchronisé)
- ✅ Nginx opérationnel (3 workers)

**Date de validation** : 18 avril 2026 23:20 UTC

---

## 🚀 Plan de Déploiement

### Phase 1 : Préparation du VPS
### Phase 2 : Configuration SSL/TLS (Let's Encrypt)
### Phase 3 : Déploiement Backend (FastAPI + PostgreSQL)
### Phase 4 : Déploiement Frontend
### Phase 5 : Configuration Stripe Webhooks
### Phase 6 : Démarrage Worker DLQ
### Phase 7 : Tests et Validation

---

## Phase 1 : Préparation du VPS

### 1.1 Installer Docker et Docker Compose

```bash
# Connexion SSH
ssh root@76.13.43.3

# Mise à jour du système
apt update && apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Vérifier l'installation
docker --version
# Docker version 24.0.7, build afdd53b

# Installer Docker Compose
apt install docker-compose-plugin -y

# Vérifier
docker compose version
# Docker Compose version v2.23.0
```

### 1.2 Créer la Structure de Répertoires

```bash
# Créer le répertoire principal
mkdir -p /opt/oceansentinel
cd /opt/oceansentinel

# Structure
mkdir -p {backend,frontend,nginx,postgres,logs}
mkdir -p nginx/{conf.d,ssl}
mkdir -p postgres/data
```

### 1.3 Configurer le Firewall Local (UFW)

```bash
# Vérifier UFW
ufw status

# Si inactif, activer avec précaution
ufw allow 22/tcp    # SSH (IMPORTANT : à faire AVANT d'activer)
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# Vérifier
ufw status verbose
```

---

## Phase 2 : Configuration SSL/TLS (Let's Encrypt)

### 2.1 Installer Certbot

```bash
# Installer Certbot
apt install certbot python3-certbot-nginx -y

# Vérifier
certbot --version
```

### 2.2 Obtenir un Certificat SSL

**Option A : Avec nom de domaine (Recommandé)**

```bash
# Remplacer par votre domaine
certbot --nginx -d oceansentinel.fr -d www.oceansentinel.fr

# Suivre les instructions:
# 1. Entrer votre email
# 2. Accepter les CGU
# 3. Choisir "2: Redirect" pour forcer HTTPS
```

**Option B : Certificat auto-signé (Développement uniquement)**

```bash
# Générer un certificat auto-signé
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/oceansentinel/nginx/ssl/selfsigned.key \
  -out /opt/oceansentinel/nginx/ssl/selfsigned.crt \
  -subj "/C=FR/ST=Aquitaine/L=Bordeaux/O=OceanSentinel/CN=76.13.43.3"
```

### 2.3 Configuration Nginx pour SSL

```bash
# Créer la configuration Nginx
cat > /etc/nginx/sites-available/oceansentinel << 'EOF'
# Redirection HTTP → HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name oceansentinel.fr www.oceansentinel.fr;
    
    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirection HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# Configuration HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name oceansentinel.fr www.oceansentinel.fr;
    
    # Certificats SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/oceansentinel.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/oceansentinel.fr/privkey.pem;
    
    # Configuration SSL moderne (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    
    # HSTS (31536000 secondes = 1 an)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Headers de sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # CSP (Content Security Policy)
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.stripe.com;" always;
    
    # Logs
    access_log /var/log/nginx/oceansentinel_access.log;
    error_log /var/log/nginx/oceansentinel_error.log;
    
    # Frontend (fichiers statiques)
    location / {
        root /opt/oceansentinel/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache pour les assets
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;
    }
    
    # Webhook Stripe (pas de rate limiting)
    location /api/webhooks/stripe {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts courts pour webhooks
        proxy_connect_timeout 10s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}
EOF

# Activer la configuration
ln -sf /etc/nginx/sites-available/oceansentinel /etc/nginx/sites-enabled/

# Tester la configuration
nginx -t

# Recharger Nginx
systemctl reload nginx
```

---

## Phase 3 : Déploiement Backend

### 3.1 Copier les Fichiers depuis Windows

**Depuis votre machine Windows (PowerShell)** :

```powershell
# Copier le backend
scp -r C:\Users\ktprt\Documents\OSwindsurf\backend\* root@76.13.43.3:/opt/oceansentinel/backend/

# Copier docker-compose
scp C:\Users\ktprt\Documents\OSwindsurf\docker-compose.prod.yml root@76.13.43.3:/opt/oceansentinel/
```

### 3.2 Créer le Fichier .env

```bash
# Sur le VPS
cd /opt/oceansentinel

# Générer les secrets
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export API_JWT_SECRET=$(openssl rand -base64 64)
export STRIPE_SECRET_KEY="sk_test_VOTRE_CLE_STRIPE"
export STRIPE_WEBHOOK_SECRET="whsec_VOTRE_SECRET_WEBHOOK"

# Créer .env
cat > .env << EOF
# Database
POSTGRES_DB=oceansentinel
POSTGRES_USER=oceansentinel
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
DATABASE_URL=postgresql+asyncpg://oceansentinel:${POSTGRES_PASSWORD}@postgres:5432/oceansentinel

# JWT
API_JWT_SECRET=${API_JWT_SECRET}
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}

# Email (à configurer)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@oceansentinel.fr
SMTP_PASSWORD=VOTRE_MOT_DE_PASSE
ADMIN_EMAIL=admin@oceansentinel.fr

# Application
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=oceansentinel.fr,www.oceansentinel.fr,76.13.43.3
CORS_ORIGINS=https://oceansentinel.fr,https://www.oceansentinel.fr

# Worker
WORKER_POLL_INTERVAL=5
MAX_RETRY_COUNT=3
BATCH_SIZE=10
DLQ_ALERT_THRESHOLD=10
EOF

# Sécuriser le fichier
chmod 600 .env
```

### 3.3 Créer docker-compose.prod.yml

```yaml
# /opt/oceansentinel/docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: oceansentinel_postgres
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - ./postgres/data:/var/lib/postgresql/data
      - ./backend/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: oceansentinel_redis
    networks:
      - backend
    restart: unless-stopped
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

networks:
  backend:
    driver: bridge
```

### 3.4 Démarrer les Services

```bash
cd /opt/oceansentinel

# Build et démarrer
docker compose -f docker-compose.prod.yml up -d --build

# Vérifier les logs
docker compose logs -f

# Vérifier que tous les services sont UP
docker compose ps

# Résultat attendu:
# NAME                        STATUS
# oceansentinel_postgres      Up (healthy)
# oceansentinel_redis         Up (healthy)
# oceansentinel_api           Up (healthy)
# oceansentinel_stripe_worker Up
```

### 3.5 Vérifier l'API

```bash
# Health check
curl http://localhost:8000/api/health

# Résultat attendu:
# {"status":"healthy","timestamp":"2026-04-19T01:30:00Z"}

# Swagger UI
curl http://localhost:8000/api/docs

# Depuis l'extérieur
curl https://oceansentinel.fr/api/health
```

---

## Phase 4 : Déploiement Frontend

### 4.1 Build du Frontend (Sur votre machine Windows)

```powershell
# Si vous avez un projet React/Vue/Angular
cd C:\Users\ktprt\Documents\OSwindsurf\frontend

# Installer les dépendances
npm install

# Build pour production
npm run build

# Le dossier dist/ contient les fichiers statiques
```

### 4.2 Copier sur le VPS

```powershell
# Copier le dossier dist
scp -r C:\Users\ktprt\Documents\OSwindsurf\frontend\dist\* root@76.13.43.3:/opt/oceansentinel/frontend/dist/
```

### 4.3 Vérifier

```bash
# Sur le VPS
ls -lh /opt/oceansentinel/frontend/dist/

# Tester
curl https://oceansentinel.fr/
```

---

## Phase 5 : Configuration Stripe Webhooks

### 5.1 Créer l'Endpoint dans Stripe Dashboard

1. **Accéder au Dashboard Stripe**
   - URL : https://dashboard.stripe.com/webhooks
   - Se connecter avec votre compte

2. **Ajouter un Endpoint**
   - Cliquer sur "Add endpoint"
   - URL : `https://oceansentinel.fr/api/webhooks/stripe`
   - Description : "Ocean Sentinel Production Webhook"

3. **Sélectionner les Événements**
   ```
   ✓ customer.subscription.created
   ✓ customer.subscription.updated
   ✓ customer.subscription.deleted
   ✓ invoice.payment_succeeded
   ✓ invoice.payment_failed
   ✓ checkout.session.completed
   ```

4. **Copier le Signing Secret**
   - Format : `whsec_...`
   - Ajouter dans `.env` : `STRIPE_WEBHOOK_SECRET=whsec_...`

5. **Redémarrer l'API**
   ```bash
   docker compose restart api stripe-worker
   ```

### 5.2 Tester avec Stripe CLI

```bash
# Installer Stripe CLI
wget https://github.com/stripe/stripe-cli/releases/download/v1.19.0/stripe_1.19.0_linux_x86_64.tar.gz
tar -xvf stripe_1.19.0_linux_x86_64.tar.gz
mv stripe /usr/local/bin/

# Se connecter
stripe login

# Tester l'envoi d'événement
stripe trigger customer.subscription.created \
  --webhook-endpoint https://oceansentinel.fr/api/webhooks/stripe

# Vérifier les logs du worker
docker compose logs -f stripe-worker

# Résultat attendu:
# ⚙️  Traitement événement evt_...
# ✅ Événement evt_... traité avec succès
```

---

## Phase 6 : Tests et Validation

### 6.1 Tests de Connectivité

```bash
# HTTP → HTTPS redirect
curl -I http://oceansentinel.fr
# HTTP/1.1 301 Moved Permanently
# Location: https://oceansentinel.fr/

# HTTPS
curl -I https://oceansentinel.fr
# HTTP/2 200
# server: nginx/1.24.0

# API Health
curl https://oceansentinel.fr/api/health
# {"status":"healthy"}

# Swagger UI
curl https://oceansentinel.fr/api/docs
# HTML de Swagger
```

### 6.2 Tests d'Authentification

```bash
# Inscription
curl -X POST https://oceansentinel.fr/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "consent": true,
    "consent_timestamp": "2026-04-19T01:30:00Z"
  }'

# Résultat attendu:
# {
#   "access_token": "eyJ...",
#   "refresh_token": "...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }
```

### 6.3 Tests Worker Stripe

```bash
# Vérifier les métriques
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://oceansentinel.fr/api/admin/stripe/metrics

# Résultat attendu:
# {
#   "pending": 0,
#   "failed": 0,
#   "processed_24h": 5,
#   "avg_processing_time_seconds": 1.23,
#   "dlq_alert": false
# }
```

---

## Phase 7 : Monitoring et Maintenance

### 7.1 Logs

```bash
# Logs API
docker compose logs -f api

# Logs Worker
docker compose logs -f stripe-worker

# Logs Nginx
tail -f /var/log/nginx/oceansentinel_access.log
tail -f /var/log/nginx/oceansentinel_error.log

# Logs PostgreSQL
docker compose logs -f postgres
```

### 7.2 Sauvegardes

```bash
# Créer un script de sauvegarde
cat > /opt/oceansentinel/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/oceansentinel/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Créer le répertoire
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec oceansentinel_postgres pg_dump -U oceansentinel oceansentinel | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup .env
cp /opt/oceansentinel/.env $BACKUP_DIR/env_$DATE

# Nettoyer les backups > 30 jours
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup terminé: $DATE"
EOF

chmod +x /opt/oceansentinel/backup.sh

# Ajouter au cron (tous les jours à 2h du matin)
crontab -e
# Ajouter: 0 2 * * * /opt/oceansentinel/backup.sh
```

### 7.3 Monitoring avec Healthchecks

```bash
# Créer un script de monitoring
cat > /opt/oceansentinel/healthcheck.sh << 'EOF'
#!/bin/bash

# Vérifier l'API
if ! curl -f -s https://oceansentinel.fr/api/health > /dev/null; then
    echo "ALERTE: API non accessible"
    # Envoyer email ou notification
fi

# Vérifier PostgreSQL
if ! docker exec oceansentinel_postgres pg_isready -U oceansentinel > /dev/null; then
    echo "ALERTE: PostgreSQL non accessible"
fi

# Vérifier les workers
WORKER_COUNT=$(docker ps --filter "name=stripe-worker" --filter "status=running" -q | wc -l)
if [ $WORKER_COUNT -lt 1 ]; then
    echo "ALERTE: Aucun worker Stripe actif"
fi
EOF

chmod +x /opt/oceansentinel/healthcheck.sh

# Ajouter au cron (toutes les 5 minutes)
crontab -e
# Ajouter: */5 * * * * /opt/oceansentinel/healthcheck.sh
```

---

## 📋 Checklist Finale

```markdown
## Infrastructure
- [x] VPS accessible (SSH, HTTP, HTTPS)
- [x] Firewall configuré (ports 22, 80, 443)
- [x] Nginx opérationnel
- [ ] Certificat SSL Let's Encrypt configuré
- [ ] Docker et Docker Compose installés

## Backend
- [ ] PostgreSQL démarré et healthy
- [ ] Redis démarré et healthy
- [ ] API FastAPI accessible (/api/health)
- [ ] Swagger UI accessible (/api/docs)
- [ ] Worker Stripe actif (2 réplicas)

## Frontend
- [ ] Fichiers statiques copiés
- [ ] Page d'accueil accessible
- [ ] Formulaire d'inscription fonctionnel

## Stripe
- [ ] Webhook endpoint créé dans dashboard
- [ ] Signing secret configuré
- [ ] Test avec Stripe CLI réussi
- [ ] Événements traités par le worker

## Sécurité
- [ ] HTTPS forcé (redirect HTTP)
- [ ] Headers de sécurité configurés
- [ ] Rate limiting activé
- [ ] Fichier .env sécurisé (chmod 600)

## Monitoring
- [ ] Logs accessibles
- [ ] Script de backup configuré
- [ ] Healthcheck automatique
- [ ] Alertes configurées
```

---

**Déploiement créé le** : 19 avril 2026  
**Version** : 1.0  
**Status** : Prêt pour production
