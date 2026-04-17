# 🚀 Déploiement Rapide Ocean Sentinel V3.0

## VPS Vérifié

✅ **IP** : `76.13.43.3`  
✅ **Port SSH** : Ouvert  
✅ **Status** : Prêt pour déploiement

---

## Déploiement Automatique (1 commande)

```powershell
.\deploy_simple.ps1
```

**Ce que fait le script** :
1. ✅ Installe Docker + Docker Compose
2. ✅ Clone le repository GitHub
3. ✅ Génère mots de passe sécurisés
4. ✅ Configure l'environnement
5. ✅ Déploie l'application
6. ✅ Valide l'API

**Durée** : 3-5 minutes  
**Interaction** : Mot de passe root VPS requis

---

## Après Déploiement

### Endpoints

- **API Health** : http://76.13.43.3:8000/api/v1/health
- **Pipeline Status** : http://76.13.43.3:8000/api/v1/pipeline/status
- **API Docs** : http://76.13.43.3:8000/docs

### Test API

```powershell
# Health check
Invoke-RestMethod -Uri "http://76.13.43.3:8000/api/v1/health"

# Pipeline status
Invoke-RestMethod -Uri "http://76.13.43.3:8000/api/v1/pipeline/status" | ConvertTo-Json
```

### Récupérer Credentials

```bash
ssh root@76.13.43.3 'cat /root/.oceansentinel_credentials'
```

---

## Commandes Utiles

### Connexion SSH

```bash
ssh root@76.13.43.3
```

### Logs en Temps Réel

```bash
# Tous les services
cd /opt/oceansentinel
docker compose -f docker-compose-full.yml logs -f

# Orchestrateur uniquement
docker compose -f docker-compose-full.yml logs -f orchestrator

# API uniquement
docker compose -f docker-compose-full.yml logs -f api
```

### Vérifier Données

```bash
# Ingestions récentes (dernière heure)
docker exec os_postgres psql -U admin -d oceansentinel -c "
SELECT source_name, COUNT(*) 
FROM raw_ingestion_log 
WHERE fetched_at > NOW() - INTERVAL '1 hour' 
GROUP BY source_name;
"

# Total mesures validées
docker exec os_postgres psql -U admin -d oceansentinel -c "
SELECT COUNT(*) FROM validated_measurements;
"

# Dernières mesures
docker exec os_postgres psql -U admin -d oceansentinel -c "
SELECT 
    timestamp_utc,
    station_id,
    temperature_water,
    salinity
FROM validated_measurements
ORDER BY timestamp_utc DESC
LIMIT 10;
"
```

### Status Services

```bash
# Status conteneurs
docker compose -f docker-compose-full.yml ps

# Stats ressources
docker stats

# Espace disque
df -h
```

---

## Sources Activées

Par défaut, **2 sources** sont activées :

1. ✅ **ERDDAP COAST-HF** (Arcachon, Ferret)
2. ✅ **Hub'Eau** (Qualité eau)

### Activer Sources Supplémentaires

```bash
# Éditer .env
vim /opt/oceansentinel/.env

# Activer source
ENABLE_ERDDAP_SOMLIT=true

# Redémarrer orchestrateur
docker compose -f docker-compose-full.yml restart orchestrator
```

---

## Troubleshooting

### API pas accessible

```bash
# Vérifier logs API
docker compose -f docker-compose-full.yml logs api

# Redémarrer API
docker compose -f docker-compose-full.yml restart api
```

### Pas de données ingérées

```bash
# Vérifier logs orchestrateur
docker compose -f docker-compose-full.yml logs orchestrator

# Vérifier jobs planifiés
docker compose -f docker-compose-full.yml logs orchestrator | grep "job.scheduled"

# Forcer exécution manuelle
docker exec os_orchestrator python -c "
from workers.orchestrator import run_job
run_job('erddap_coast_hf')
"
```

### Redémarrer tout

```bash
cd /opt/oceansentinel
docker compose -f docker-compose-full.yml restart
```

---

## Monitoring

### Vérification Santé (toutes les 5 min)

```bash
# Créer script monitoring
cat > /opt/oceansentinel/monitor.sh <<'EOF'
#!/bin/bash
echo "=== Ocean Sentinel Health Check ==="
echo ""
echo "API Health:"
curl -s http://localhost:8000/api/v1/health | jq -r '.status'
echo ""
echo "Pipeline Status:"
curl -s http://localhost:8000/api/v1/pipeline/status | jq
echo ""
echo "Containers:"
docker compose -f /opt/oceansentinel/docker-compose-full.yml ps
EOF

chmod +x /opt/oceansentinel/monitor.sh

# Ajouter cron
crontab -e
# Ajouter: */5 * * * * /opt/oceansentinel/monitor.sh >> /var/log/oceansentinel.log 2>&1
```

### Backup Quotidien

```bash
# Créer script backup
cat > /opt/oceansentinel/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/oceansentinel/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
docker exec os_postgres pg_dump -U admin oceansentinel | gzip > $BACKUP_DIR/db_$DATE.sql.gz
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

chmod +x /opt/oceansentinel/backup.sh

# Ajouter cron (3h du matin)
crontab -e
# Ajouter: 0 3 * * * /opt/oceansentinel/backup.sh
```

---

## Prochaines Étapes

1. ✅ Déployer avec `.\deploy_simple.ps1`
2. ⏳ Attendre 1h pour voir premières ingestions
3. 📊 Vérifier données dans PostgreSQL
4. 🔧 Activer sources supplémentaires si besoin
5. 🎨 Brancher frontend React sur API

---

**Ocean Sentinel V3.0 - Backend Production Ready !** 🌊🚀
