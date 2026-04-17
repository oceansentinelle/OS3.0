# Ocean Sentinel V3.0 - Guide Déploiement VPS

## Vision

Déployer le **pipeline backend complet** sur VPS Hostinger pour valider l'ingestion réelle.

**Objectif** : Données entrent → Normalisées → Stockées → Exposées → Alertes réelles

---

## Prérequis

### VPS Hostinger
- 8GB RAM
- 4 vCPUs
- 200GB SSD
- Ubuntu 22.04 LTS
- IP publique

### Accès
```bash
ssh root@<VPS_IP>
```

### Logiciels Requis
- Docker 24+
- Docker Compose v2
- Git
- curl, jq

---

## Phase 1 - Préparation VPS

### 1.1 Connexion et Mise à Jour

```bash
# Connexion
ssh root@<VPS_IP>

# Mise à jour système
apt update && apt upgrade -y

# Installation outils de base
apt install -y curl wget git vim htop net-tools jq
```

### 1.2 Installation Docker

```bash
# Désinstaller anciennes versions
apt remove -y docker docker-engine docker.io containerd runc

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Vérification
docker --version
# Docker version 24.0.x

# Démarrage automatique
systemctl enable docker
systemctl start docker
```

### 1.3 Installation Docker Compose

```bash
# Installation Docker Compose v2
apt install -y docker-compose-plugin

# Vérification
docker compose version
# Docker Compose version v2.x.x
```

### 1.4 Configuration Firewall

```bash
# UFW (si installé)
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw allow 8000/tcp    # API (temporaire pour tests)
ufw enable

# Vérification
ufw status
```

---

## Phase 2 - Clonage et Configuration

### 2.1 Clonage Repository

```bash
# Créer répertoire projet
mkdir -p /opt/oceansentinel
cd /opt/oceansentinel

# Cloner repo
git clone https://github.com/oceansentinelle/OS3.0.git .

# Vérifier structure
ls -la
# Doit contenir: docker-compose-full.yml, workers/, api/, scripts/, alembic/
```

### 2.2 Configuration Environnement

```bash
# Copier exemple .env
cp .env.full.example .env

# Éditer .env
vim .env
```

**Variables critiques à modifier** :

```bash
# Database
POSTGRES_PASSWORD=<GÉNÉRER_MOT_DE_PASSE_FORT>
DB_PASSWORD=<MÊME_MOT_DE_PASSE>

# MinIO
MINIO_ROOT_PASSWORD=<GÉNÉRER_MOT_DE_PASSE_FORT>

# API
API_SECRET_KEY=<GÉNÉRER_CLÉ_SECRÈTE>

# Générer mots de passe forts
openssl rand -base64 32
```

**Variables sources à activer** :

```bash
# Phase 1 - MVP (commencer avec 2 sources max)
ENABLE_ERDDAP_COAST_HF=true
ENABLE_HUBEAU=true

# Désactiver le reste au début
ENABLE_ERDDAP_SOMLIT=false
ENABLE_SEANOE_LOADER=false
ENABLE_SIBA_LOADER=false

# Phase 2 - Référentiels (activer après MVP)
ENABLE_SHOM_REFERENCE=false
ENABLE_INSEE_GEO=false
ENABLE_INSEE_SIRENE=false
```

### 2.3 Création Répertoires

```bash
# Répertoires de données
mkdir -p data/seanoe
mkdir -p data_drop/siba/processed
mkdir -p alerts
mkdir -p grafana/provisioning

# Permissions
chmod -R 755 data data_drop alerts grafana
```

---

## Phase 3 - Déploiement Infrastructure

### 3.1 Build Images

```bash
cd /opt/oceansentinel

# Build toutes les images
docker compose -f docker-compose-full.yml build

# Vérifier images
docker images | grep os_
```

### 3.2 Démarrage Infrastructure Seule

```bash
# Démarrer PostgreSQL, Redis, MinIO uniquement
docker compose -f docker-compose-full.yml up -d postgres redis minio

# Vérifier logs
docker compose -f docker-compose-full.yml logs -f postgres
# Attendre: "database system is ready to accept connections"

docker compose -f docker-compose-full.yml logs -f redis
# Attendre: "Ready to accept connections"

docker compose -f docker-compose-full.yml logs -f minio
# Attendre: "API: http://..."
```

### 3.3 Vérification Healthchecks

```bash
# PostgreSQL
docker exec os_postgres pg_isready -U admin -d oceansentinel
# os_postgres:5432 - accepting connections

# Redis
docker exec os_redis redis-cli ping
# PONG

# MinIO
curl -f http://localhost:9000/minio/health/live
# OK
```

---

## Phase 4 - Initialisation Base de Données

### 4.1 Migrations Alembic

```bash
# Créer Dockerfile si manquant
cat > Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Créer requirements.txt si manquant
cat > requirements.txt <<'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.1
redis==5.0.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
apscheduler==3.10.4
EOF

# Rebuild avec Dockerfile
docker compose -f docker-compose-full.yml build api

# Lancer migrations
docker compose -f docker-compose-full.yml run --rm api alembic upgrade head

# Vérifier tables créées
docker exec os_postgres psql -U admin -d oceansentinel -c "\dt"
# Doit afficher: alembic_version, reference_entities, etc.
```

### 4.2 Seed Sources

```bash
# Lancer seed
docker compose -f docker-compose-full.yml run --rm api python scripts/seed_sources.py

# Vérifier sources
docker exec os_postgres psql -U admin -d oceansentinel -c "SELECT code, nom, is_active FROM sources;"
```

### 4.3 Initialisation Tables Pipeline

```bash
# Lancer script init
docker exec os_postgres psql -U admin -d oceansentinel -f /docker-entrypoint-initdb.d/01_init.sql

# Vérifier tables
docker exec os_postgres psql -U admin -d oceansentinel -c "\dt"
# Doit afficher: ocean_data, raw_ingestion_log, raw_payloads, validated_measurements, alerts, etc.
```

---

## Phase 5 - Démarrage Application

### 5.1 Lancement API

```bash
# Démarrer API
docker compose -f docker-compose-full.yml up -d api

# Vérifier logs
docker compose -f docker-compose-full.yml logs -f api
# Attendre: "Application startup complete"

# Test healthcheck
curl http://localhost:8000/api/v1/health
# {"status":"healthy","version":"3.0.0",...}

# Test pipeline status
curl http://localhost:8000/api/v1/pipeline/status | jq
```

### 5.2 Lancement Orchestrateur

```bash
# Démarrer orchestrateur
docker compose -f docker-compose-full.yml up -d orchestrator

# Vérifier logs
docker compose -f docker-compose-full.yml logs -f orchestrator
# Attendre: "job.scheduled" pour chaque job actif

# Vérifier jobs planifiés
docker compose -f docker-compose-full.yml logs orchestrator | grep "job.scheduled"
```

### 5.3 Lancement Workers

```bash
# Démarrer workers
docker compose -f docker-compose-full.yml up -d ingest_worker transform_worker alert_worker

# Vérifier statut
docker compose -f docker-compose-full.yml ps
```

---

## Phase 6 - Tests et Validation

### 6.1 Smoke Tests

```bash
# Rendre exécutable
chmod +x scripts/smoke_tests.sh

# Lancer tests
./scripts/smoke_tests.sh

# Résultat attendu:
# ✅ ALL TESTS PASSED (10/10)
```

### 6.2 Test Ingestion Manuelle

```bash
# Forcer run orchestrateur (pour tester immédiatement)
docker exec os_orchestrator python -c "
from workers.connectors.erddap_ifremer import ErddapCoastHFConnector
connector = ErddapCoastHFConnector(
    base_url='https://erddap.ifremer.fr/erddap',
    dataset_id='COAST-HF_Arcachon_Ferret',
    variables=['TEMP', 'PSAL']
)
result = connector.fetch_data()
print(f'Records: {len(result)}')
"
```

### 6.3 Vérification Données

```bash
# Vérifier ingestion
docker exec os_postgres psql -U admin -d oceansentinel -c "
SELECT COUNT(*) FROM raw_ingestion_log;
"

# Vérifier mesures validées
docker exec os_postgres psql -U admin -d oceansentinel -c "
SELECT 
    station_id,
    COUNT(*) as measurements,
    MAX(timestamp_utc) as last_measurement
FROM validated_measurements
GROUP BY station_id;
"

# Vérifier dernières mesures
docker exec os_postgres psql -U admin -d oceansentinel -c "
SELECT 
    timestamp_utc,
    station_id,
    temperature_water,
    salinity,
    quality_flag
FROM validated_measurements
ORDER BY timestamp_utc DESC
LIMIT 10;
"
```

---

## Phase 7 - Monitoring et Logs

### 7.1 Logs en Temps Réel

```bash
# Tous les services
docker compose -f docker-compose-full.yml logs -f

# Service spécifique
docker compose -f docker-compose-full.yml logs -f orchestrator
docker compose -f docker-compose-full.yml logs -f api
docker compose -f docker-compose-full.yml logs -f ingest_worker

# Dernières 100 lignes
docker compose -f docker-compose-full.yml logs --tail=100 orchestrator
```

### 7.2 Monitoring Ressources

```bash
# Stats conteneurs
docker stats

# Espace disque
df -h

# Mémoire
free -h

# Processus
htop
```

### 7.3 Vérification Santé Services

```bash
# Script de monitoring
cat > /opt/oceansentinel/monitor.sh <<'EOF'
#!/bin/bash
echo "=== Ocean Sentinel Health Check ==="
echo ""
echo "API Health:"
curl -s http://localhost:8000/api/v1/health | jq -r '.status'
echo ""
echo "Pipeline Status:"
curl -s http://localhost:8000/api/v1/pipeline/status | jq -r '.database.connected, .sources.active'
echo ""
echo "Containers:"
docker compose -f docker-compose-full.yml ps
echo ""
echo "Recent Ingestions:"
docker exec os_postgres psql -U admin -d oceansentinel -t -c "SELECT COUNT(*) FROM raw_ingestion_log WHERE fetched_at > NOW() - INTERVAL '1 hour';"
EOF

chmod +x /opt/oceansentinel/monitor.sh

# Lancer monitoring
./monitor.sh
```

---

## Phase 8 - Automatisation et Maintenance

### 8.1 Cron Job Monitoring

```bash
# Ajouter cron job
crontab -e

# Ajouter ligne (monitoring toutes les 5 minutes)
*/5 * * * * /opt/oceansentinel/monitor.sh >> /var/log/oceansentinel-monitor.log 2>&1
```

### 8.2 Backup Automatique

```bash
# Script backup
cat > /opt/oceansentinel/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/oceansentinel/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec os_postgres pg_dump -U admin oceansentinel | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup .env
cp .env $BACKUP_DIR/env_$DATE.bak

# Nettoyage backups > 30 jours
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/oceansentinel/backup.sh

# Ajouter cron (backup quotidien 3h du matin)
crontab -e
# 0 3 * * * /opt/oceansentinel/backup.sh >> /var/log/oceansentinel-backup.log 2>&1
```

### 8.3 Rotation Logs

```bash
# Configuration logrotate
cat > /etc/logrotate.d/oceansentinel <<'EOF'
/var/log/oceansentinel-*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

---

## Phase 9 - Troubleshooting

### 9.1 Problèmes Courants

#### Service ne démarre pas

```bash
# Vérifier logs
docker compose -f docker-compose-full.yml logs <service>

# Vérifier healthcheck
docker inspect os_<service> | jq '.[0].State.Health'

# Redémarrer service
docker compose -f docker-compose-full.yml restart <service>
```

#### Base de données inaccessible

```bash
# Vérifier connexion
docker exec os_postgres pg_isready -U admin

# Vérifier variables
docker exec os_postgres env | grep POSTGRES

# Recréer base (ATTENTION: perte données)
docker compose -f docker-compose-full.yml down -v
docker compose -f docker-compose-full.yml up -d postgres
```

#### Orchestrateur ne lance pas jobs

```bash
# Vérifier variables d'environnement
docker exec os_orchestrator env | grep ENABLE_

# Vérifier logs
docker compose -f docker-compose-full.yml logs orchestrator | grep "job.scheduled"

# Redémarrer orchestrateur
docker compose -f docker-compose-full.yml restart orchestrator
```

#### Pas de données ingérées

```bash
# Vérifier connectivité externe
docker exec os_orchestrator curl -I https://erddap.ifremer.fr/erddap

# Vérifier logs ingestion
docker compose -f docker-compose-full.yml logs ingest_worker

# Test manuel connecteur
docker exec os_orchestrator python -c "
from workers.connectors.erddap_ifremer import ErddapCoastHFConnector
connector = ErddapCoastHFConnector(...)
result = connector.fetch_data()
print(result)
"
```

### 9.2 Commandes Utiles

```bash
# Redémarrer tout
docker compose -f docker-compose-full.yml restart

# Arrêter tout
docker compose -f docker-compose-full.yml down

# Supprimer volumes (ATTENTION: perte données)
docker compose -f docker-compose-full.yml down -v

# Rebuild complet
docker compose -f docker-compose-full.yml build --no-cache
docker compose -f docker-compose-full.yml up -d

# Nettoyer Docker
docker system prune -a --volumes
```

---

## Phase 10 - Validation Finale

### 10.1 Checklist Déploiement

- [ ] VPS accessible via SSH
- [ ] Docker et Docker Compose installés
- [ ] Repository cloné
- [ ] `.env` configuré avec mots de passe forts
- [ ] Images Docker buildées
- [ ] PostgreSQL démarré et accessible
- [ ] Redis démarré et accessible
- [ ] MinIO démarré et accessible
- [ ] Migrations Alembic exécutées
- [ ] Sources seedées
- [ ] Tables pipeline initialisées
- [ ] API démarrée et healthcheck OK
- [ ] Orchestrateur démarré et jobs planifiés
- [ ] Workers démarrés
- [ ] Smoke tests passés (10/10)
- [ ] Données ingérées (au moins 1 source)
- [ ] Monitoring configuré
- [ ] Backups automatisés

### 10.2 Tests de Validation

```bash
# 1. API Health
curl http://localhost:8000/api/v1/health

# 2. Pipeline Status
curl http://localhost:8000/api/v1/pipeline/status | jq

# 3. Sources actives
docker exec os_postgres psql -U admin -d oceansentinel -c "SELECT code, is_active FROM sources WHERE is_active = true;"

# 4. Ingestions récentes
docker exec os_postgres psql -U admin -d oceansentinel -c "SELECT source_name, COUNT(*) FROM raw_ingestion_log WHERE fetched_at > NOW() - INTERVAL '24 hours' GROUP BY source_name;"

# 5. Mesures validées
docker exec os_postgres psql -U admin -d oceansentinel -c "SELECT COUNT(*) FROM validated_measurements;"

# 6. Alertes actives
docker exec os_postgres psql -U admin -d oceansentinel -c "SELECT COUNT(*) FROM alerts WHERE status = 'active';"
```

---

## Résultat Attendu

Après déploiement complet, vous devriez avoir :

✅ **Infrastructure** : PostgreSQL, Redis, MinIO opérationnels  
✅ **Application** : API, Orchestrateur, Workers en cours d'exécution  
✅ **Données** : Ingestion réelle depuis au moins 2 sources (ERDDAP, Hub'Eau)  
✅ **Monitoring** : Healthchecks, logs, métriques accessibles  
✅ **Automatisation** : Backups quotidiens, monitoring 5min  

**Le pipeline backend Ocean Sentinel V3.0 est maintenant en production et ingère des données réelles !** 🌊🚀
