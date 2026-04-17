# 🎉 Déploiement TimescaleDB Réussi !

## ✅ Statut du Déploiement

**Date:** 16 avril 2026  
**Serveur:** srv1341436 (VPS Hostinger)  
**Statut:** ✅ OPÉRATIONNEL

---

## 📊 Configuration Actuelle

### Infrastructure
- **OS:** Ubuntu 24.04 (Noble)
- **Docker:** Installé et opérationnel
- **TimescaleDB:** PostgreSQL 16.13 + TimescaleDB extension
- **Port:** 6543 (externe) → 5432 (interne)

### Base de Données
- **Nom:** oceansentinelle
- **Utilisateur:** oceansentinel
- **Taille actuelle:** 9.4 MB
- **Localisation:** /opt/oceansentinel/data

### Fonctionnalités Actives
✅ Hypertable `barag.sensor_data` (partitionnement par jour)  
✅ Compression automatique après 7 jours  
✅ Rétention de 2 ans  
✅ Agrégats continus horaires  
✅ Background workers TimescaleDB actifs  

---

## 🔐 Informations de Connexion

### Depuis le VPS (local)
```bash
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle
```

### Depuis l'extérieur
```bash
# Récupérer l'IP du VPS
curl ifconfig.me

# Récupérer le mot de passe
cat ~/oceansentinel/.env | grep POSTGRES_PASSWORD

# Connexion
psql -h VOTRE_IP_VPS -p 6543 -U oceansentinel -d oceansentinelle
```

**Paramètres de connexion pour clients graphiques (DBeaver, pgAdmin) :**
- **Host:** [IP du VPS]
- **Port:** 6543
- **Database:** oceansentinelle
- **Username:** oceansentinel
- **Password:** [voir ~/oceansentinel/.env]
- **SSL Mode:** prefer (ou disable pour tests)

---

## 📝 Tests de Validation Effectués

### 1. Extension TimescaleDB
```sql
SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';
-- Résultat: Version installée et active
```

### 2. Hypertables
```sql
SELECT * FROM timescaledb_information.hypertables;
-- Résultat: barag.sensor_data configurée
```

### 3. Politique de Compression
```sql
SELECT * FROM timescaledb_information.jobs WHERE proc_name = 'policy_compression';
-- Résultat: Job 1000 actif, compression après 7 jours
```

### 4. Insertion de Données Test
```sql
INSERT INTO barag.sensor_data (time, station_id, temperature_air, temperature_water, salinity, ph)
VALUES (NOW(), 'BARAG', 22.5, 18.3, 35.2, 8.1);
-- Résultat: 2 lignes insérées avec succès
```

### 5. Lecture des Données
```sql
SELECT * FROM barag.sensor_data ORDER BY time DESC LIMIT 5;
-- Résultat: Données récupérées correctement
```

---

## 🔧 Commandes de Maintenance

### Gestion du Conteneur
```bash
# Voir les logs
docker compose logs -f timescaledb

# Redémarrer
docker compose restart timescaledb

# Arrêter
docker compose down

# Démarrer
docker compose up -d

# Voir le statut
docker ps | grep oceansentinel
```

### Monitoring
```bash
# Taille de la base
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT pg_size_pretty(pg_database_size('oceansentinelle'));"

# Nombre de chunks
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM timescaledb_information.chunks;"

# Chunks compressés
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM timescaledb_information.chunks WHERE is_compressed = true;"

# Statistiques d'ingestion
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*), MIN(time), MAX(time) FROM barag.sensor_data;"
```

### Backup
```bash
# Créer un backup
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel -Fc oceansentinelle \
  > ~/backups/oceansentinelle_$(date +%Y%m%d_%H%M%S).dump

# Restaurer un backup
docker exec -i oceansentinel_timescaledb pg_restore -U oceansentinel -d oceansentinelle \
  < ~/backups/oceansentinelle_20260416.dump
```

---

## 📈 Prochaines Étapes

### 1. Configuration de l'Ingesteur de Données
Créer un service qui envoie les données de la station BARAG vers TimescaleDB.

**Exemple de connexion Python :**
```python
import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host="VOTRE_IP_VPS",
    port=6543,
    database="oceansentinelle",
    user="oceansentinel",
    password="VOTRE_MOT_DE_PASSE"
)

cur = conn.cursor()
cur.execute("""
    INSERT INTO barag.sensor_data 
    (time, station_id, temperature_air, temperature_water, salinity, ph)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (datetime.now(), 'BARAG', 22.5, 18.3, 35.2, 8.1))

conn.commit()
cur.close()
conn.close()
```

### 2. Configuration des Backups Automatiques
```bash
# Créer le script de backup
mkdir -p ~/backups
cat > ~/backup-oceansentinel.sh << 'EOSCRIPT'
#!/bin/bash
BACKUP_DIR=~/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel -Fc oceansentinelle \
  > $BACKUP_DIR/oceansentinelle_$TIMESTAMP.dump
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete
EOSCRIPT

chmod +x ~/backup-oceansentinel.sh

# Ajouter au cron (backup quotidien à 2h)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-oceansentinel.sh") | crontab -
```

### 3. Monitoring avec Grafana (Optionnel)
Installer Grafana pour visualiser les données en temps réel.

### 4. Configuration SSL/TLS (Production)
Activer SSL pour sécuriser les connexions externes.

### 5. Créer les Rôles Supplémentaires
```sql
-- Rôle lecture seule
CREATE ROLE oceansentinel_readonly WITH LOGIN PASSWORD 'mot_de_passe_fort';
GRANT CONNECT ON DATABASE oceansentinelle TO oceansentinel_readonly;
GRANT USAGE ON SCHEMA barag, analytics, metadata TO oceansentinel_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA barag, analytics, metadata TO oceansentinel_readonly;

-- Rôle écriture (pour l'ingesteur)
CREATE ROLE oceansentinel_writer WITH LOGIN PASSWORD 'mot_de_passe_fort';
GRANT CONNECT ON DATABASE oceansentinelle TO oceansentinel_writer;
GRANT USAGE ON SCHEMA barag, metadata TO oceansentinel_writer;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA barag, metadata TO oceansentinel_writer;
```

---

## 🔒 Sécurité

### Checklist de Sécurité
- [x] Port non-standard (6543)
- [x] Authentification SCRAM-SHA-256
- [x] Pare-feu UFW activé
- [ ] Pare-feu Hostinger configuré (à faire via le panel)
- [ ] SSL/TLS activé (recommandé pour production)
- [ ] Fail2Ban installé (optionnel)
- [ ] Backups automatiques configurés
- [ ] Rôles avec privilèges minimaux créés

### Configuration Pare-feu Hostinger
1. Connectez-vous au panel Hostinger
2. VPS → Pare-feu
3. Ajoutez une règle :
   - Port: **6543**
   - Protocole: **TCP**
   - Source: **0.0.0.0/0** (ou restreindre à vos IPs)
   - Action: **Autoriser**

---

## 📚 Ressources

- **Documentation TimescaleDB:** https://docs.timescale.com/
- **PostgreSQL 16 Docs:** https://www.postgresql.org/docs/16/
- **Docker Compose Reference:** https://docs.docker.com/compose/

---

## 🆘 Support et Troubleshooting

### Problème: Conteneur ne démarre pas
```bash
docker compose logs timescaledb
sudo chown -R 999:999 /opt/oceansentinel/data
```

### Problème: Connexion refusée depuis l'extérieur
```bash
# Vérifier que le port est ouvert
sudo ufw status
sudo netstat -tlnp | grep 6543

# Tester localement
telnet localhost 6543
```

### Problème: Performances dégradées
```bash
# Vérifier les chunks non compressés
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM timescaledb_information.chunks WHERE is_compressed = false;"

# Forcer la compression manuelle
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT compress_chunk(i) FROM show_chunks('barag.sensor_data', older_than => INTERVAL '7 days') i;"
```

---

## 📞 Contact

Pour toute question ou problème, consultez :
1. Les logs: `docker compose logs -f`
2. Ce document
3. La documentation officielle TimescaleDB

---

**🌊 Ocean Sentinel - Infrastructure TimescaleDB Opérationnelle**  
**Déployé avec succès le 16 avril 2026**
