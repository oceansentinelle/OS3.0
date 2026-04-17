#!/bin/bash

# =====================================================
# Script d'Installation Docker pour VPS Ocean Sentinel
# =====================================================

set -e

echo "🔧 Installation de Docker sur VPS Ubuntu..."
echo ""

# 1. Nettoyage des installations partielles
echo "[1/6] Nettoyage..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# 2. Mise à jour des dépôts (avec retry)
echo "[2/6] Mise à jour des dépôts..."
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*
sudo apt-get update

# 3. Installation des prérequis
echo "[3/6] Installation des prérequis..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 4. Ajout de la clé GPG Docker
echo "[4/6] Configuration du dépôt Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 5. Ajout du dépôt Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 6. Installation de Docker
echo "[5/6] Installation de Docker Engine..."
sudo apt-get update
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# 7. Démarrage de Docker
echo "[6/6] Démarrage de Docker..."
sudo systemctl enable docker
sudo systemctl start docker

# Vérification
echo ""
echo "✅ Installation terminée !"
echo ""
docker --version
docker compose version
echo ""
echo "🧪 Test de Docker..."
sudo docker run hello-world

echo ""
echo "✅ Docker est opérationnel !"
