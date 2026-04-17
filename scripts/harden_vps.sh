#!/bin/bash

# ============================================================================
# Ocean Sentinel V3.0 - Agent DevOps
# ============================================================================
# Script de durcissement (hardening) VPS Hostinger
# Sécurisation système, pare-feu UFW, fail2ban, optimisations
# ============================================================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_VERSION="3.0.0"
LOG_FILE="/var/log/oceansentinel_hardening.log"
SSH_PORT="${SSH_PORT:-22}"
ALLOWED_IPS="${ALLOWED_IPS:-}"  # IPs autorisées (séparées par des espaces)

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Ce script doit être exécuté en tant que root"
        exit 1
    fi
}

backup_file() {
    local file=$1
    if [[ -f "$file" ]]; then
        cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)"
        log "Backup créé: ${file}.backup"
    fi
}

# ============================================================================
# BANNIÈRE
# ============================================================================

show_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║          🌊 OCEAN SENTINEL V3.0 - VPS HARDENING 🌊           ║
║                                                                ║
║              Infrastructure de Recherche ILICO                 ║
║                  Bassin d'Arcachon - COAST-HF                  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    log "Version: $SCRIPT_VERSION"
    log "Démarrage du durcissement VPS Hostinger"
    echo ""
}

# ============================================================================
# ÉTAPE 1: MISE À JOUR SYSTÈME
# ============================================================================

update_system() {
    log "═══ [1/10] Mise à jour du système ═══"
    
    # Nettoyage des dépôts
    apt-get clean
    rm -rf /var/lib/apt/lists/*
    
    # Mise à jour
    apt-get update -qq
    apt-get upgrade -y -qq
    apt-get dist-upgrade -y -qq
    apt-get autoremove -y -qq
    apt-get autoclean -y -qq
    
    log "✓ Système mis à jour"
}

# ============================================================================
# ÉTAPE 2: INSTALLATION PAQUETS ESSENTIELS
# ============================================================================

install_essentials() {
    log "═══ [2/10] Installation des paquets essentiels ═══"
    
    apt-get install -y -qq \
        ufw \
        fail2ban \
        unattended-upgrades \
        apt-listchanges \
        logwatch \
        curl \
        wget \
        git \
        htop \
        iotop \
        net-tools \
        vim \
        tmux \
        rsync \
        ca-certificates \
        gnupg \
        lsb-release \
        software-properties-common
    
    log "✓ Paquets essentiels installés"
}

# ============================================================================
# ÉTAPE 3: CONFIGURATION SSH SÉCURISÉE
# ============================================================================

harden_ssh() {
    log "═══ [3/10] Durcissement SSH ═══"
    
    backup_file "/etc/ssh/sshd_config"
    
    # Configuration SSH sécurisée
    cat > /etc/ssh/sshd_config << EOF
# Ocean Sentinel V3.0 - Configuration SSH Durcie
# Généré le $(date)

# Port et protocole
Port ${SSH_PORT}
Protocol 2
AddressFamily inet

# Authentification
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes

# Sécurité
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server

# Performance et timeouts
ClientAliveInterval 300
ClientAliveCountMax 2
LoginGraceTime 60
MaxAuthTries 3
MaxSessions 10

# Logging
SyslogFacility AUTH
LogLevel VERBOSE

# Restrictions
AllowUsers ${SUDO_USER:-root}
DenyUsers guest
EOF

    # Redémarrage SSH
    systemctl restart sshd
    
    log "✓ SSH durci (Port: ${SSH_PORT})"
    log_warning "IMPORTANT: Testez la connexion SSH avant de fermer cette session!"
}

# ============================================================================
# ÉTAPE 4: CONFIGURATION PARE-FEU UFW
# ============================================================================

configure_ufw() {
    log "═══ [4/10] Configuration du pare-feu UFW ═══"
    
    # Désactiver UFW temporairement
    ufw --force disable
    
    # Réinitialiser les règles
    ufw --force reset
    
    # Politique par défaut
    ufw default deny incoming
    ufw default allow outgoing
    
    # SSH (CRITIQUE - toujours en premier)
    ufw allow ${SSH_PORT}/tcp comment 'SSH Ocean Sentinel'
    
    # Services Ocean Sentinel
    ufw allow 6543/tcp comment 'TimescaleDB'
    ufw allow 8000/tcp comment 'API FastAPI'
    ufw allow 3000/tcp comment 'Grafana'
    ufw allow 9090/tcp comment 'Prometheus'
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Restrictions par IP si configurées
    if [[ -n "$ALLOWED_IPS" ]]; then
        log "Configuration des restrictions IP..."
        for ip in $ALLOWED_IPS; do
            ufw allow from "$ip" to any port ${SSH_PORT} proto tcp comment "SSH autorisé: $ip"
        done
    fi
    
    # Protection contre le scan de ports
    ufw limit ${SSH_PORT}/tcp
    
    # Activer UFW
    ufw --force enable
    
    # Afficher le statut
    ufw status numbered
    
    log "✓ Pare-feu UFW configuré et activé"
}

# ============================================================================
# ÉTAPE 5: CONFIGURATION FAIL2BAN
# ============================================================================

configure_fail2ban() {
    log "═══ [5/10] Configuration Fail2Ban ═══"
    
    # Configuration jail SSH
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = root@localhost
sendername = Fail2Ban Ocean Sentinel
action = %(action_mwl)s

[sshd]
enabled = true
port = ${SSH_PORT}
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200

[sshd-ddos]
enabled = true
port = ${SSH_PORT}
filter = sshd-ddos
logpath = /var/log/auth.log
maxretry = 2
bantime = 86400

[postgresql]
enabled = true
port = 6543
filter = postgresql
logpath = /var/log/postgresql/postgresql-*.log
maxretry = 5
bantime = 3600
EOF

    # Filtre PostgreSQL personnalisé
    cat > /etc/fail2ban/filter.d/postgresql.conf << EOF
[Definition]
failregex = FATAL:.*authentication failed for user.*
            FATAL:.*password authentication failed.*
            FATAL:.*no pg_hba.conf entry.*
ignoreregex =
EOF

    # Redémarrage Fail2Ban
    systemctl enable fail2ban
    systemctl restart fail2ban
    
    log "✓ Fail2Ban configuré"
}

# ============================================================================
# ÉTAPE 6: MISES À JOUR AUTOMATIQUES
# ============================================================================

configure_auto_updates() {
    log "═══ [6/10] Configuration des mises à jour automatiques ═══"
    
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}";
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "03:00";
EOF

    cat > /etc/apt/apt.conf.d/20auto-upgrades << EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

    log "✓ Mises à jour automatiques configurées"
}

# ============================================================================
# ÉTAPE 7: DURCISSEMENT KERNEL (SYSCTL)
# ============================================================================

harden_kernel() {
    log "═══ [7/10] Durcissement du kernel ═══"
    
    backup_file "/etc/sysctl.conf"
    
    cat >> /etc/sysctl.conf << EOF

# ============================================================================
# Ocean Sentinel V3.0 - Optimisations Kernel
# ============================================================================

# Protection contre SYN flood
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_syn_retries = 2
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_max_syn_backlog = 4096

# Protection IP spoofing
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignorer les pings ICMP
net.ipv4.icmp_echo_ignore_all = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Désactiver le routage IP
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Ignorer les redirections ICMP
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0

# Log des paquets suspects
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# Protection contre les attaques de fragmentation
net.ipv4.ipfrag_high_thresh = 512000
net.ipv4.ipfrag_low_thresh = 446464

# Optimisations TCP
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_fin_timeout = 30

# Limites de connexions
net.core.somaxconn = 4096
net.core.netdev_max_backlog = 5000

# Optimisations mémoire
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# Sécurité processus
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
EOF

    # Appliquer les changements
    sysctl -p
    
    log "✓ Kernel durci"
}

# ============================================================================
# ÉTAPE 8: LIMITES SYSTÈME (ULIMIT)
# ============================================================================

configure_limits() {
    log "═══ [8/10] Configuration des limites système ═══"
    
    cat >> /etc/security/limits.conf << EOF

# Ocean Sentinel V3.0 - Limites système
* soft nofile 65536
* hard nofile 65536
* soft nproc 4096
* hard nproc 4096
postgres soft nofile 65536
postgres hard nofile 65536
EOF

    log "✓ Limites système configurées"
}

# ============================================================================
# ÉTAPE 9: MONITORING ET LOGS
# ============================================================================

configure_monitoring() {
    log "═══ [9/10] Configuration du monitoring ═══"
    
    # Logwatch
    cat > /etc/logwatch/conf/logwatch.conf << EOF
Output = mail
Format = html
MailTo = root
MailFrom = logwatch@oceansentinel
Range = yesterday
Detail = Med
Service = All
EOF

    # Rotation des logs
    cat > /etc/logrotate.d/oceansentinel << EOF
/var/log/oceansentinel*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}
EOF

    log "✓ Monitoring configuré"
}

# ============================================================================
# ÉTAPE 10: NETTOYAGE ET VÉRIFICATIONS
# ============================================================================

final_checks() {
    log "═══ [10/10] Vérifications finales ═══"
    
    # Nettoyage
    apt-get autoremove -y -qq
    apt-get autoclean -y -qq
    
    # Vérifications
    log "Vérification UFW:"
    ufw status numbered
    
    log "Vérification Fail2Ban:"
    fail2ban-client status
    
    log "Vérification SSH:"
    systemctl status sshd --no-pager | head -5
    
    # Statistiques
    log "Statistiques système:"
    echo "  - Uptime: $(uptime -p)"
    echo "  - Mémoire: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
    echo "  - Disque: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"
    
    log "✓ Vérifications terminées"
}

# ============================================================================
# RAPPORT FINAL
# ============================================================================

generate_report() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║          ✅ DURCISSEMENT VPS TERMINÉ AVEC SUCCÈS ✅           ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}📊 RÉSUMÉ DE LA CONFIGURATION:${NC}"
    echo -e "  • SSH Port: ${YELLOW}${SSH_PORT}${NC}"
    echo -e "  • UFW: ${GREEN}Actif${NC} ($(ufw status | grep -c 'ALLOW') règles)"
    echo -e "  • Fail2Ban: ${GREEN}Actif${NC}"
    echo -e "  • Mises à jour auto: ${GREEN}Activées${NC}"
    echo -e "  • Kernel: ${GREEN}Durci${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  ACTIONS REQUISES:${NC}"
    echo -e "  1. Testez la connexion SSH sur le port ${SSH_PORT}"
    echo -e "  2. Configurez les clés SSH si ce n'est pas déjà fait"
    echo -e "  3. Redémarrez le serveur: ${YELLOW}sudo reboot${NC}"
    echo -e "  4. Vérifiez les logs: ${YELLOW}tail -f $LOG_FILE${NC}"
    echo ""
    echo -e "${BLUE}📝 Log complet: ${YELLOW}$LOG_FILE${NC}"
    echo ""
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    check_root
    show_banner
    
    update_system
    install_essentials
    harden_ssh
    configure_ufw
    configure_fail2ban
    configure_auto_updates
    harden_kernel
    configure_limits
    configure_monitoring
    final_checks
    
    generate_report
}

# Exécution
main "$@"
