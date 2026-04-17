# 🌊 Ocean Sentinel - Guide de Référence Rapide

---

## 🔐 INFORMATIONS DE CONNEXION

### Récupérer les Identifiants (sur le VPS)

```bash
# Mot de passe
cat ~/oceansentinel/.env | grep POSTGRES_PASSWORD

# IP du serveur
curl ifconfig.me
```

### Connexion depuis le VPS (Local)

```bash
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle
```

### Connexion depuis l'Extérieur

**Ligne de commande (psql) :**
```bash
psql -h VOTRE_IP_VPS -p 6543 -U oceansentinel -d oceansentinelle
```

**Clients Graphiques (DBeaver, pgAdmin, TablePlus) :**
```
Host:     [IP du VPS - obtenue avec: curl ifconfig.me]
Port:     6543
Database: oceansentinelle
Username: oceansentinel
Password: [voir: cat ~/oceansentinel/.env | grep POSTGRES_PASSWORD]
SSL Mode: prefer (ou disable pour tests)
```

**Chaîne de connexion PostgreSQL :**
```
postgresql://oceansentinel:VOTRE_MOT_DE_PASSE@VOTRE_IP_VPS:6543/oceansentinelle
```

---

## 📊 COMMANDES UTILES

### Monitoring de la Base de Données

```bash
# Taille de la base de données
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT pg_size_pretty(pg_database_size('oceansentinelle'));"

# Nombre total d'enregistrements
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM barag.sensor_data;"

# Dernières données insérées
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT * FROM barag.sensor_data ORDER BY time DESC LIMIT 10;"

# Statistiques par station
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT station_id, COUNT(*), MIN(time), MAX(time) FROM barag.sensor_data GROUP BY station_id;"

# Nombre de chunks
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM timescaledb_information.chunks;"

# Chunks compressés vs non compressés
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT is_compressed, COUNT(*) FROM timescaledb_information.chunks GROUP BY is_compressed;"

# Version de TimescaleDB
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';"

# Connexions actives
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'oceansentinelle';"
```

### Monitoring du Conteneur Docker

```bash
# Statut du conteneur
docker ps | grep oceansentinel

# Logs en temps réel
docker compose logs -f timescaledb

# Logs des 100 dernières lignes
docker compose logs --tail=100 timescaledb

# Utilisation des ressources (CPU, RAM)
docker stats oceansentinel_timescaledb --no-stream

# Inspecter le conteneur
docker inspect oceansentinel_timescaledb

# Vérifier la santé du conteneur
docker exec oceansentinel_timescaledb pg_isready -U oceansentinel -d oceansentinelle
```

### Insertion de Données Test

```bash
# Insérer une donnée test
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
INSERT INTO barag.sensor_data (time, station_id, temperature_air, temperature_water, salinity, ph)
VALUES (NOW(), 'BARAG', 22.5, 18.3, 35.2, 8.1);
"

# Insérer plusieurs données
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
INSERT INTO barag.sensor_data (time, station_id, temperature_air, temperature_water, salinity, ph, wind_speed)
VALUES 
  (NOW(), 'BARAG', 22.5, 18.3, 35.2, 8.1, 12.5),
  (NOW() - INTERVAL '1 hour', 'BARAG', 22.3, 18.2, 35.1, 8.0, 11.8),
  (NOW() - INTERVAL '2 hours', 'BARAG', 22.1, 18.0, 35.0, 7.9, 10.2);
"
```

### Requêtes d'Analyse

```bash
# Moyenne des températures sur 24h
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT 
  AVG(temperature_air) AS avg_temp_air,
  AVG(temperature_water) AS avg_temp_water,
  COUNT(*) AS samples
FROM barag.sensor_data 
WHERE time > NOW() - INTERVAL '24 hours';
"

# Données agrégées par heure (dernières 24h)
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT * FROM analytics.hourly_aggregates 
WHERE bucket > NOW() - INTERVAL '24 hours' 
ORDER BY bucket DESC;
"

# Min/Max températures par jour
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT 
  DATE(time) AS date,
  MIN(temperature_air) AS min_temp,
  MAX(temperature_air) AS max_temp,
  AVG(temperature_air) AS avg_temp
FROM barag.sensor_data 
GROUP BY DATE(time) 
ORDER BY date DESC 
LIMIT 7;
"
```

---

## 🔧 GESTION DU SERVICE

### Démarrage et Arrêt

```bash
# Aller dans le répertoire du projet
cd ~/oceansentinel

# Démarrer le service
docker compose up -d

# Arrêter le service
docker compose down

# Redémarrer le service
docker compose restart timescaledb

# Arrêter puis redémarrer (avec rechargement de la config)
docker compose down && docker compose up -d

# Voir le statut
docker compose ps
```

### Mise à Jour de l'Image

```bash
cd ~/oceansentinel

# Télécharger la dernière image
docker compose pull

# Redémarrer avec la nouvelle image
docker compose down
docker compose up -d

# Vérifier la version
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT version();"
```

### Backup et Restauration

```bash
# Créer un backup complet
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel -Fc oceansentinelle \
  > ~/backups/oceansentinelle_$(date +%Y%m%d_%H%M%S).dump

# Créer un backup SQL (texte)
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel oceansentinelle \
  > ~/backups/oceansentinelle_$(date +%Y%m%d_%H%M%S).sql

# Lister les backups
ls -lh ~/backups/

# Restaurer un backup (format custom)
docker exec -i oceansentinel_timescaledb pg_restore -U oceansentinel -d oceansentinelle \
  < ~/backups/oceansentinelle_20260416.dump

# Restaurer un backup SQL
docker exec -i oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle \
  < ~/backups/oceansentinelle_20260416.sql
```

### Nettoyage et Maintenance

```bash
# Vacuum de la base (nettoyage)
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "VACUUM;"

# Vacuum complet (plus long)
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "VACUUM FULL;"

# Analyser les tables (optimisation du planificateur)
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "ANALYZE;"

# Reindex la base
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "REINDEX DATABASE oceansentinelle;"

# Nettoyer les images Docker inutilisées
docker system prune -a

# Voir l'espace disque utilisé
df -h /opt/oceansentinel/data
du -sh /opt/oceansentinel/data
```

### Logs et Debugging

```bash
# Logs PostgreSQL internes
docker exec oceansentinel_timescaledb tail -f /var/lib/postgresql/data/pg_log/postgresql-*.log

# Logs Docker du conteneur
docker logs oceansentinel_timescaledb --tail=100 -f

# Entrer dans le conteneur (shell)
docker exec -it oceansentinel_timescaledb bash

# Vérifier les processus dans le conteneur
docker exec oceansentinel_timescaledb ps aux

# Vérifier la configuration PostgreSQL
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SHOW ALL;" | grep -E "(shared_buffers|work_mem|max_connections)"
```

### Redémarrage Automatique

```bash
# Activer le redémarrage automatique au boot du serveur
sudo systemctl enable docker

# Vérifier que Docker démarre au boot
sudo systemctl is-enabled docker

# Le conteneur redémarrera automatiquement grâce à "restart: unless-stopped" dans docker-compose.yml
```

### Modification de la Configuration

```bash
# Éditer le fichier .env
cd ~/oceansentinel
nano .env

# Éditer docker-compose.yml
nano docker-compose.yml

# Appliquer les changements
docker compose down
docker compose up -d
```

---

## 🚨 DÉPANNAGE RAPIDE

### Le conteneur ne démarre pas
```bash
# Vérifier les logs
docker compose logs timescaledb

# Vérifier les permissions
sudo chown -R 999:999 /opt/oceansentinel/data
sudo chmod 700 /opt/oceansentinel/data

# Recréer le conteneur
docker compose down
docker compose up -d
```

### Impossible de se connecter depuis l'extérieur
```bash
# Vérifier que le port est ouvert
sudo ufw status | grep 6543
sudo netstat -tlnp | grep 6543

# Tester localement
telnet localhost 6543

# Vérifier le pare-feu Hostinger (via panel web)
```

### Base de données lente
```bash
# Vérifier les chunks non compressés
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM timescaledb_information.chunks WHERE is_compressed = false;"

# Forcer la compression manuelle
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT compress_chunk(i) FROM show_chunks('barag.sensor_data', older_than => INTERVAL '7 days') i;"

# Analyser les requêtes lentes
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT query, calls, total_exec_time, mean_exec_time 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC 
   LIMIT 10;"
```

---

## 📞 INFORMATIONS SYSTÈME

```bash
# Version du système
cat /etc/os-release

# Version Docker
docker --version
docker compose version

# Espace disque
df -h

# Mémoire disponible
free -h

# Uptime du serveur
uptime

# Uptime du conteneur
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

**🌊 Ocean Sentinel - TimescaleDB**  
**Guide de Référence Rapide - Avril 2026**
