#!/bin/bash

# =====================================================
# Configuration des Backups Automatiques
# Ocean Sentinel - TimescaleDB
# =====================================================

set -e

echo "🔄 Configuration des backups automatiques pour Ocean Sentinel"
echo "=============================================================="
echo ""

# Créer le répertoire de backups
echo "[1/4] Création du répertoire de backups..."
mkdir -p ~/backups
chmod 700 ~/backups

# Créer le script de backup
echo "[2/4] Création du script de backup..."
cat > ~/backup-oceansentinel.sh << 'EOSCRIPT'
#!/bin/bash

# Configuration
BACKUP_DIR=~/backups
CONTAINER="oceansentinel_timescaledb"
DB_USER="oceansentinel"
DB_NAME="oceansentinelle"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/oceansentinelle_$TIMESTAMP.dump"
LOG_FILE="$BACKUP_DIR/backup.log"

# Fonction de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Début du backup ==="

# Vérifier que le conteneur est actif
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    log "ERREUR: Le conteneur $CONTAINER n'est pas actif"
    exit 1
fi

# Créer le backup
log "Création du backup: $BACKUP_FILE"
if docker exec $CONTAINER pg_dump -U $DB_USER -Fc $DB_NAME > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✓ Backup créé avec succès ($BACKUP_SIZE)"
else
    log "✗ ERREUR lors de la création du backup"
    exit 1
fi

# Nettoyer les anciens backups (garder 7 jours)
log "Nettoyage des backups de plus de 7 jours..."
DELETED=$(find $BACKUP_DIR -name "oceansentinelle_*.dump" -mtime +7 -delete -print | wc -l)
log "✓ $DELETED ancien(s) backup(s) supprimé(s)"

# Statistiques
TOTAL_BACKUPS=$(ls -1 $BACKUP_DIR/oceansentinelle_*.dump 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
log "Backups actuels: $TOTAL_BACKUPS fichier(s), taille totale: $TOTAL_SIZE"

log "=== Backup terminé ==="
echo ""
EOSCRIPT

chmod +x ~/backup-oceansentinel.sh

# Tester le script
echo "[3/4] Test du script de backup..."
~/backup-oceansentinel.sh

# Configurer le cron
echo "[4/4] Configuration du cron (backup quotidien à 2h du matin)..."

# Sauvegarder le crontab actuel
crontab -l > /tmp/current_cron 2>/dev/null || echo "" > /tmp/current_cron

# Vérifier si la tâche existe déjà
if grep -q "backup-oceansentinel.sh" /tmp/current_cron; then
    echo "⚠️  La tâche cron existe déjà, non modifiée"
else
    # Ajouter la nouvelle tâche
    echo "0 2 * * * ~/backup-oceansentinel.sh >> ~/backups/backup.log 2>&1" >> /tmp/current_cron
    crontab /tmp/current_cron
    echo "✓ Tâche cron ajoutée"
fi

rm /tmp/current_cron

echo ""
echo "✅ Configuration des backups terminée !"
echo ""
echo "📊 Résumé:"
echo "  • Répertoire: ~/backups"
echo "  • Script: ~/backup-oceansentinel.sh"
echo "  • Planification: Tous les jours à 2h du matin"
echo "  • Rétention: 7 jours"
echo "  • Log: ~/backups/backup.log"
echo ""
echo "🔧 Commandes utiles:"
echo "  • Backup manuel:     ~/backup-oceansentinel.sh"
echo "  • Voir les backups:  ls -lh ~/backups/"
echo "  • Voir le log:       tail -f ~/backups/backup.log"
echo "  • Voir le cron:      crontab -l"
echo ""
