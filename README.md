# 🌊 Ocean Sentinel V3.0

**Système de surveillance océanographique autonome pour le Bassin d'Arcachon**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)
[![TimescaleDB](https://img.shields.io/badge/timescaledb-latest-orange.svg)](https://www.timescale.com/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![Grafana](https://img.shields.io/badge/grafana-latest-orange.svg)](https://grafana.com/)

Infrastructure complète d'ingestion, stockage, analyse et visualisation de données océanographiques en temps réel depuis les sources NOAA ERDDAP et SEANOE.

## � Table des Matières

- [Vue d'Ensemble](#-vue-densemble)
- [Architecture](#-architecture)
- [Fonctionnalités](#-fonctionnalités)
- [Démarrage Rapide](#-démarrage-rapide)
- [Déploiement Production](#-déploiement-production)
- [API REST](#-api-rest)
- [Monitoring Agent](#-monitoring-agent)
- [Documentation](#-documentation)
- [Maintenance](#-maintenance)

---

## 🎯 Vue d'Ensemble

**Ocean Sentinel V3.0** est une infrastructure complète de surveillance océanographique déployée sur VPS, conçue pour :

✅ **Ingérer** des données océanographiques depuis NOAA ERDDAP (failover SEANOE)  
✅ **Stocker** dans TimescaleDB avec compression et rétention automatiques  
✅ **Exposer** via API REST FastAPI avec alertes écologiques SACS  
✅ **Visualiser** avec Grafana (dashboards provisionnés automatiquement)  
✅ **Monitorer** via compétence agent Antigravity  
✅ **Prédire** avec pipeline Machine Learning (LSTM + Isolation Forest)  

### 🌍 Station Surveillée

**COAST-HF Bassin d'Arcachon (BARAG)**
- **Localisation** : 44.666°N, -1.25°W
- **Paramètres** : Température, Salinité, pH, Oxygène dissous, Turbidité
- **Fréquence** : Données horaires
- **Source primaire** : NOAA ERDDAP
- **Source secondaire** : SEANOE (failover automatique)

### 📊 Données Collectées

| Paramètre | Unité | Seuil SACS | Description |
|-----------|-------|------------|-------------|
| **TEMP** | °C | - | Température de l'eau |
| **PSAL** | PSU | - | Salinité pratique |
| **DOX2** | µmol/kg | < 150 (warning)<br>< 100 (critical) | Oxygène dissous |
| **pH** | pH | < 7.8 (warning)<br>< 7.5 (critical) | Acidité de l'eau |
| **TURB** | NTU | - | Turbidité |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SOURCES DE DONNÉES                        │
│  NOAA ERDDAP (primaire) ←→ SEANOE (failover automatique)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              SERVICE D'INGESTION (Python)                    │
│  • Polling horaire                                           │
│  • Validation données                                        │
│  • Gestion erreurs réseau                                    │
│  • Failover ERDDAP → SEANOE                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            TIMESCALEDB (PostgreSQL 16)                       │
│  • Hypertables (partitionnement automatique)                │
│  • Compression après 7 jours                                 │
│  • Rétention 2 ans                                           │
│  • Port 6543                                                 │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│   API REST (FastAPI)    │  │   GRAFANA (Visualisation)    │
│  • GET /health          │  │  • Dashboard 8 panneaux      │
│  • GET /latest          │  │  • Provisioning automatique  │
│  • GET /history         │  │  • Alertes SACS intégrées    │
│  • GET /alerts/sacs     │  │  • Port 3000                 │
│  • Port 8000            │  │                              │
└────────────┬────────────┘  └──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│         MONITORING AGENT (Compétence Antigravity)            │
│  • Health checks API                                         │
│  • Vérification alertes SACS                                 │
│  • Rapport JSON                                              │
└─────────────────────────────────────────────────────────────┘
```

### 🐳 Services Docker

| Service | Image | RAM | Ports | Rôle |
|---------|-------|-----|-------|------|
| **timescaledb** | `timescale/timescaledb:latest-pg16` | 256 Mo | 6543 | Base de données |
| **ingestion** | `oceansentinel-ingestion` | 256 Mo | - | Ingestion NOAA |
| **api** | `oceansentinel-api` | 128 Mo | 8000 | API REST |
| **grafana** | `grafana/grafana:latest` | 128 Mo | 3000 | Visualisation |

## ⚡ Fonctionnalités

### 🔄 Ingestion de Données
- ✅ Polling automatique NOAA ERDDAP (horaire)
- ✅ Failover automatique vers SEANOE si ERDDAP indisponible
- ✅ Validation et nettoyage des données
- ✅ Gestion robuste des erreurs réseau
- ✅ Logging détaillé

### 💾 Stockage TimescaleDB
- ✅ Hypertables avec partitionnement automatique par jour
- ✅ Compression automatique après 7 jours (ratio ~70-90%)
- ✅ Politique de rétention 2 ans
- ✅ Indexation optimisée pour requêtes temporelles
- ✅ Backups automatiques quotidiens

### 🌐 API REST
- ✅ **GET /** - Informations API
- ✅ **GET /health** - Health check (DB + stats)
- ✅ **GET /api/v1/station/{id}/latest** - Dernière mesure
- ✅ **GET /api/v1/station/{id}/history** - Historique (plage temporelle)
- ✅ **GET /api/v1/alerts/sacs** - Alertes écologiques SACS
- ✅ Documentation Swagger interactive (/docs)

### � Visualisation Grafana
- ✅ Dashboard "Ocean Sentinel - COAST-HF Bassin d'Arcachon"
- ✅ 8 panneaux : Température, Salinité, Oxygène, pH, Statistiques
- ✅ Provisioning automatique (datasource + dashboard)
- ✅ Alertes visuelles SACS intégrées
- ✅ Rafraîchissement automatique 30s

### 🚨 Système d'Alertes SACS (Vigilance Écologique)

**Seuils de surveillance :**

| Paramètre | Normal | Warning | Critical |
|-----------|--------|---------|----------|
| **pH** | ≥ 8.0 | 7.8 - 8.0 | < 7.8 |
| **Oxygène (DOX2)** | ≥ 200 µmol/kg | 150 - 200 | < 150 |

**Niveaux d'alerte :**
- 🟢 **NORMAL** : Tous les paramètres dans les normes
- 🟡 **WARNING** : Un paramètre en zone d'attention
- 🔴 **CRITICAL** : Un paramètre en zone critique

### 🤖 Monitoring Agent
- ✅ Compétence Antigravity `ocean-sentinel-ops` v2.0.0
- ✅ Health checks API automatiques
- ✅ Vérification alertes SACS
- ✅ Rapport JSON structuré
- ✅ Exécutable depuis machine locale

### 🧠 Machine Learning (Optionnel)
- ✅ Modèle LSTM pour prédiction température/salinité
- ✅ Détection d'anomalies (Isolation Forest)
- ✅ Pipeline complet : ingestion → entraînement → prédiction

---

## 🚀 Démarrage Rapide

### Prérequis

- Docker & Docker Compose v2+
- Git
- 512 Mo RAM minimum (768 Mo recommandé avec swap)
- Ports disponibles : 6543, 8000, 3000

### Installation Locale (Développement)

```bash
# 1. Cloner le dépôt
git clone git@github.com:oceansentinelle/OS3.0.git
cd OS3.0

# 2. Configurer l'environnement
cp .env.vps.example .env
nano .env  # Éditer POSTGRES_PASSWORD

# 3. Lancer la stack complète
docker compose -f docker-compose-v3.yml up -d

# 4. Vérifier les services
docker compose -f docker-compose-v3.yml ps

# 5. Tester l'API
curl http://localhost:8000/health

# 6. Accéder à Grafana
# http://localhost:3000 (admin/admin)
```

## � Déploiement Production

### VPS Hostinger (Ubuntu 22.04)

**Configuration recommandée :**
- **RAM** : 512 Mo + swap 512 Mo
- **CPU** : 1-2 vCPU
- **Stockage** : 20 Go SSD
- **OS** : Ubuntu 22.04 LTS

### Étape 1 : Préparation du VPS

```bash
# Connexion SSH
ssh root@VOTRE_IP_VPS

# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation Docker Compose v2
sudo apt install docker-compose-plugin -y

# Création répertoire projet
sudo mkdir -p /opt/oceansentinel
sudo chown $USER:$USER /opt/oceansentinel
cd /opt/oceansentinel
```

### Étape 2 : Transfert des Fichiers

**Depuis votre machine locale (Windows PowerShell) :**

```powershell
# Transfert docker-compose
scp -P 22 docker-compose-vps.yml root@VOTRE_IP_VPS:/opt/oceansentinel/

# Transfert Dockerfile API
scp -P 22 Dockerfile.api root@VOTRE_IP_VPS:/opt/oceansentinel/

# Transfert dossier API
scp -P 22 -r api root@VOTRE_IP_VPS:/opt/oceansentinel/

# Transfert dossier Grafana
scp -P 22 -r grafana root@VOTRE_IP_VPS:/opt/oceansentinel/

# Transfert fichier .env
scp -P 22 .env.vps root@VOTRE_IP_VPS:/opt/oceansentinel/.env
```

### Étape 3 : Configuration Pare-feu

```bash
# UFW (sur le VPS)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # API REST
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 6543/tcp  # TimescaleDB (optionnel)
sudo ufw enable
sudo ufw status
```

**⚠️ N'oubliez pas de configurer aussi le pare-feu Hostinger via le panneau web !**

### Étape 4 : Déploiement

```bash
# Sur le VPS
cd /opt/oceansentinel

# Construire l'image API
docker compose -f docker-compose-vps.yml build api

# Démarrer tous les services
docker compose -f docker-compose-vps.yml up -d

# Vérifier le statut
docker compose -f docker-compose-vps.yml ps

# Vérifier les logs
docker compose -f docker-compose-vps.yml logs -f
```

### Étape 5 : Vérification

```bash
# Test API (depuis le VPS)
curl http://localhost:8000/health

# Test Grafana (depuis le VPS)
curl -I http://localhost:3000

# Vérifier les ports ouverts
netstat -tlnp | grep -E '8000|3000|6543'
```

**Accès web :**
- API REST : `http://VOTRE_IP_VPS:8000`
- API Docs : `http://VOTRE_IP_VPS:8000/docs`
- Grafana : `http://VOTRE_IP_VPS:3000` (admin/admin)

---

## 🌐 API REST

### Endpoints Disponibles

#### **GET /**
Informations générales sur l'API.

```bash
curl http://VOTRE_IP_VPS:8000/
```

**Réponse :**
```json
{
  "name": "Ocean Sentinel API",
  "version": "3.0.0",
  "description": "API REST pour accès aux données océanographiques COAST-HF"
}
```

#### **GET /health**
Health check avec statistiques base de données.

```bash
curl http://VOTRE_IP_VPS:8000/health
```

**Réponse :**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-04-17T12:00:00",
  "total_records": 1523
}
```

#### **GET /api/v1/station/{station_id}/latest**
Dernière mesure pour une station.

```bash
curl http://VOTRE_IP_VPS:8000/api/v1/station/VPS_PROD/latest
```

**Réponse :**
```json
{
  "station_id": "VPS_PROD",
  "time": "2026-04-17T11:00:00+00:00",
  "temperature_water": 15.2,
  "salinity": 35.1,
  "ph": 8.05,
  "dissolved_oxygen": 245.3,
  "turbidity": 2.1,
  "quality_flag": 1
}
```

#### **GET /api/v1/station/{station_id}/history**
Historique sur une plage temporelle.

**Paramètres :**
- `start_time` : ISO 8601 (ex: 2026-04-16T00:00:00Z)
- `end_time` : ISO 8601 (ex: 2026-04-17T00:00:00Z)
- `limit` : Nombre max de résultats (défaut: 100)

```bash
curl "http://VOTRE_IP_VPS:8000/api/v1/station/VPS_PROD/history?start_time=2026-04-16T00:00:00Z&end_time=2026-04-17T00:00:00Z&limit=50"
```

#### **GET /api/v1/alerts/sacs**
Alertes écologiques SACS (pH, oxygène).

```bash
curl http://VOTRE_IP_VPS:8000/api/v1/alerts/sacs
```

**Réponse (aucune alerte) :**
```json
{
  "status": "normal",
  "alerts": [],
  "last_check": "2026-04-17T12:00:00+00:00",
  "station_id": "VPS_PROD"
}
```

**Réponse (alerte active) :**
```json
{
  "status": "warning",
  "alerts": [
    {
      "parameter": "ph",
      "value": 7.75,
      "threshold": 7.8,
      "level": "warning",
      "message": "pH en dessous du seuil d'attention (7.8)"
    }
  ],
  "last_check": "2026-04-17T12:00:00+00:00",
  "station_id": "VPS_PROD"
}
```

### Documentation Interactive

Accédez à la documentation Swagger : **http://VOTRE_IP_VPS:8000/docs**

---

## 🤖 Monitoring Agent

### Compétence Antigravity `ocean-sentinel-ops`

**Localisation :** `.agents/skills/ocean-sentinel-ops/`

### Utilisation

**Depuis votre machine locale (Windows PowerShell) :**

```powershell
cd C:\Users\VOTRE_USER\Documents\OSwindsurf\.agents\skills\ocean-sentinel-ops

# Monitoring complet
python scripts\monitor.py --vps-ip VOTRE_IP_VPS

# Rapport JSON
python scripts\monitor.py --vps-ip VOTRE_IP_VPS --json

# Aide
python scripts\monitor.py --help
```

### Exemple de Rapport

```
================================================================================
OCEAN SENTINEL OPS - MONITORING VPS
================================================================================
ℹ️  VPS: 76.13.43.3:8000

✅ Statut général: HEALTHY

ℹ️  API REST:
✅   Statut: healthy

ℹ️  Base de données:
✅   Statut: connected
ℹ️   Total enregistrements: 1523

ℹ️  Alertes SACS:
✅   Aucune alerte active

ℹ️  Dernière mesure:
✅   Station: VPS_PROD
ℹ️   Timestamp: 2026-04-17T11:00:00+00:00
ℹ️   Température: 15.2 °C
ℹ️   Salinité: 35.1 PSU
ℹ️   Qualité: QC=1
```

## 🔧 Configuration Optimisée

### Paramètres Mémoire (8 Go RAM)
```conf
shared_buffers = 2GB              # 25% de la RAM
effective_cache_size = 4GB        # 50% de la RAM
work_mem = 20MB
maintenance_work_mem = 512MB
```

### Parallélisme (4 vCPU)
```conf
max_worker_processes = 8
max_parallel_workers = 4
timescaledb.max_background_workers = 8
```

### Compression
- **Délai:** 7 jours après insertion
- **Méthode:** Segmentation par `station_id`, tri par `time DESC`
- **Ratio attendu:** ~70-90% de réduction

## 📈 Monitoring

### Vues de Monitoring Intégrées

```sql
-- État des chunks et compression
SELECT * FROM metadata.chunk_status;

-- Statistiques d'ingestion
SELECT * FROM metadata.ingestion_stats;

-- Requêtes lentes
SELECT * FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;
```

### Commandes Utiles

```bash
# Ressources du conteneur
docker stats oceansentinel_timescaledb

# Logs PostgreSQL
docker exec oceansentinel_timescaledb tail -f /var/lib/postgresql/data/pg_log/postgresql-*.log

# Taille de la base
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT pg_size_pretty(pg_database_size('oceansentinelle'));"
```

## 🔐 Sécurité

### Checklist de Sécurité

- [ ] Mot de passe fort pour `POSTGRES_PASSWORD` (min 16 caractères)
- [ ] Changement des mots de passe par défaut des rôles
- [ ] Port non-standard configuré (6543)
- [ ] Pare-feu UFW activé et configuré
- [ ] Pare-feu Hostinger configuré
- [ ] SSL/TLS activé (production)
- [ ] Fail2Ban installé (optionnel)
- [ ] Backups automatiques configurés
- [ ] `.env` ajouté au `.gitignore`

### Configuration Pare-feu

```bash
# UFW
sudo ufw allow 22/tcp
sudo ufw allow 6543/tcp
sudo ufw enable

# Vérification
sudo ufw status
```

## 📚 Documentation

### Fichiers du Projet

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Référence rapide des commandes
- **[QUERY_SCRIPT_GUIDE.md](QUERY_SCRIPT_GUIDE.md)** - Guide des requêtes SQL
- **[.agents/skills/ocean-sentinel-ops/SKILL.md](.agents/skills/ocean-sentinel-ops/SKILL.md)** - Documentation compétence agent

### Ressources Externes

- **[TimescaleDB Docs](https://docs.timescale.com/)** - Documentation officielle TimescaleDB
- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - Documentation FastAPI
- **[Grafana Docs](https://grafana.com/docs/)** - Documentation Grafana
- **[NOAA ERDDAP](https://coastwatch.pfeg.noaa.gov/erddap/)** - Source de données primaire
- **[SEANOE](https://www.seanoe.org/)** - Source de données secondaire

## 🛠️ Maintenance

### Backups Automatiques

**Configuration :**

```bash
# Sur le VPS
cd /opt/oceansentinel
chmod +x setup-backups.sh
./setup-backups.sh
```

Cela configure :
- Backups quotidiens à 2h00 du matin
- Rotation sur 7 jours
- Compression gzip
- Stockage dans `/opt/oceansentinel/backups/`

### Backup Manuel

```bash
# Créer un backup
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel -Fc oceansentinelle \
    > backup_$(date +%Y%m%d_%H%M%S).dump

# Restaurer un backup
docker exec -i oceansentinel_timescaledb pg_restore -U oceansentinel -d oceansentinelle \
    < backup_20260417_120000.dump
```

### Monitoring des Services

```bash
# Statut des conteneurs
docker compose -f docker-compose-vps.yml ps

# Logs en temps réel
docker compose -f docker-compose-vps.yml logs -f

# Logs d'un service spécifique
docker compose -f docker-compose-vps.yml logs -f api

# Utilisation ressources
docker stats

# Espace disque
df -h
du -sh /opt/oceansentinel/*
```

### Redémarrage des Services

```bash
# Redémarrer tous les services
docker compose -f docker-compose-vps.yml restart

# Redémarrer un service spécifique
docker compose -f docker-compose-vps.yml restart api

# Reconstruire et redémarrer l'API
docker compose -f docker-compose-vps.yml build api
docker compose -f docker-compose-vps.yml up -d api
```

### Nettoyage

```bash
# Supprimer les images inutilisées
docker image prune -a

# Supprimer les volumes inutilisés
docker volume prune

# Nettoyage complet
docker system prune -a --volumes
```

### Mise à Jour

```bash
# 1. Backup avant mise à jour
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel -Fc oceansentinelle \
    > backup_avant_maj_$(date +%Y%m%d).dump

# 2. Mettre à jour les images
docker compose -f docker-compose-vps.yml pull

# 3. Reconstruire l'API si nécessaire
docker compose -f docker-compose-vps.yml build api

# 4. Redémarrer les services
docker compose -f docker-compose-vps.yml up -d

# 5. Vérifier les versions
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT extname, extversion FROM pg_extension WHERE extname = 'timescaledb';"
```

---

## 🐛 Troubleshooting

### Services ne Démarrent Pas

```bash
# Vérifier les logs
docker compose -f docker-compose-vps.yml logs

# Vérifier les logs d'un service spécifique
docker compose -f docker-compose-vps.yml logs timescaledb
docker compose -f docker-compose-vps.yml logs api

# Vérifier l'état des conteneurs
docker compose -f docker-compose-vps.yml ps

# Vérifier les permissions
sudo chown -R 999:999 /opt/oceansentinel/data
```

### API Inaccessible

```bash
# Vérifier que le port est ouvert
sudo netstat -tlnp | grep 8000

# Vérifier le pare-feu
sudo ufw status

# Tester localement sur le VPS
curl http://localhost:8000/health

# Vérifier les logs API
docker compose -f docker-compose-vps.yml logs api
```

### Grafana Affiche "No Data"

```bash
# Vérifier la connexion datasource
# Dans Grafana : Connections → Data sources → TimescaleDB → Save & test

# Vérifier les données dans la base
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT COUNT(*), MIN(time), MAX(time) FROM ocean_data;"

# Vérifier l'UID de la datasource dans les logs
docker compose -f docker-compose-vps.yml logs grafana | grep -i "datasource"

# Corriger l'UID dans le dashboard si nécessaire
# Voir QUERY_SCRIPT_GUIDE.md pour les détails
```

### Ingestion ne Fonctionne Pas

```bash
# Vérifier les logs d'ingestion
docker compose -f docker-compose-vps.yml logs ingestion

# Tester manuellement ERDDAP
curl "https://coastwatch.pfeg.noaa.gov/erddap/tabledap/BARAG.csv?time,temperature_water,salinity&time>=2026-04-16T00:00:00Z&time<=2026-04-17T00:00:00Z"

# Redémarrer le service d'ingestion
docker compose -f docker-compose-vps.yml restart ingestion
```

### Mémoire Insuffisante

```bash
# Vérifier l'utilisation mémoire
free -h
docker stats

# Activer le swap si nécessaire
sudo fallocate -l 512M /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Rendre permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 📦 Structure du Projet

```
OS3.0/
├── .agents/
│   └── skills/ocean-sentinel-ops/    # Compétence agent Antigravity
│       ├── SKILL.md
│       ├── README.md
│       └── scripts/
│           ├── monitor.py              # Script de monitoring
│           ├── check_logs.sh
│           └── query_prod_db.py
├── api/                           # API REST FastAPI
│   ├── main.py
│   ├── alerts.py                   # Système d'alertes SACS
│   └── requirements.txt
├── grafana/                       # Configuration Grafana
│   └── provisioning/
│       ├── datasources/
│       │   └── datasource.yml
│       └── dashboards/
│           ├── dashboard.yml
│           └── ocean_sentinel.json
├── scripts/                       # Scripts Python
│   ├── ingestion_stream.py         # Ingestion NOAA
│   ├── ml_pipeline.py              # Machine Learning
│   ├── query.py                    # Requêtes SQL
│   └── test_*.py                   # Scripts de test
├── docker-compose.yml             # Dev local
├── docker-compose-v3.yml          # Stack complète
├── docker-compose-vps.yml         # Production VPS
├── Dockerfile.api                 # Build API
├── .env.vps.example               # Template config
├── setup-backups.sh               # Configuration backups
├── QUICK_REFERENCE.md             # Référence rapide
├── QUERY_SCRIPT_GUIDE.md          # Guide SQL
└── README.md                      # Ce fichier
```

---

## 🎓 Missions Complétées

- ✅ **Mission 1-3** : Infrastructure TimescaleDB + Ingestion NOAA
- ✅ **Mission 4** : Failover ERDDAP/SEANOE
- ✅ **Mission 5** : Pipeline Machine Learning (LSTM + Isolation Forest)
- ✅ **Mission 6** : Backups automatiques
- ✅ **Mission 7** : Compétence agent v1.0
- ✅ **Mission 8** : API REST + Grafana + Alertes SACS
- ✅ **Mission 9** : Déploiement VPS + Agent v2.0 (95%)

---

## 📞 Support

Pour toute question :
1. Consultez la documentation dans le dépôt
2. Vérifiez les logs : `docker compose logs -f`
3. Utilisez le monitoring agent : `python scripts/monitor.py`
4. Consultez les ressources externes listées ci-dessus

---

## 📄 Licence

MIT License - Projet Ocean Sentinel V3.0 - 2026

---

## ✨ Contributeurs

Projet développé dans le cadre de la surveillance océanographique du Bassin d'Arcachon.

**Développé avec ❤️ pour la surveillance océanographique**

---

**🌊 Ocean Sentinel V3.0** - *Surveiller, Analyser, Préserver*
