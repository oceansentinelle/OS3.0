# 🌊 Ocean Sentinel V3.0 - Guide d'Installation Pas à Pas

**Guide Anti-Erreur - Procédure Complète et Sécurisée**

---

## 📋 Vue d'Ensemble

Ce guide vous accompagne **étape par étape** pour installer Ocean Sentinel V3.0 sans risque d'erreur. Chaque étape est **validée** avant de passer à la suivante.

**Durée estimée:** 30-45 minutes  
**Niveau:** Débutant à Intermédiaire  
**Prérequis:** Windows 10/11, Accès VPS Hostinger

---

## ✅ PHASE 1 : PRÉPARATION LOCALE (Windows)

### Étape 1.1 : Vérifier les Fichiers du Projet

**Objectif:** S'assurer que tous les fichiers ont été générés correctement.

**Action:**
```powershell
# Ouvrir PowerShell dans le répertoire du projet
cd C:\Users\ktprt\Documents\OSwindsurf

# Lister les fichiers critiques
Get-ChildItem -Recurse -Include *.py,*.yml,*.sh,*.md | Select-Object Name, Length
```

**Validation:**
- [ ] `docker-compose-v3.yml` existe (> 5 Ko)
- [ ] `scripts/ingestion_stream.py` existe (> 20 Ko)
- [ ] `scripts/ml_pipeline.py` existe (> 25 Ko)
- [ ] `scripts/harden_vps.sh` existe (> 15 Ko)
- [ ] `.windsurf/skills/project-context.md` existe (> 30 Ko)

**Si un fichier manque:** Demandez à l'IA de le régénérer avant de continuer.

---

### Étape 1.2 : Exécuter le Script d'Installation Automatique

**Objectif:** Créer automatiquement l'arborescence complète du projet.

**Action:**
```powershell
# Exécuter le script d'installation
.\setup_project.ps1
```

**Ce que fait le script:**
1. ✅ Crée tous les dossiers nécessaires (`data/`, `logs/`, `models/`, etc.)
2. ✅ Vérifie la présence des fichiers critiques
3. ✅ Génère le fichier `.env` avec un mot de passe fort
4. ✅ Crée les fichiers de configuration (Prometheus, Nginx, .gitignore)
5. ✅ Affiche un rapport détaillé

**Validation:**
- [ ] Le script s'exécute sans erreur
- [ ] Message "✅ INSTALLATION TERMINÉE AVEC SUCCÈS" affiché
- [ ] Fichier `.env` créé avec un mot de passe généré
- [ ] **IMPORTANT:** Copiez et sauvegardez le mot de passe affiché

**Exemple de mot de passe généré:**
```
🔐 IMPORTANT: Mot de passe PostgreSQL généré:
   aB3dE7fG9hJ2kL4mN6pQ8rS0tU1vW5xY
```

**⚠️ CRITIQUE:** Sauvegardez ce mot de passe dans un gestionnaire sécurisé (KeePass, 1Password, etc.)

---

### Étape 1.3 : Vérifier le Fichier .env

**Objectif:** S'assurer que toutes les variables d'environnement sont correctes.

**Action:**
```powershell
# Ouvrir le fichier .env
notepad .env
```

**Vérifications:**
```env
# Base de données
POSTGRES_USER=oceansentinel              ✓ OK
POSTGRES_PASSWORD=VOTRE_MOT_DE_PASSE     ✓ Vérifier qu'il est bien rempli
POSTGRES_DB=oceansentinelle              ✓ OK
POSTGRES_PORT=6543                       ✓ OK

# Connexion externe (IMPORTANT pour Windows)
DB_HOST=VOTRE_IP_VPS                     ⚠️ À REMPLIR (voir étape suivante)
DB_PORT=6543                             ✓ OK
```

**Validation:**
- [ ] `POSTGRES_PASSWORD` contient un mot de passe fort (32 caractères)
- [ ] `DB_HOST` sera rempli après avoir obtenu l'IP du VPS

---

### Étape 1.4 : Obtenir l'IP du VPS

**Objectif:** Récupérer l'adresse IP publique de votre VPS Hostinger.

**Méthode 1 : Via le Panel Hostinger**
1. Connexion à https://hpanel.hostinger.com
2. Sélectionner votre VPS (srv1341436)
3. L'IP est affichée en haut : `XX.XX.XX.XX`

**Méthode 2 : Via SSH**
```bash
# Se connecter au VPS
ssh root@srv1341436.hostinger.com

# Afficher l'IP publique
curl ifconfig.me
```

**Action:**
```powershell
# Éditer .env et ajouter l'IP
notepad .env

# Remplacer:
DB_HOST=VOTRE_IP_VPS

# Par (exemple):
DB_HOST=185.123.45.67
```

**Validation:**
- [ ] IP du VPS notée : `___.___.___. ___`
- [ ] `DB_HOST` dans `.env` mis à jour

---

### Étape 1.5 : Vérifier la Structure du Projet

**Objectif:** Confirmer que l'arborescence est complète.

**Action:**
```powershell
# Afficher l'arborescence
tree /F /A
```

**Structure attendue:**
```
OSwindsurf/
├── data/
│   ├── netcdf/
│   ├── csv/
│   └── grib2/
├── logs/
│   ├── ingestion/
│   └── ml/
├── models/
│   ├── lstm/
│   └── isolation_forest/
├── backups/
├── scripts/
│   ├── ingestion_stream.py
│   ├── ml_pipeline.py
│   ├── harden_vps.sh
│   ├── query.py
│   └── inspect_netcdf.py
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
├── nginx/
│   ├── nginx.conf
│   └── ssl/
├── .windsurf/
│   └── skills/
│       └── project-context.md
├── .env
├── .gitignore
├── docker-compose-v3.yml
└── requirements*.txt
```

**Validation:**
- [ ] Tous les dossiers principaux existent
- [ ] Les scripts Python sont présents
- [ ] Les fichiers de configuration existent

---

## ✅ PHASE 2 : INITIALISATION GIT

### Étape 2.1 : Initialiser le Dépôt Git

**Objectif:** Préparer le projet pour le versionnement et le transfert vers le VPS.

**Action:**
```powershell
# Initialiser Git
git init

# Vérifier le statut
git status
```

**Validation:**
- [ ] Message "Initialized empty Git repository" affiché
- [ ] Fichiers non suivis listés

---

### Étape 2.2 : Premier Commit

**Objectif:** Sauvegarder l'état initial du projet.

**Action:**
```powershell
# Ajouter tous les fichiers
git add .

# Vérifier ce qui sera commité
git status

# Créer le commit
git commit -m "Ocean Sentinel V3.0 - Configuration initiale"
```

**Validation:**
- [ ] Message "X files changed" affiché
- [ ] Aucune erreur

**⚠️ Vérification importante:**
```powershell
# S'assurer que .env n'est PAS commité
git log --name-only | Select-String ".env"
```

**Résultat attendu:** Aucune ligne contenant `.env` (sauf `.env.example`)

---

### Étape 2.3 : Créer un Dépôt GitHub/GitLab (Optionnel mais Recommandé)

**Objectif:** Héberger le code sur un dépôt distant pour faciliter le déploiement.

**Option A : GitHub**
1. Aller sur https://github.com/new
2. Nom du dépôt : `oceansentinel-v3`
3. Visibilité : **Privé** (recommandé)
4. Ne pas initialiser avec README
5. Créer le dépôt

**Option B : GitLab**
1. Aller sur https://gitlab.com/projects/new
2. Nom : `oceansentinel-v3`
3. Visibilité : **Privé**
4. Créer le projet

**Action:**
```powershell
# Ajouter le dépôt distant (remplacer par votre URL)
git remote add origin https://github.com/VOTRE_USERNAME/oceansentinel-v3.git

# Pousser le code
git branch -M main
git push -u origin main
```

**Validation:**
- [ ] Code poussé sans erreur
- [ ] Dépôt visible sur GitHub/GitLab

---

## ✅ PHASE 3 : DÉPLOIEMENT SUR LE VPS

### Étape 3.1 : Connexion au VPS

**Objectif:** Se connecter au VPS Hostinger en SSH.

**Action:**
```powershell
# Depuis PowerShell Windows
ssh root@VOTRE_IP_VPS

# Ou avec le nom d'hôte Hostinger
ssh root@srv1341436.hostinger.com
```

**Validation:**
- [ ] Connexion réussie
- [ ] Prompt du VPS affiché : `root@srv1341436:~#`

**Si erreur de connexion:**
- Vérifier l'IP du VPS
- Vérifier que le port SSH est ouvert (22)
- Utiliser le panel Hostinger pour réinitialiser le mot de passe root si nécessaire

---

### Étape 3.2 : Vérifier Docker sur le VPS

**Objectif:** S'assurer que Docker est installé et fonctionnel.

**Action:**
```bash
# Vérifier la version de Docker
docker --version

# Vérifier Docker Compose
docker compose version

# Tester Docker
docker run hello-world
```

**Validation:**
- [ ] Docker version 24.0+ affiché
- [ ] Docker Compose version 2.20+ affiché
- [ ] Message "Hello from Docker!" affiché

**Si Docker n'est pas installé:**
```bash
# Utiliser le script d'installation fourni précédemment
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installer Docker Compose
sudo apt install docker-compose-plugin -y
```

---

### Étape 3.3 : Cloner le Projet sur le VPS

**Objectif:** Récupérer le code depuis Git.

**Action:**
```bash
# Aller dans le répertoire home
cd ~

# Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/oceansentinel-v3.git oceansentinel

# Entrer dans le répertoire
cd oceansentinel

# Vérifier les fichiers
ls -la
```

**Validation:**
- [ ] Dossier `oceansentinel` créé
- [ ] Fichiers présents (docker-compose-v3.yml, scripts/, etc.)
- [ ] Fichier `.env.example` présent
- [ ] Fichier `.env` **ABSENT** (normal, il est dans .gitignore)

---

### Étape 3.4 : Configurer .env sur le VPS

**Objectif:** Créer le fichier .env avec les bonnes valeurs pour le VPS.

**Action:**
```bash
# Copier le template
cp .env.example .env

# Éditer le fichier
nano .env
```

**Configuration pour le VPS:**
```env
# Base de données (CONNEXION LOCALE sur le VPS)
POSTGRES_USER=oceansentinel
POSTGRES_PASSWORD=VOTRE_MOT_DE_PASSE_COPIE_DEPUIS_WINDOWS
POSTGRES_DB=oceansentinelle
POSTGRES_PORT=6543

# Connexion interne Docker (IMPORTANT: localhost pour le VPS)
DB_HOST=localhost
DB_PORT=6543
DB_NAME=oceansentinelle
DB_USER=oceansentinel
DB_PASSWORD=VOTRE_MOT_DE_PASSE_COPIE_DEPUIS_WINDOWS

# API
API_PORT=8000

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=CHOISIR_UN_MOT_DE_PASSE_GRAFANA

# Alertes
ALERT_PH_MIN=7.8
ALERT_O2_MIN=150
```

**⚠️ IMPORTANT:**
- `DB_HOST=localhost` sur le VPS (connexion interne Docker)
- `DB_HOST=VOTRE_IP_VPS` sur Windows (connexion externe)

**Sauvegarder:**
- `Ctrl+O` puis `Entrée` pour sauvegarder
- `Ctrl+X` pour quitter nano

**Validation:**
```bash
# Vérifier que le fichier est bien configuré
cat .env | grep POSTGRES_PASSWORD
cat .env | grep DB_HOST
```

- [ ] `POSTGRES_PASSWORD` contient le mot de passe
- [ ] `DB_HOST=localhost` (pas l'IP publique)

---

### Étape 3.5 : Créer les Répertoires de Données

**Objectif:** Préparer les volumes Docker persistants.

**Action:**
```bash
# Créer le répertoire de données TimescaleDB
sudo mkdir -p /opt/oceansentinel/data

# Définir les permissions (utilisateur PostgreSQL = UID 999)
sudo chown -R 999:999 /opt/oceansentinel/data
sudo chmod 700 /opt/oceansentinel/data

# Créer les autres répertoires
mkdir -p ~/oceansentinel/data/{netcdf,csv,grib2}
mkdir -p ~/oceansentinel/logs/{ingestion,ml}
mkdir -p ~/oceansentinel/models/{lstm,isolation_forest}
mkdir -p ~/oceansentinel/backups
```

**Validation:**
```bash
# Vérifier les permissions
ls -ld /opt/oceansentinel/data
```

**Résultat attendu:**
```
drwx------ 2 systemd-coredump systemd-coredump 4096 Apr 16 21:00 /opt/oceansentinel/data
```

- [ ] Permissions `drwx------` (700)
- [ ] Propriétaire UID 999

---

## ✅ PHASE 4 : DURCISSEMENT DU VPS (SÉCURITÉ)

### Étape 4.1 : Exécuter le Script de Durcissement

**Objectif:** Sécuriser le VPS avec UFW, Fail2Ban, SSH durci.

**⚠️ ATTENTION:** Cette étape modifie la configuration SSH. **Testez la connexion SSH dans une autre fenêtre avant de fermer la session actuelle.**

**Action:**
```bash
cd ~/oceansentinel

# Rendre le script exécutable
chmod +x scripts/harden_vps.sh

# Exécuter le script (durée: 5-10 minutes)
sudo bash scripts/harden_vps.sh
```

**Ce que fait le script:**
1. ✅ Met à jour le système
2. ✅ Installe UFW, Fail2Ban
3. ✅ Durcit SSH (désactive mot de passe, active clés uniquement)
4. ✅ Configure le pare-feu (ports 22, 6543, 8000, 3000, 9090, 80, 443)
5. ✅ Optimise le kernel
6. ✅ Active les mises à jour automatiques

**Validation:**
```bash
# Vérifier UFW
sudo ufw status numbered

# Vérifier Fail2Ban
sudo fail2ban-client status

# Vérifier SSH
sudo systemctl status sshd
```

- [ ] UFW actif avec 7+ règles
- [ ] Fail2Ban actif
- [ ] SSH actif

**⚠️ CRITIQUE: Tester la connexion SSH**

**Dans une NOUVELLE fenêtre PowerShell (ne pas fermer l'ancienne):**
```powershell
ssh root@VOTRE_IP_VPS
```

- [ ] Connexion réussie dans la nouvelle fenêtre
- [ ] **Seulement après validation:** Fermer l'ancienne session

---

### Étape 4.2 : Configurer le Pare-feu Hostinger (Panel Web)

**Objectif:** Autoriser les ports nécessaires au niveau du pare-feu Hostinger.

**Action:**
1. Aller sur https://hpanel.hostinger.com
2. Sélectionner VPS → Pare-feu
3. Ajouter les règles suivantes :

| Nom | Port | Protocole | Source | Action |
|-----|------|-----------|--------|--------|
| SSH | 22 | TCP | 0.0.0.0/0 | AUTORISER |
| TimescaleDB | 6543 | TCP | 0.0.0.0/0 | AUTORISER |
| API | 8000 | TCP | 0.0.0.0/0 | AUTORISER |
| Grafana | 3000 | TCP | 0.0.0.0/0 | AUTORISER |
| Prometheus | 9090 | TCP | 0.0.0.0/0 | AUTORISER |
| HTTP | 80 | TCP | 0.0.0.0/0 | AUTORISER |
| HTTPS | 443 | TCP | 0.0.0.0/0 | AUTORISER |

**Validation:**
- [ ] 7 règles créées
- [ ] Règles synchronisées (bouton "Appliquer")

---

## ✅ PHASE 5 : LANCEMENT D'OCEAN SENTINEL

### Étape 5.1 : Vérifier la Configuration Docker Compose

**Objectif:** S'assurer que docker-compose-v3.yml est correct.

**Action:**
```bash
cd ~/oceansentinel

# Valider la syntaxe
docker compose -f docker-compose-v3.yml config
```

**Validation:**
- [ ] Aucune erreur de syntaxe
- [ ] Configuration affichée correctement

---

### Étape 5.2 : Lancer Ocean Sentinel V3.0

**Objectif:** Démarrer tous les services Docker.

**Action:**
```bash
# Lancer en arrière-plan
docker compose -f docker-compose-v3.yml up -d

# Suivre les logs
docker compose -f docker-compose-v3.yml logs -f
```

**Validation:**
```bash
# Vérifier que tous les conteneurs sont actifs
docker compose -f docker-compose-v3.yml ps
```

**Résultat attendu:**
```
NAME                          STATUS
oceansentinel_timescaledb     Up (healthy)
oceansentinel_ingestion       Up
oceansentinel_ml              Up
oceansentinel_api             Up
oceansentinel_prometheus      Up
oceansentinel_grafana         Up
oceansentinel_nginx           Up
```

- [ ] 7 conteneurs en statut "Up"
- [ ] TimescaleDB en statut "healthy"

**Si un conteneur est en erreur:**
```bash
# Voir les logs du conteneur problématique
docker logs oceansentinel_NOMDUCONTENEUR
```

---

### Étape 5.3 : Vérifier TimescaleDB

**Objectif:** Confirmer que la base de données est opérationnelle.

**Action:**
```bash
# Tester la connexion
docker exec oceansentinel_timescaledb pg_isready -U oceansentinel -d oceansentinelle

# Vérifier l'extension TimescaleDB
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';"

# Vérifier les tables
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "\dt barag.*"
```

**Validation:**
- [ ] Message "accepting connections"
- [ ] Version TimescaleDB affichée (ex: 2.13.0)
- [ ] Table `barag.sensor_data` existe

---

### Étape 5.4 : Tester l'Ingestion (Données Test)

**Objectif:** Insérer des données de test pour valider le système.

**Action:**
```bash
# Insérer une donnée test
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
INSERT INTO barag.sensor_data (time, station_id, temperature_air, temperature_water, salinity, ph)
VALUES (NOW(), 'BARAG', 22.5, 18.3, 35.2, 8.1);
"

# Vérifier l'insertion
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
  "SELECT * FROM barag.sensor_data ORDER BY time DESC LIMIT 5;"
```

**Validation:**
- [ ] Donnée insérée sans erreur
- [ ] Donnée visible dans la requête SELECT

---

### Étape 5.5 : Accéder à Grafana

**Objectif:** Vérifier que l'interface de monitoring est accessible.

**Action:**
1. Ouvrir un navigateur
2. Aller sur `http://VOTRE_IP_VPS:3000`
3. Connexion:
   - **Utilisateur:** `admin`
   - **Mot de passe:** (celui défini dans .env, variable `GRAFANA_PASSWORD`)

**Validation:**
- [ ] Page de connexion Grafana affichée
- [ ] Connexion réussie
- [ ] Dashboard vide (normal, pas encore configuré)

---

## ✅ PHASE 6 : CONFIGURATION DES BACKUPS

### Étape 6.1 : Installer le Script de Backup

**Objectif:** Configurer les backups automatiques quotidiens.

**Action:**
```bash
# Créer le répertoire de backups
mkdir -p ~/backups
chmod 700 ~/backups

# Créer le script de backup (copier depuis BACKUP_QUICK_REFERENCE.txt)
nano ~/backup-oceansentinel.sh
```

**Contenu du script** (voir `BACKUP_QUICK_REFERENCE.txt` pour le script complet)

**Rendre exécutable:**
```bash
chmod +x ~/backup-oceansentinel.sh
```

**Validation:**
```bash
# Tester le script
~/backup-oceansentinel.sh
```

- [ ] Backup créé sans erreur
- [ ] Fichier `.dump` présent dans `~/backups/`

---

### Étape 6.2 : Configurer le Cron

**Objectif:** Automatiser les backups quotidiens à 2h du matin.

**Action:**
```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne à la fin:
0 2 * * * ~/backup-oceansentinel.sh >> ~/backups/backup.log 2>&1

# Sauvegarder et quitter
```

**Validation:**
```bash
# Vérifier le cron
crontab -l | grep backup
```

- [ ] Ligne de cron affichée

---

## ✅ PHASE 7 : TEST DEPUIS WINDOWS

### Étape 7.1 : Installer les Dépendances Python (Windows)

**Objectif:** Préparer l'environnement Python pour se connecter depuis Windows.

**Action:**
```powershell
# Depuis le répertoire du projet
cd C:\Users\ktprt\Documents\OSwindsurf

# Installer les dépendances
pip install -r requirements.txt
```

**Validation:**
```powershell
# Vérifier l'installation
pip list | Select-String "psycopg2|pandas"
```

- [ ] `psycopg2-binary` installé
- [ ] `pandas` installé

---

### Étape 7.2 : Tester la Connexion depuis Windows

**Objectif:** Vérifier que vous pouvez interroger la base depuis votre PC.

**Action:**
```powershell
# Tester avec le script query.py
python scripts\query.py "SELECT COUNT(*) FROM barag.sensor_data"
```

**Validation:**
- [ ] Connexion réussie
- [ ] Résultat JSON affiché

**Si erreur de connexion:**
- Vérifier `DB_HOST` dans `.env` (doit être l'IP du VPS)
- Vérifier que le port 6543 est ouvert (UFW + Hostinger)
- Tester avec `telnet VOTRE_IP_VPS 6543`

---

## ✅ CHECKLIST FINALE

### Vérifications Système

- [ ] **VPS accessible** en SSH
- [ ] **Docker** installé et fonctionnel
- [ ] **UFW** actif avec 7+ règles
- [ ] **Fail2Ban** actif
- [ ] **Pare-feu Hostinger** configuré (7 ports ouverts)

### Vérifications Ocean Sentinel

- [ ] **7 conteneurs** actifs (docker compose ps)
- [ ] **TimescaleDB** healthy
- [ ] **Extension TimescaleDB** installée
- [ ] **Table sensor_data** créée
- [ ] **Données test** insérées et visibles
- [ ] **Grafana** accessible (http://IP:3000)
- [ ] **Backups** configurés (cron actif)

### Vérifications Connexion

- [ ] **Connexion depuis Windows** fonctionnelle (query.py)
- [ ] **Fichier .env Windows** avec `DB_HOST=IP_VPS`
- [ ] **Fichier .env VPS** avec `DB_HOST=localhost`

---

## 🎉 FÉLICITATIONS !

**Ocean Sentinel V3.0 est maintenant opérationnel !**

### Prochaines Étapes

1. **Télécharger des données COAST-HF** (voir `GUIDE_NETCDF_COAST_HF.md`)
2. **Ingérer des données réelles** avec `ingestion_stream.py`
3. **Entraîner les modèles ML** avec `ml_pipeline.py`
4. **Configurer les dashboards Grafana**
5. **Mettre en place les alertes** (email, webhook)

### Support

- **Documentation complète:** `OCEAN_SENTINEL_V3_README.md`
- **Constitution SACS:** `.windsurf/skills/project-context.md`
- **Guide NetCDF:** `GUIDE_NETCDF_COAST_HF.md`
- **Référence Backups:** `BACKUP_QUICK_REFERENCE.txt`

---

**🌊 Bon monitoring océanographique avec Ocean Sentinel V3.0 ! 🌊**
