#!/bin/bash
# ============================================================================
# Ocean Sentinel Ops - Script de Consultation des Logs VPS
# ============================================================================
# Description: Se connecte au VPS via SSH pour récupérer les logs des conteneurs
# Usage: ./check_logs.sh [service]
# Services: ingestion, timescaledb, backup, all
# ============================================================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration VPS
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Charger les variables d'environnement
if [ -f "$PROJECT_ROOT/.env.vps" ]; then
    source "$PROJECT_ROOT/.env.vps"
else
    echo -e "${RED}❌ Fichier .env.vps non trouvé${NC}"
    echo "Créez le fichier .env.vps à la racine du projet avec:"
    echo "VPS_HOST=76.13.43.3"
    echo "VPS_USER=root"
    echo "VPS_SSH_PORT=22"
    exit 1
fi

# Valeurs par défaut
VPS_HOST=${VPS_HOST:-76.13.43.3}
VPS_USER=${VPS_USER:-root}
VPS_SSH_PORT=${VPS_SSH_PORT:-22}
SERVICE=${1:-ingestion}

# Fonction d'affichage
print_header() {
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Vérifier la connexion SSH
check_ssh_connection() {
    print_info "Test de connexion SSH vers ${VPS_HOST}..."
    if ssh -p ${VPS_SSH_PORT} -o ConnectTimeout=5 -o BatchMode=yes ${VPS_USER}@${VPS_HOST} "echo 'SSH OK'" &>/dev/null; then
        print_success "Connexion SSH établie"
        return 0
    else
        print_error "Impossible de se connecter au VPS"
        print_info "Vérifiez vos credentials SSH ou utilisez: ssh ${VPS_USER}@${VPS_HOST}"
        return 1
    fi
}

# Récupérer les logs d'ingestion
get_ingestion_logs() {
    print_header "LOGS DU SERVICE D'INGESTION (50 dernières lignes)"
    
    ssh -p ${VPS_SSH_PORT} ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /opt/oceansentinel
docker compose -f docker-compose-vps.yml logs --tail=50 ingestion 2>/dev/null | tail -50
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "Logs récupérés avec succès"
    else
        print_error "Erreur lors de la récupération des logs"
    fi
}

# Récupérer les logs TimescaleDB
get_timescaledb_logs() {
    print_header "LOGS TIMESCALEDB (50 dernières lignes)"
    
    ssh -p ${VPS_SSH_PORT} ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /opt/oceansentinel
docker compose -f docker-compose-vps.yml logs --tail=50 timescaledb 2>/dev/null | tail -50
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "Logs récupérés avec succès"
    else
        print_error "Erreur lors de la récupération des logs"
    fi
}

# Récupérer les logs de backup
get_backup_logs() {
    print_header "LOGS DE BACKUP (50 dernières lignes)"
    
    ssh -p ${VPS_SSH_PORT} ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
if [ -f /var/log/oceansentinel_backup.log ]; then
    tail -50 /var/log/oceansentinel_backup.log
else
    echo "Aucun log de backup trouvé"
fi
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "Logs récupérés avec succès"
    else
        print_warning "Aucun log de backup disponible"
    fi
}

# Statut de tous les conteneurs
get_all_status() {
    print_header "STATUT DE TOUS LES CONTENEURS"
    
    ssh -p ${VPS_SSH_PORT} ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
cd /opt/oceansentinel
echo "=== CONTENEURS ==="
docker compose -f docker-compose-vps.yml ps 2>/dev/null

echo ""
echo "=== UTILISATION RESSOURCES ==="
docker stats --no-stream 2>/dev/null

echo ""
echo "=== SYSTÈME ==="
free -h | grep -E "Mem|Swap"
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "Statut récupéré avec succès"
    else
        print_error "Erreur lors de la récupération du statut"
    fi
}

# Main
main() {
    print_header "OCEAN SENTINEL OPS - CONSULTATION DES LOGS"
    echo ""
    print_info "VPS: ${VPS_HOST}"
    print_info "Service: ${SERVICE}"
    echo ""
    
    # Vérifier la connexion
    if ! check_ssh_connection; then
        exit 1
    fi
    
    echo ""
    
    # Récupérer les logs selon le service demandé
    case ${SERVICE} in
        ingestion)
            get_ingestion_logs
            ;;
        timescaledb|db)
            get_timescaledb_logs
            ;;
        backup)
            get_backup_logs
            ;;
        all|status)
            get_all_status
            ;;
        *)
            print_error "Service inconnu: ${SERVICE}"
            echo ""
            echo "Services disponibles:"
            echo "  - ingestion    : Logs du service d'ingestion"
            echo "  - timescaledb  : Logs de la base de données"
            echo "  - backup       : Logs des backups"
            echo "  - all          : Statut de tous les conteneurs"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Opération terminée"
}

# Exécution
main
