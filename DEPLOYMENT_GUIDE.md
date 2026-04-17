# 🚀 Ocean Sentinel V3.0 - Guide de Déploiement VPS Hostinger

**Version:** 3.0.0  
**Date:** 2026-04-16  
**Cible:** VPS Hostinger 512 Mo RAM  
**Auteur:** Ocean Sentinel Team - Agent DevOps

---

## 📋 Prérequis

### **Matériel VPS Hostinger**
- **RAM:** 512 Mo minimum
- **CPU:** 1 vCore
- **Disque:** 20 Go SSD
- **OS:** Ubuntu 22.04 LTS

### **Accès Requis**
- Accès SSH root
- Nom de domaine configuré (optionnel)
- Clé SSH générée localement

---

## 🔐 Étape 1 : Connexion SSH Initiale

### **1.1 Générer une Clé SSH (Local)**

```bash
# Sur votre machine locale
ssh-keygen -t ed25519 -C "oceansentinel@hostinger" -f ~/.ssh/oceansentinel_vps

# Afficher la clé publique
cat ~/.ssh/oceansentinel_vps.pub
```

### **1.2 Première Connexion au VPS**

```bash
# Connexion initiale (mot de passe fourni par Hostinger)
ssh root@<VOTRE_IP_VPS>

# Créer le répertoire SSH
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Ajouter votre clé publique
nano ~/.ssh/authorized_keys
# Coller la clé publique générée précédemment
# Ctrl+X, Y, Enter pour sauvegarder

chmod 600 ~/.ssh/authorized_keys
```

### **1.3 Tester la Connexion par Clé**

```bash
# Depuis votre machine locale
ssh -i ~/.ssh/oceansentinel_vps root@<VOTRE_IP_VPS>
```

---

## 🛡️ Étape 2 : Sécurisation du VPS

### **2.1 Télécharger le Script de Sécurisation**

```bash
# Créer le répertoire du projet
mkdir -p /opt/oceansentinel
cd /opt/oceansentinel

# Télécharger le script de sécurisation
wget https://raw.githubusercontent.com/VOTRE_REPO/ocean-sentinel/main/scripts/harden_vps.sh

# Rendre exécutable
chmod +x harden_vps.sh
```

### **2.2 Exécuter le Script de Sécurisation**

```bash
# Exécution avec port SSH par défaut (22)
./harden_vps.sh

# OU avec port SSH personnalisé (recommandé)
SSH_PORT=2222 ./harden_vps.sh
```

**⚠️ IMPORTANT:** Le script va :
- Configurer le pare-feu UFW
- Installer Fail2Ban
- Durcir SSH (désactiver mot de passe)
- Optimiser le kernel
- Configurer les mises à jour automatiques

**Durée:** ~5-10 minutes

### **2.3 Vérifier la Sécurisation**

```bash
# Vérifier UFW
sudo ufw status numbered

# Vérifier Fail2Ban
sudo fail2ban-client status

# Vérifier SSH
sudo systemctl status sshd
```

### **2.4 Redémarrer le VPS**

```bash
sudo reboot
```

**Attendez 2-3 minutes puis reconnectez-vous:**

```bash
# Si port SSH personnalisé (ex: 2222)
ssh -i ~/.ssh/oceansentinel_vps -p 2222 root@<VOTRE_IP_VPS>

# Sinon port par défaut
ssh -i ~/.ssh/oceansentinel_vps root@<VOTRE_IP_VPS>
```

---

## 🐳 Étape 3 : Installation Docker

### **3.1 Installer Docker Engine**

```bash
# Mise à jour des paquets
apt-get update
apt-get upgrade -y

# Installation des dépendances
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Ajouter la clé GPG Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Ajouter le dépôt Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Vérifier l'installation
docker --version
docker compose version
```

**Résultat attendu:**
```
Docker version 24.0.x
Docker Compose version v2.20.x
```

### **3.2 Configurer Docker pour VPS 512 Mo**

```bash
# Créer le fichier de configuration Docker
mkdir -p /etc/docker

cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "5m",
    "max-file": "2"
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
EOF

# Redémarrer Docker
systemctl restart docker
systemctl enable docker
```

### **3.3 Configurer le Swap (Critique pour 512 Mo RAM)**

```bash
# Créer un fichier swap de 1 Go
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Rendre permanent
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Optimiser swappiness pour VPS
sysctl vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf

# Vérifier
free -h
```

**Résultat attendu:**
```
              total        used        free      shared  buff/cache   available
Mem:          512Mi       150Mi       200Mi        10Mi       162Mi       340Mi
Swap:         1.0Gi         0Bi       1.0Gi
```

---

## 📦 Étape 4 : Déploiement Ocean Sentinel

### **4.1 Cloner le Projet**

```bash
cd /opt/oceansentinel

# Cloner depuis GitHub (ou télécharger les fichiers)
git clone https://github.com/VOTRE_REPO/ocean-sentinel.git .

# OU télécharger manuellement
# Transférer les fichiers depuis votre machine locale:
# scp -i ~/.ssh/oceansentinel_vps -r /chemin/local/* root@<IP_VPS>:/opt/oceansentinel/
```

### **4.2 Créer le Fichier .env**

```bash
# Créer le fichier de configuration
cat > .env << 'EOF'
# ============================================================================
# Ocean Sentinel V3.0 - Configuration Production VPS
# ============================================================================

# Base de données
POSTGRES_USER=oceansentinel
POSTGRES_PASSWORD=CHANGEZ_MOI_AVEC_MOT_DE_PASSE_FORT
POSTGRES_DB=oceansentinelle
POSTGRES_PORT=6543

# Sécurité
# Générer avec: openssl rand -base64 32
SECRET_KEY=CHANGEZ_MOI_AVEC_CLE_SECRETE

# Monitoring (optionnel)
GRAFANA_USER=admin
GRAFANA_PASSWORD=CHANGEZ_MOI_AVEC_MOT_DE_PASSE_FORT

# API (optionnel)
API_PORT=8000
EOF

# Sécuriser le fichier
chmod 600 .env
```

**⚠️ IMPORTANT:** Changez les mots de passe !

```bash
# Générer un mot de passe fort
openssl rand -base64 32
```

### **4.3 Créer les Répertoires Nécessaires**

```bash
# Créer la structure de répertoires
mkdir -p /opt/oceansentinel/{data,logs/ingestion,models,init-scripts}

# Permissions
chmod 755 /opt/oceansentinel/data
chmod 755 /opt/oceansentinel/logs
```

### **4.4 Vérifier les Fichiers de Configuration**

```bash
# Vérifier que les fichiers essentiels existent
ls -lh /opt/oceansentinel/

# Doit contenir:
# - docker-compose-vps.yml
# - Dockerfile.ingestion
# - scripts/ingestion_stream.py
# - init-scripts/01-init-timescaledb.sql
# - .env
```

---

## 🚀 Étape 5 : Lancement de l'Infrastructure

### **5.1 Construire les Images Docker**

```bash
cd /opt/oceansentinel

# Construire l'image d'ingestion
docker compose -f docker-compose-vps.yml build ingestion
```

**Durée:** ~5-10 minutes (première fois)

### **5.2 Démarrer TimescaleDB**

```bash
# Démarrer uniquement TimescaleDB d'abord
docker compose -f docker-compose-vps.yml up -d timescaledb

# Attendre que la base soit prête (30-60 secondes)
docker compose -f docker-compose-vps.yml logs -f timescaledb
```

**Logs attendus:**
```
oceansentinel_timescaledb | PostgreSQL init process complete; ready for start up.
oceansentinel_timescaledb | LOG:  database system is ready to accept connections
```

**Appuyez sur Ctrl+C pour quitter les logs**

### **5.3 Vérifier TimescaleDB**

```bash
# Vérifier le healthcheck
docker compose -f docker-compose-vps.yml ps

# Doit afficher:
# NAME                          STATUS              PORTS
# oceansentinel_timescaledb     Up (healthy)        0.0.0.0:6543->5432/tcp

# Tester la connexion
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "\dt barag.*"
```

**Résultat attendu:**
```
             List of relations
 Schema |    Name     | Type  |     Owner      
--------+-------------+-------+----------------
 barag  | sensor_data | table | oceansentinel
```

### **5.4 Démarrer le Service d'Ingestion**

```bash
# Démarrer le service d'ingestion
docker compose -f docker-compose-vps.yml up -d ingestion

# Vérifier les logs
docker compose -f docker-compose-vps.yml logs -f ingestion
```

**Logs attendus:**
```
oceansentinel_ingestion | [FAILOVER] Détection source de données active
oceansentinel_ingestion | [FAILOVER] Test connexion: https://erddap.ifremer.fr/erddap/tabledap/EXIN0001
oceansentinel_ingestion | [FAILOVER] Serveur indisponible (HTTP 404)
oceansentinel_ingestion | [FAILOVER] Bascule sur fallback
oceansentinel_ingestion | [FAILOVER] Source fallback active: NOAA
oceansentinel_ingestion | [ERDDAP] Connexion OPeNDAP réussie
oceansentinel_ingestion | [DB] Connexion établie: timescaledb:5432/oceansentinelle
oceansentinel_ingestion | [SUCCESS] Ingestion démarrée
```

---

## ✅ Étape 6 : Vérifications Post-Déploiement

### **6.1 Vérifier l'État des Conteneurs**

```bash
# Statut global
docker compose -f docker-compose-vps.yml ps

# Doit afficher:
# NAME                          STATUS              PORTS
# oceansentinel_timescaledb     Up (healthy)        0.0.0.0:6543->5432/tcp
# oceansentinel_ingestion       Up                  -
```

### **6.2 Vérifier l'Utilisation Mémoire**

```bash
# Mémoire système
free -h

# Mémoire des conteneurs
docker stats --no-stream

# Résultat attendu:
# CONTAINER                     MEM USAGE / LIMIT     MEM %
# oceansentinel_timescaledb     180MiB / 256MiB       70%
# oceansentinel_ingestion       120MiB / 256MiB       47%
# TOTAL:                        ~300 MiB / 512 MiB    58%
```

**✅ Si mémoire < 400 Mo utilisée, c'est parfait !**

### **6.3 Vérifier les Données Ingérées**

```bash
# Compter les lignes dans la base
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) as total_records FROM barag.sensor_data;"

# Afficher les 5 dernières lignes
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT time, station_id, temperature_water, salinity FROM barag.sensor_data ORDER BY time DESC LIMIT 5;"
```

**Résultat attendu:**
```
 total_records 
---------------
           128

           time            | station_id | temperature_water | salinity 
---------------------------+------------+-------------------+----------
 2026-04-16 20:00:00+00    | NOAA_TAO   |             25.3  |     NULL
 2026-04-16 19:00:00+00    | NOAA_TAO   |             25.1  |     NULL
 ...
```

### **6.4 Vérifier les Logs**

```bash
# Logs d'ingestion
tail -f /opt/oceansentinel/logs/ingestion/ingestion_stream.log

# Logs Docker
docker compose -f docker-compose-vps.yml logs --tail=50 -f
```

---

## 🔧 Étape 7 : Configuration Automatique (Cron)

### **7.1 Créer un Script de Surveillance**

```bash
cat > /opt/oceansentinel/monitor.sh << 'EOF'
#!/bin/bash
# Ocean Sentinel - Script de surveillance

cd /opt/oceansentinel

# Vérifier que les conteneurs tournent
if ! docker compose -f docker-compose-vps.yml ps | grep -q "Up"; then
    echo "[$(date)] ALERTE: Conteneurs arrêtés, redémarrage..." >> /var/log/oceansentinel_monitor.log
    docker compose -f docker-compose-vps.yml up -d
fi

# Vérifier la mémoire
MEM_USED=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ $MEM_USED -gt 90 ]; then
    echo "[$(date)] ALERTE: Mémoire élevée ($MEM_USED%)" >> /var/log/oceansentinel_monitor.log
fi
EOF

chmod +x /opt/oceansentinel/monitor.sh
```

### **7.2 Configurer le Cron**

```bash
# Éditer le crontab
crontab -e

# Ajouter ces lignes:
# Surveillance toutes les 5 minutes
*/5 * * * * /opt/oceansentinel/monitor.sh

# Ingestion quotidienne à 2h du matin (si fichiers locaux)
0 2 * * * cd /opt/oceansentinel && docker compose -f docker-compose-vps.yml exec -T ingestion python scripts/ingestion_stream.py /data/daily.nc >> /var/log/oceansentinel_cron.log 2>&1

# Nettoyage des logs hebdomadaire
0 3 * * 0 find /opt/oceansentinel/logs -name "*.log" -mtime +30 -delete
```

---

## 📊 Étape 8 : Monitoring et Maintenance

### **8.1 Commandes de Monitoring**

```bash
# Statut global
docker compose -f docker-compose-vps.yml ps

# Logs en temps réel
docker compose -f docker-compose-vps.yml logs -f

# Statistiques mémoire/CPU
docker stats

# Espace disque
df -h /opt/oceansentinel

# Nombre de lignes en base
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT COUNT(*) FROM barag.sensor_data;"
```

### **8.2 Commandes de Maintenance**

```bash
# Redémarrer les services
docker compose -f docker-compose-vps.yml restart

# Arrêter les services
docker compose -f docker-compose-vps.yml down

# Démarrer les services
docker compose -f docker-compose-vps.yml up -d

# Voir les logs d'un service spécifique
docker compose -f docker-compose-vps.yml logs -f timescaledb
docker compose -f docker-compose-vps.yml logs -f ingestion

# Nettoyer les images inutilisées
docker system prune -a --volumes
```

### **8.3 Backup de la Base de Données**

```bash
# Créer un backup
docker exec oceansentinel_timescaledb pg_dump -U oceansentinel oceansentinelle | gzip > /opt/oceansentinel/backup_$(date +%Y%m%d).sql.gz

# Restaurer un backup
gunzip < /opt/oceansentinel/backup_20260416.sql.gz | docker exec -i oceansentinel_timescaledb psql -U oceansentinel oceansentinelle
```

---

## 🚨 Dépannage

### **Problème: Conteneur ne démarre pas**

```bash
# Vérifier les logs
docker compose -f docker-compose-vps.yml logs timescaledb
docker compose -f docker-compose-vps.yml logs ingestion

# Vérifier la configuration
docker compose -f docker-compose-vps.yml config

# Reconstruire l'image
docker compose -f docker-compose-vps.yml build --no-cache ingestion
```

### **Problème: Mémoire insuffisante**

```bash
# Vérifier la mémoire
free -h
docker stats --no-stream

# Augmenter le swap
swapoff -a
fallocate -l 2G /swapfile
mkswap /swapfile
swapon /swapfile

# Redémarrer les conteneurs
docker compose -f docker-compose-vps.yml restart
```

### **Problème: Connexion base de données refusée**

```bash
# Vérifier que TimescaleDB est démarré
docker compose -f docker-compose-vps.yml ps timescaledb

# Vérifier les logs
docker compose -f docker-compose-vps.yml logs timescaledb

# Tester la connexion
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle
```

### **Problème: Failover ERDDAP échoue**

```bash
# Vérifier la connectivité réseau
curl -I https://erddap.ifremer.fr/erddap/tabledap/EXIN0001
curl -I https://coastwatch.pfeg.noaa.gov/erddap/tabledap/pmelTaoDySst

# Vérifier les logs d'ingestion
docker compose -f docker-compose-vps.yml logs ingestion | grep FAILOVER
```

---

## 📝 Checklist de Déploiement

### **Avant le Déploiement**
- [ ] VPS Hostinger provisionné (512 Mo RAM minimum)
- [ ] Accès SSH root configuré
- [ ] Clé SSH générée et ajoutée
- [ ] Nom de domaine configuré (optionnel)

### **Sécurisation**
- [ ] Script `harden_vps.sh` exécuté
- [ ] UFW activé et configuré
- [ ] Fail2Ban actif
- [ ] SSH durci (clés uniquement)
- [ ] VPS redémarré

### **Docker**
- [ ] Docker Engine installé
- [ ] Docker Compose installé
- [ ] Swap configuré (1 Go)
- [ ] Configuration Docker optimisée

### **Déploiement**
- [ ] Projet cloné dans `/opt/oceansentinel`
- [ ] Fichier `.env` créé et sécurisé
- [ ] Répertoires créés (`data`, `logs`, `models`)
- [ ] Image d'ingestion construite
- [ ] TimescaleDB démarré et healthy
- [ ] Service d'ingestion démarré

### **Vérifications**
- [ ] Conteneurs en état "Up"
- [ ] Mémoire < 400 Mo utilisée
- [ ] Données ingérées dans la base
- [ ] Logs sans erreur
- [ ] Failover fonctionnel

### **Maintenance**
- [ ] Cron de surveillance configuré
- [ ] Backup automatique configuré
- [ ] Monitoring actif

---

## 🎉 Déploiement Réussi !

Si toutes les vérifications sont passées, votre infrastructure Ocean Sentinel V3.0 est opérationnelle !

**Prochaines étapes:**
1. Configurer l'URL ERDDAP correcte pour BARAG (une fois obtenue)
2. Ajouter des sources de données locales (fichiers NetCDF)
3. Déployer l'API REST (optionnel)
4. Configurer Grafana pour la visualisation (optionnel)

---

## 📞 Support

**En cas de problème:**
- Consulter les logs: `/opt/oceansentinel/logs/`
- Vérifier la documentation: `MISSION_4_RAPPORT.md`
- Contacter l'équipe COAST-HF: contact@coast-hf.fr

---

**Guide généré le:** 2026-04-16  
**Version:** 3.0.0  
**Auteur:** Ocean Sentinel Team - Agent DevOps
