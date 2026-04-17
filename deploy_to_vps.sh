#!/bin/bash
# ============================================================================
# Ocean Sentinel V3.0 - Script de Déploiement VPS
# ============================================================================
# Usage: ./deploy_to_vps.sh [--vps-ip IP] [--ssh-port PORT]
# ============================================================================

set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration par défaut
VPS_IP="${VPS_IP:-76.13.43.3}"
SSH_PORT="${SSH_PORT:-22}"
SSH_USER="${SSH_USER:-root}"
REMOTE_DIR="/opt/oceansentinel"

print_header() {
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================================${NC}"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
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

# Vérifier les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --vps-ip)
            VPS_IP="$2"
            shift 2
            ;;
        --ssh-port)
            SSH_PORT="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--vps-ip IP] [--ssh-port PORT]"
            exit 1
            ;;
    esac
done

print_header "OCEAN SENTINEL V3.0 - DÉPLOIEMENT VPS"
echo ""
print_step "Configuration:"
echo "  VPS IP: $VPS_IP"
echo "  SSH Port: $SSH_PORT"
echo "  SSH User: $SSH_USER"
echo "  Remote Dir: $REMOTE_DIR"
echo ""

# Étape 1: Vérifier la connexion SSH
print_step "Vérification de la connexion SSH..."
if ssh -p $SSH_PORT -o ConnectTimeout=5 $SSH_USER@$VPS_IP "echo 'SSH OK'" &>/dev/null; then
    print_success "Connexion SSH établie"
else
    print_error "Impossible de se connecter au VPS"
    exit 1
fi

# Étape 2: Transférer les fichiers
print_step "Transfert des fichiers vers le VPS..."

echo "  - Transfert du dossier api/"
scp -P $SSH_PORT -r api/ $SSH_USER@$VPS_IP:$REMOTE_DIR/

echo "  - Transfert du dossier grafana/"
scp -P $SSH_PORT -r grafana/ $SSH_USER@$VPS_IP:$REMOTE_DIR/

echo "  - Transfert de Dockerfile.api"
scp -P $SSH_PORT Dockerfile.api $SSH_USER@$VPS_IP:$REMOTE_DIR/

echo "  - Transfert de docker-compose-vps-full.yml"
scp -P $SSH_PORT docker-compose-vps-full.yml $SSH_USER@$VPS_IP:$REMOTE_DIR/

print_success "Fichiers transférés"

# Étape 3: Déploiement sur le VPS
print_step "Déploiement sur le VPS..."

ssh -p $SSH_PORT $SSH_USER@$VPS_IP << 'ENDSSH'
cd /opt/oceansentinel

echo "Arrêt de l'ancienne stack..."
docker compose -f docker-compose-vps.yml down || true

echo "Sauvegarde de l'ancien fichier..."
if [ -f docker-compose-vps.yml ]; then
    cp docker-compose-vps.yml docker-compose-vps.yml.backup-$(date +%Y%m%d-%H%M%S)
fi

echo "Utilisation de la nouvelle configuration..."
cp docker-compose-vps-full.yml docker-compose-vps.yml

echo "Build de l'image API..."
docker compose -f docker-compose-vps.yml build api

echo "Démarrage de la nouvelle stack..."
docker compose -f docker-compose-vps.yml up -d

echo "Attente du démarrage (30s)..."
sleep 30

echo "Vérification du statut..."
docker compose -f docker-compose-vps.yml ps
ENDSSH

print_success "Déploiement terminé"

# Étape 4: Configuration UFW
print_step "Configuration du pare-feu UFW..."

ssh -p $SSH_PORT $SSH_USER@$VPS_IP << 'ENDSSH'
echo "Ouverture du port 8000 (API)..."
sudo ufw allow 8000/tcp comment 'Ocean Sentinel API' || true

echo "Ouverture du port 3000 (Grafana)..."
sudo ufw allow 3000/tcp comment 'Ocean Sentinel Grafana' || true

echo "Rechargement UFW..."
sudo ufw reload || true

echo "Vérification des ports..."
sudo ufw status | grep -E '8000|3000' || echo "Ports non trouvés dans UFW"
ENDSSH

print_success "Pare-feu configuré"

# Étape 5: Tests de connectivité
print_step "Tests de connectivité..."

echo "  - Test API Health..."
if curl -s -f http://$VPS_IP:8000/health > /dev/null; then
    print_success "API accessible"
else
    print_warning "API non accessible (peut nécessiter quelques secondes)"
fi

echo "  - Test Grafana..."
if curl -s -I http://$VPS_IP:3000 | grep -q "HTTP"; then
    print_success "Grafana accessible"
else
    print_warning "Grafana non accessible (peut nécessiter quelques secondes)"
fi

# Étape 6: Affichage des logs
print_step "Logs des services (10 dernières lignes)..."

ssh -p $SSH_PORT $SSH_USER@$VPS_IP << 'ENDSSH'
cd /opt/oceansentinel
echo "=== API ==="
docker compose -f docker-compose-vps.yml logs --tail=10 api

echo ""
echo "=== Grafana ==="
docker compose -f docker-compose-vps.yml logs --tail=10 grafana
ENDSSH

# Résumé final
echo ""
print_header "DÉPLOIEMENT COMPLÉTÉ !"
echo ""
print_success "Services déployés:"
echo "  - TimescaleDB: $VPS_IP:6543"
echo "  - API REST: http://$VPS_IP:8000"
echo "  - API Docs: http://$VPS_IP:8000/docs"
echo "  - Grafana: http://$VPS_IP:3000 (admin/admin)"
echo ""
print_step "Commandes utiles:"
echo "  - Logs: ssh $SSH_USER@$VPS_IP 'cd $REMOTE_DIR && docker compose logs -f'"
echo "  - Statut: ssh $SSH_USER@$VPS_IP 'cd $REMOTE_DIR && docker compose ps'"
echo "  - Monitoring: cd .agents/skills/ocean-sentinel-ops && python scripts/monitor.py"
echo ""
