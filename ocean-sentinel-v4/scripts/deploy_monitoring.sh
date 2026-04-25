#!/bin/bash
# Script de déploiement monitoring Ocean Sentinel API
# Installe: Prometheus, Grafana, Node Exporter, Blackbox Exporter

set -euo pipefail

echo "======================================"
echo "DÉPLOIEMENT MONITORING OCEAN SENTINEL"
echo "======================================"
echo ""

# Variables
PROMETHEUS_VERSION="2.45.0"
GRAFANA_VERSION="10.0.0"
NODE_EXPORTER_VERSION="1.6.0"
BLACKBOX_EXPORTER_VERSION="0.24.0"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions
log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Vérifier droits root
if [ "$EUID" -ne 0 ]; then
    log_error "Ce script doit être exécuté en root"
    exit 1
fi

# 2. Créer utilisateurs système
log_info "Création utilisateurs système..."
useradd --no-create-home --shell /bin/false prometheus || true
useradd --no-create-home --shell /bin/false node_exporter || true
useradd --no-create-home --shell /bin/false blackbox_exporter || true

# 3. Installer Prometheus
log_info "Installation Prometheus ${PROMETHEUS_VERSION}..."
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz
tar -xzf prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz
cd prometheus-${PROMETHEUS_VERSION}.linux-amd64

mkdir -p /etc/prometheus /var/lib/prometheus
cp prometheus promtool /usr/local/bin/
cp -r consoles console_libraries /etc/prometheus/
chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus

# Configuration Prometheus
cat > /etc/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ocean-sentinel-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - https://oceansentinelle.fr/health
          - https://oceansentinelle.fr/api/v1/stations
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
EOF

# Service systemd Prometheus
cat > /etc/systemd/system/prometheus.service << 'EOF'
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus/ \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
EOF

# 4. Installer Node Exporter
log_info "Installation Node Exporter ${NODE_EXPORTER_VERSION}..."
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz
tar -xzf node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz
cp node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter /usr/local/bin/
chown node_exporter:node_exporter /usr/local/bin/node_exporter

# Service systemd Node Exporter
cat > /etc/systemd/system/node_exporter.service << 'EOF'
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# 5. Installer Blackbox Exporter
log_info "Installation Blackbox Exporter ${BLACKBOX_EXPORTER_VERSION}..."
cd /tmp
wget https://github.com/prometheus/blackbox_exporter/releases/download/v${BLACKBOX_EXPORTER_VERSION}/blackbox_exporter-${BLACKBOX_EXPORTER_VERSION}.linux-amd64.tar.gz
tar -xzf blackbox_exporter-${BLACKBOX_EXPORTER_VERSION}.linux-amd64.tar.gz
cp blackbox_exporter-${BLACKBOX_EXPORTER_VERSION}.linux-amd64/blackbox_exporter /usr/local/bin/
chown blackbox_exporter:blackbox_exporter /usr/local/bin/blackbox_exporter

mkdir -p /etc/blackbox_exporter
cat > /etc/blackbox_exporter/blackbox.yml << 'EOF'
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200]
      method: GET
      preferred_ip_protocol: "ip4"
EOF

# Service systemd Blackbox Exporter
cat > /etc/systemd/system/blackbox_exporter.service << 'EOF'
[Unit]
Description=Blackbox Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=blackbox_exporter
Group=blackbox_exporter
Type=simple
ExecStart=/usr/local/bin/blackbox_exporter --config.file=/etc/blackbox_exporter/blackbox.yml

[Install]
WantedBy=multi-user.target
EOF

# 6. Installer Grafana
log_info "Installation Grafana ${GRAFANA_VERSION}..."
apt-get install -y apt-transport-https software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | tee -a /etc/apt/sources.list.d/grafana.list
apt-get update
apt-get install -y grafana

# Configuration Grafana datasource Prometheus
mkdir -p /etc/grafana/provisioning/datasources
cat > /etc/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    editable: true
EOF

# 7. Démarrer services
log_info "Démarrage des services..."
systemctl daemon-reload
systemctl enable prometheus node_exporter blackbox_exporter grafana-server
systemctl start prometheus node_exporter blackbox_exporter grafana-server

# 8. Vérifier statuts
sleep 3
echo ""
echo "======================================"
echo "VÉRIFICATION SERVICES"
echo "======================================"

services=("prometheus" "node_exporter" "blackbox_exporter" "grafana-server")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        log_info "$service: ACTIF"
    else
        log_error "$service: INACTIF"
    fi
done

# 9. Configurer Nginx reverse proxy
log_info "Configuration Nginx reverse proxy..."
cat > /etc/nginx/sites-available/monitoring << 'EOF'
# Prometheus
server {
    listen 9090;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:9090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Grafana
server {
    listen 3000;
    server_name oceansentinelle.fr;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -sf /etc/nginx/sites-available/monitoring /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 10. Afficher URLs
echo ""
echo "======================================"
echo "✅ MONITORING DÉPLOYÉ AVEC SUCCÈS"
echo "======================================"
echo ""
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://oceansentinelle.fr:3000 (admin/admin)"
echo "🖥️  Node Exporter: http://localhost:9100/metrics"
echo "🔍 Blackbox Exporter: http://localhost:9115"
echo ""
echo "Prochaines étapes:"
echo "1. Importer dashboard Grafana: monitoring/grafana_dashboard.json"
echo "2. Configurer alertes: monitoring/alerts.yml"
echo "3. Tester endpoints: newman run tests/contract/ocean_sentinel_api.postman_collection.json"
echo ""
