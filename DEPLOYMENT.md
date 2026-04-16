# 🌊 Ocean Sentinel - Guide de Déploiement TimescaleDB

## 📋 Prérequis

### Infrastructure VPS Hostinger
- **OS:** Ubuntu 22.04 LTS
- **RAM:** 8 Go
- **vCPU:** 4 cœurs
- **Stockage:** ≥ 50 Go SSD (recommandé 100 Go pour les données)
- **Accès:** SSH root ou sudo

### Logiciels Requis
```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation Docker Compose
sudo apt install docker-compose-plugin -y

# Vérification
docker --version
docker compose version
```

---

## 🚀 Déploiement Étape par Étape

### 1️⃣ Préparation du Serveur

#### Création du répertoire de données
```bash
# Créer la structure de répertoires
sudo mkdir -p /opt/oceansentinel/data
sudo chown -R 999:999 /opt/oceansentinel/data  # UID/GID de postgres dans le conteneur
sudo chmod 700 /opt/oceansentinel/data
```

#### Configuration du pare-feu UFW
```bash
# Activer UFW si nécessaire
sudo ufw enable

# Autoriser SSH (IMPORTANT: avant de bloquer les autres ports)
sudo ufw allow 22/tcp

# Autoriser le port PostgreSQL non-standard (6543)
sudo ufw allow 6543/tcp comment 'TimescaleDB Ocean Sentinel'

# Vérifier les règles
sudo ufw status numbered

# Recharger
sudo ufw reload
```

#### Pare-feu Hostinger (Panel Web)
1. Connectez-vous au panel Hostinger
2. Allez dans **VPS → Pare-feu**
3. Ajoutez une règle:
   - **Port:** 6543
   - **Protocole:** TCP
   - **Source:** `0.0.0.0/0` (ou restreindre aux IPs de confiance)
   - **Action:** Autoriser

---

### 2️⃣ Configuration de l'Application

#### Cloner ou transférer les fichiers
```bash
# Créer le répertoire du projet
mkdir -p ~/oceansentinel
cd ~/oceansentinel

# Transférer les fichiers via SCP (depuis votre machine locale)
# scp -r * user@vps-ip:~/oceansentinel/
```

#### Configuration des variables d'environnement
```bash
# Copier le template
cp .env.example .env

# Générer un mot de passe fort
openssl rand -base64 32

# Éditer le fichier .env
nano .env
```

**Modifiez au minimum:**
```env
POSTGRES_PASSWORD=VOTRE_MOT_DE_PASSE_GENERE_ICI
POSTGRES_PORT=6543
```

#### Modifier les mots de passe des rôles
```bash
nano init-scripts/01-init-timescaledb.sql
```

Remplacez:
- `readonly_changeme` → mot de passe fort pour lecture seule
- `writer_changeme` → mot de passe fort pour écriture

---

### 3️⃣ Lancement de TimescaleDB

#### Démarrage du conteneur
```bash
# Lancer en arrière-plan
docker compose up -d

# Vérifier les logs
docker compose logs -f timescaledb
```

**Attendez le message:**
```
✓ TimescaleDB initialisé avec succès pour Ocean Sentinel
```

#### Vérification de la santé
```bash
# Vérifier que le conteneur est en cours d'exécution
docker ps | grep oceansentinel

# Tester la connexion
docker exec oceansentinel_timescaledb pg_isready -U oceansentinel -d oceansentinelle
```

---

### 4️⃣ Tuning Automatique

#### Exécution du script de tuning
```bash
# Rendre le script exécutable
chmod +x scripts/tune-timescaledb.sh

# Exécuter le tuning
./scripts/tune-timescaledb.sh
```

**Le script va:**
1. ✅ Vérifier que le conteneur est actif
2. ✅ Sauvegarder la configuration actuelle
3. ✅ Exécuter `timescaledb-tune` avec les paramètres optimaux
4. ✅ Redémarrer le conteneur
5. ✅ Vérifier la disponibilité

#### Vérification des paramètres appliqués
```bash
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT name, setting, unit 
FROM pg_settings 
WHERE name IN (
    'shared_buffers', 
    'effective_cache_size', 
    'work_mem',
    'maintenance_work_mem',
    'max_worker_processes',
    'timescaledb.max_background_workers'
);"
```

---

## 🔍 Vérifications Post-Déploiement

### Test de Connexion Externe
```bash
# Depuis votre machine locale
psql -h VOTRE_IP_VPS -p 6543 -U oceansentinel -d oceansentinelle
```

### Vérification des Hypertables
```sql
-- Se connecter à la base
\c oceansentinelle

-- Lister les hypertables
SELECT * FROM timescaledb_information.hypertables;

-- Vérifier les politiques de compression
SELECT * FROM timescaledb_information.jobs 
WHERE proc_name = 'policy_compression';

-- Vérifier les agrégats continus
SELECT view_name, materialization_hypertable_name 
FROM timescaledb_information.continuous_aggregates;
```

### Monitoring des Chunks
```sql
-- Vue d'ensemble des chunks
SELECT * FROM metadata.chunk_status LIMIT 10;

-- Statistiques d'ingestion
SELECT * FROM metadata.ingestion_stats;
```

---

## 🔐 Sécurité Renforcée

### 1. Restriction par IP (Recommandé)
Modifiez `docker-compose.yml`:
```yaml
ports:
  - "VOTRE_IP_FIXE:6543:5432"  # Remplacez VOTRE_IP_FIXE
```

### 2. Activation SSL/TLS
```bash
# Générer les certificats
sudo mkdir -p /opt/oceansentinel/certs
cd /opt/oceansentinel/certs

# Certificat auto-signé (pour tests)
sudo openssl req -new -x509 -days 365 -nodes -text \
  -out server.crt -keyout server.key \
  -subj "/CN=oceansentinel.local"

# Permissions
sudo chown 999:999 server.key server.crt
sudo chmod 600 server.key
sudo chmod 644 server.crt
```

Modifiez `postgresql-custom.conf`:
```conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
```

Ajoutez dans `docker-compose.yml`:
```yaml
volumes:
  - /opt/oceansentinel/certs/server.crt:/etc/ssl/certs/server.crt:ro
  - /opt/oceansentinel/certs/server.key:/etc/ssl/private/server.key:ro
```

### 3. Fail2Ban (Protection contre brute-force)
```bash
sudo apt install fail2ban -y

# Créer un filtre pour PostgreSQL
sudo nano /etc/fail2ban/filter.d/postgresql.conf
```

Contenu:
```ini
[Definition]
failregex = FATAL:.*authentication failed for user.*
            FATAL:.*password authentication failed.*
ignoreregex =
```

Activer dans `/etc/fail2ban/jail.local`:
```ini
[postgresql]
enabled = true
port = 6543
filter = postgresql
logpath = /var/log/postgresql/postgresql-*.log
maxretry = 5
bantime = 3600
```

---

## 📊 Monitoring et Maintenance

### Logs en Temps Réel
```bash
# Logs du conteneur
docker compose logs -f timescaledb

# Logs PostgreSQL internes
docker exec oceansentinel_timescaledb tail -f /var/lib/postgresql/data/pg_log/postgresql-*.log
```

### Statistiques de Performance
```sql
-- Top 10 des requêtes les plus lentes
SELECT 
    calls,
    total_exec_time,
    mean_exec_time,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Taille de la base
SELECT 
    pg_size_pretty(pg_database_size('oceansentinelle')) AS db_size;

-- Taille des hypertables
SELECT 
    hypertable_name,
    pg_size_pretty(total_bytes) AS total_size,
    pg_size_pretty(compressed_total_bytes) AS compressed_size
FROM timescaledb_information.hypertables h
JOIN timescaledb_information.compression_settings cs 
    ON h.hypertable_name = cs.hypertable_name;
```

### Backup Automatique
```bash
# Créer un script de backup
sudo nano /opt/oceansentinel/backup.sh
```

Contenu:
```bash
#!/bin/bash
BACKUP_DIR="/opt/oceansentinel/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER="oceansentinel_timescaledb"

mkdir -p $BACKUP_DIR

docker exec $CONTAINER pg_dump -U oceansentinel -Fc oceansentinelle \
    > $BACKUP_DIR/oceansentinelle_$TIMESTAMP.dump

# Garder seulement les 7 derniers backups
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete

echo "Backup créé: oceansentinelle_$TIMESTAMP.dump"
```

Automatiser avec cron:
```bash
sudo chmod +x /opt/oceansentinel/backup.sh
crontab -e

# Ajouter: Backup quotidien à 2h du matin
0 2 * * * /opt/oceansentinel/backup.sh >> /var/log/oceansentinel-backup.log 2>&1
```

---

## 🔄 Commandes Utiles

### Gestion du Conteneur
```bash
# Démarrer
docker compose up -d

# Arrêter
docker compose down

# Redémarrer
docker compose restart

# Voir les ressources utilisées
docker stats oceansentinel_timescaledb

# Shell interactif
docker exec -it oceansentinel_timescaledb bash

# Connexion psql
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle
```

### Maintenance PostgreSQL
```sql
-- Analyser les tables
ANALYZE;

-- Vacuum complet
VACUUM FULL;

-- Reindex
REINDEX DATABASE oceansentinelle;

-- Vérifier l'intégrité
SELECT * FROM timescaledb_information.job_stats;
```

---

## ⚠️ Troubleshooting

### Problème: Le conteneur ne démarre pas
```bash
# Vérifier les logs
docker compose logs timescaledb

# Vérifier les permissions du volume
ls -la /opt/oceansentinel/data
sudo chown -R 999:999 /opt/oceansentinel/data
```

### Problème: Impossible de se connecter depuis l'extérieur
```bash
# Vérifier que le port est ouvert
sudo netstat -tlnp | grep 6543

# Tester depuis le serveur
telnet localhost 6543

# Vérifier UFW
sudo ufw status

# Vérifier les logs de connexion
docker exec oceansentinel_timescaledb grep "connection" /var/lib/postgresql/data/pg_log/postgresql-*.log
```

### Problème: Performances dégradées
```sql
-- Vérifier les chunks non compressés
SELECT * FROM timescaledb_information.chunks
WHERE is_compressed = false
AND range_end < NOW() - INTERVAL '7 days';

-- Forcer la compression manuelle
SELECT compress_chunk(i.show_chunks)
FROM show_chunks('barag.sensor_data', older_than => INTERVAL '7 days') i;
```

---

## 📚 Ressources

- [Documentation TimescaleDB](https://docs.timescale.com/)
- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Hostinger VPS Guide](https://www.hostinger.com/tutorials/vps)

---

## 📞 Support

Pour toute question ou problème:
1. Vérifiez les logs: `docker compose logs -f`
2. Consultez la section Troubleshooting
3. Contactez l'équipe Ocean Sentinel

---

**✅ Déploiement terminé! Votre instance TimescaleDB est prête pour la production.**
