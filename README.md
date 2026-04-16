# 🌊 Ocean Sentinel - Infrastructure TimescaleDB

Infrastructure de base de données TimescaleDB optimisée pour le projet **Ocean Sentinel**, station de surveillance océanographique BARAG.

## 📦 Contenu du Projet

```
oceansentinel/
├── docker-compose.yml              # Orchestration Docker
├── postgresql-custom.conf          # Configuration PostgreSQL optimisée
├── .env.example                    # Template de configuration
├── .gitignore                      # Fichiers à exclure de Git
├── DEPLOYMENT.md                   # Guide de déploiement complet
├── README.md                       # Ce fichier
├── init-scripts/
│   └── 01-init-timescaledb.sql    # Initialisation de la base
└── scripts/
    └── tune-timescaledb.sh        # Script de tuning automatique
```

## 🎯 Caractéristiques

### Infrastructure
- **Base de données:** TimescaleDB (PostgreSQL 16+)
- **Déploiement:** Docker Compose
- **Cible:** VPS Hostinger Ubuntu 22.04 (8 Go RAM / 4 vCPU)

### Fonctionnalités TimescaleDB
- ✅ **Hypertables** pour séries temporelles
- ✅ **Compression automatique** après 7 jours
- ✅ **Rétention** de 2 ans
- ✅ **Agrégats continus** (horaire + journalier)
- ✅ **Tuning automatique** des performances
- ✅ **Monitoring** intégré

### Sécurité
- 🔒 Port non-standard (6543)
- 🔒 Authentification SCRAM-SHA-256
- 🔒 Utilisateur non-root
- 🔒 Rôles avec principe de moindre privilège
- 🔒 Support SSL/TLS

## 🚀 Démarrage Rapide

### 1. Configuration
```bash
# Copier le template de configuration
cp .env.example .env

# Générer un mot de passe fort
openssl rand -base64 32

# Éditer .env et remplacer POSTGRES_PASSWORD
nano .env
```

### 2. Lancement
```bash
# Démarrer TimescaleDB
docker compose up -d

# Vérifier les logs
docker compose logs -f timescaledb
```

### 3. Tuning (Optionnel mais recommandé)
```bash
# Rendre le script exécutable
chmod +x scripts/tune-timescaledb.sh

# Exécuter le tuning
./scripts/tune-timescaledb.sh
```

### 4. Test de Connexion
```bash
# Depuis le serveur
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle

# Depuis l'extérieur (remplacez VOTRE_IP_VPS)
psql -h VOTRE_IP_VPS -p 6543 -U oceansentinel -d oceansentinelle
```

## 📊 Structure de la Base de Données

### Schémas
- **`barag`** - Données brutes de la station
- **`analytics`** - Agrégats et analyses
- **`metadata`** - Métadonnées des stations

### Tables Principales

#### `barag.sensor_data` (Hypertable)
Données brutes de capteurs avec partitionnement automatique par jour.

**Colonnes:**
- Météo: `temperature_air`, `humidity`, `pressure`, `wind_speed`, `wind_direction`, `precipitation`
- Océanographie: `temperature_water`, `salinity`, `ph`, `dissolved_oxygen`, `turbidity`
- Qualité: `quality_flag`, `data_source`

#### Vues Matérialisées
- **`analytics.hourly_aggregates`** - Agrégats horaires (rafraîchis toutes les 15 min)
- **`analytics.daily_aggregates`** - Agrégats journaliers (rafraîchis toutes les heures)

### Rôles Utilisateurs

| Rôle | Permissions | Usage |
|------|-------------|-------|
| `oceansentinel` | Superuser | Administration |
| `oceansentinel_writer` | INSERT, UPDATE | Ingesteur de données |
| `oceansentinel_readonly` | SELECT | Applications d'analyse |

⚠️ **Changez les mots de passe par défaut dans `init-scripts/01-init-timescaledb.sql`**

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

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guide de déploiement complet
- **[TimescaleDB Docs](https://docs.timescale.com/)** - Documentation officielle
- **[PostgreSQL 16 Docs](https://www.postgresql.org/docs/16/)** - Référence PostgreSQL

## 🛠️ Maintenance

### Backup Manuel
```bash
# Créer un backup
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel -Fc oceansentinelle \
    > backup_$(date +%Y%m%d).dump

# Restaurer un backup
docker exec -i oceansentinel_timescaledb pg_restore -U oceansentinel -d oceansentinelle \
    < backup_20260416.dump
```

### Mise à Jour de TimescaleDB
```bash
# Sauvegarder d'abord
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel -Fc oceansentinelle \
    > backup_avant_maj.dump

# Mettre à jour l'image
docker compose pull
docker compose up -d

# Vérifier la version
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT extname, extversion FROM pg_extension WHERE extname = 'timescaledb';"
```

## 🐛 Troubleshooting

### Le conteneur ne démarre pas
```bash
# Vérifier les logs
docker compose logs timescaledb

# Vérifier les permissions
sudo chown -R 999:999 /opt/oceansentinel/data
```

### Impossible de se connecter
```bash
# Vérifier que le port est ouvert
sudo netstat -tlnp | grep 6543

# Tester localement
telnet localhost 6543
```

### Performances dégradées
```bash
# Relancer le tuning
./scripts/tune-timescaledb.sh

# Vérifier la compression
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT * FROM metadata.chunk_status WHERE is_compressed = false;"
```

## 📞 Support

Pour toute question:
1. Consultez `DEPLOYMENT.md`
2. Vérifiez les logs: `docker compose logs -f`
3. Consultez la documentation TimescaleDB

## 📄 Licence

Projet Ocean Sentinel - 2026

---

**Développé avec ❤️ pour la surveillance océanographique**
