# 🔄 Guide des Backups - Ocean Sentinel TimescaleDB

## 🚀 Installation Rapide

### Sur le VPS, exécutez ces commandes :

```bash
# 1. Créer le répertoire de backups
mkdir -p ~/backups && chmod 700 ~/backups

# 2. Créer le script de backup
cat > ~/backup-oceansentinel.sh << 'EOSCRIPT'
#!/bin/bash
BACKUP_DIR=~/backups
CONTAINER="oceansentinel_timescaledb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/oceansentinelle_$TIMESTAMP.dump"
LOG_FILE="$BACKUP_DIR/backup.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "=== Début du backup ==="

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    log "ERREUR: Conteneur non actif"
    exit 1
fi

log "Création du backup..."
if docker exec $CONTAINER pg_dump -U oceansentinel -Fc oceansentinelle > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✓ Backup créé: $BACKUP_SIZE"
else
    log "✗ ERREUR backup"
    exit 1
fi

log "Nettoyage (>7 jours)..."
DELETED=$(find $BACKUP_DIR -name "oceansentinelle_*.dump" -mtime +7 -delete -print | wc -l)
log "✓ $DELETED backup(s) supprimé(s)"

TOTAL=$(ls -1 $BACKUP_DIR/oceansentinelle_*.dump 2>/dev/null | wc -l)
SIZE=$(du -sh $BACKUP_DIR | cut -f1)
log "Total: $TOTAL fichier(s), $SIZE"
log "=== Backup terminé ==="
EOSCRIPT

chmod +x ~/backup-oceansentinel.sh

# 3. Tester le script
~/backup-oceansentinel.sh

# 4. Configurer le cron (backup quotidien à 2h)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-oceansentinel.sh >> ~/backups/backup.log 2>&1") | crontab -

# 5. Vérifier le cron
crontab -l
```

---

## ✅ Vérification

```bash
# Voir les backups créés
ls -lh ~/backups/

# Voir le log
cat ~/backups/backup.log

# Vérifier le cron
crontab -l | grep backup
```

---

## 📋 Commandes Utiles

### Backup Manuel
```bash
~/backup-oceansentinel.sh
```

### Lister les Backups
```bash
ls -lh ~/backups/oceansentinelle_*.dump
```

### Taille Totale des Backups
```bash
du -sh ~/backups/
```

### Voir les Logs
```bash
# Dernières lignes
tail -20 ~/backups/backup.log

# Suivi en temps réel
tail -f ~/backups/backup.log
```

---

## 🔄 Restauration d'un Backup

### Restauration Complète
```bash
# 1. Arrêter les connexions actives (optionnel)
docker exec oceansentinel_timescaledb psql -U oceansentinel -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'oceansentinelle' AND pid <> pg_backend_pid();"

# 2. Restaurer le backup
docker exec -i oceansentinel_timescaledb pg_restore -U oceansentinel -d oceansentinelle --clean --if-exists \
  < ~/backups/oceansentinelle_20260416_020000.dump

# 3. Vérifier
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM barag.sensor_data;"
```

### Restauration dans une Nouvelle Base (Test)
```bash
# 1. Créer une base de test
docker exec oceansentinel_timescaledb psql -U oceansentinel -d postgres -c \
  "CREATE DATABASE oceansentinelle_test;"

# 2. Restaurer dans la base de test
docker exec -i oceansentinel_timescaledb pg_restore -U oceansentinel -d oceansentinelle_test \
  < ~/backups/oceansentinelle_20260416_020000.dump

# 3. Comparer
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle_test -c \
  "SELECT COUNT(*) FROM barag.sensor_data;"
```

---

## 📊 Monitoring des Backups

### Script de Vérification
```bash
cat > ~/check-backups.sh << 'EOSCRIPT'
#!/bin/bash
echo "🔍 Statut des Backups Ocean Sentinel"
echo "===================================="
echo ""

BACKUP_DIR=~/backups
LATEST=$(ls -t $BACKUP_DIR/oceansentinelle_*.dump 2>/dev/null | head -1)

if [ -z "$LATEST" ]; then
    echo "❌ Aucun backup trouvé"
    exit 1
fi

echo "📦 Dernier backup:"
echo "  Fichier: $(basename $LATEST)"
echo "  Taille:  $(du -h $LATEST | cut -f1)"
echo "  Date:    $(stat -c %y $LATEST | cut -d'.' -f1)"
echo ""

TOTAL=$(ls -1 $BACKUP_DIR/oceansentinelle_*.dump 2>/dev/null | wc -l)
SIZE=$(du -sh $BACKUP_DIR 2>/dev/null | cut -f1)
echo "📊 Statistiques:"
echo "  Total:   $TOTAL backup(s)"
echo "  Espace:  $SIZE"
echo ""

# Vérifier l'âge du dernier backup
AGE_HOURS=$(( ($(date +%s) - $(stat -c %Y $LATEST)) / 3600 ))
if [ $AGE_HOURS -gt 30 ]; then
    echo "⚠️  ATTENTION: Dernier backup vieux de $AGE_HOURS heures"
else
    echo "✅ Backups à jour (dernier: il y a $AGE_HOURS heures)"
fi
EOSCRIPT

chmod +x ~/check-backups.sh
```

### Exécuter la Vérification
```bash
~/check-backups.sh
```

---

## 🔐 Backup Distant (Optionnel)

### Transférer vers un Serveur Distant
```bash
# Via SCP
scp ~/backups/oceansentinelle_*.dump user@backup-server:/backups/

# Via rsync (plus efficace)
rsync -avz --progress ~/backups/ user@backup-server:/backups/oceansentinel/
```

### Backup vers un Bucket S3 (AWS/Hostinger Object Storage)
```bash
# Installer AWS CLI
sudo apt install awscli -y

# Configurer
aws configure

# Synchroniser
aws s3 sync ~/backups/ s3://oceansentinel-backups/timescaledb/
```

---

## 🔧 Modification de la Planification

### Changer l'Heure du Backup
```bash
# Éditer le cron
crontab -e

# Exemples de planification:
# Tous les jours à 2h:     0 2 * * *
# Tous les jours à 3h30:   30 3 * * *
# Toutes les 6 heures:     0 */6 * * *
# Deux fois par jour:      0 2,14 * * *
```

### Changer la Rétention
```bash
# Éditer le script
nano ~/backup-oceansentinel.sh

# Modifier la ligne:
find $BACKUP_DIR -name "oceansentinelle_*.dump" -mtime +7 -delete

# Exemples:
# 14 jours: -mtime +14
# 30 jours: -mtime +30
# 3 jours:  -mtime +3
```

---

## 📧 Notifications (Optionnel)

### Recevoir un Email en Cas d'Erreur
```bash
# Installer mailutils
sudo apt install mailutils -y

# Modifier le script pour ajouter:
if ! docker exec $CONTAINER pg_dump ... ; then
    echo "Backup failed" | mail -s "Ocean Sentinel Backup Error" votre@email.com
    exit 1
fi
```

---

## 🧪 Test de Restauration

### Test Mensuel Recommandé
```bash
# 1. Créer une base de test
docker exec oceansentinel_timescaledb psql -U oceansentinel -d postgres -c \
  "DROP DATABASE IF EXISTS test_restore; CREATE DATABASE test_restore;"

# 2. Restaurer le dernier backup
LATEST=$(ls -t ~/backups/oceansentinelle_*.dump | head -1)
docker exec -i oceansentinel_timescaledb pg_restore -U oceansentinel -d test_restore < $LATEST

# 3. Vérifier l'intégrité
docker exec oceansentinel_timescaledb psql -U oceansentinel -d test_restore -c \
  "SELECT COUNT(*) FROM barag.sensor_data;"

# 4. Nettoyer
docker exec oceansentinel_timescaledb psql -U oceansentinel -d postgres -c \
  "DROP DATABASE test_restore;"
```

---

## 📊 Résumé de la Configuration

| Paramètre | Valeur |
|-----------|--------|
| **Répertoire** | ~/backups |
| **Script** | ~/backup-oceansentinel.sh |
| **Planification** | Quotidien à 2h du matin |
| **Rétention** | 7 jours |
| **Format** | PostgreSQL Custom (compressed) |
| **Log** | ~/backups/backup.log |

---

**✅ Vos données TimescaleDB sont maintenant protégées par des backups automatiques !**
