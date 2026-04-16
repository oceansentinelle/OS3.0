# 🚀 Instructions de Déploiement Ocean Sentinel

## PHASE 1 : Préparation Git (Windows)

### 1. Initialiser Git localement
```powershell
cd C:\Users\ktprt\Documents\OSwindsurf
git init
git add .
git commit -m "Initial commit - Ocean Sentinel TimescaleDB"
```

### 2. Créer un dépôt GitHub privé

**Option A : Via GitHub CLI (si installé)**
```powershell
gh repo create oceansentinel-db --private --source=. --remote=origin --push
```

**Option B : Via l'interface web GitHub**
1. Allez sur https://github.com/new
2. Nom du dépôt : `oceansentinel-db`
3. Visibilité : **Private** ✅
4. Ne pas initialiser avec README/gitignore
5. Cliquez sur "Create repository"

Puis dans PowerShell :
```powershell
git remote add origin https://github.com/VOTRE_USERNAME/oceansentinel-db.git
git branch -M main
git push -u origin main
```

---

## PHASE 2 : Déploiement VPS (Ubuntu)

### 1. Installation de Docker (sur le VPS)
```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation de Docker Compose
sudo apt install docker-compose-plugin -y

# Vérification
docker --version
docker compose version

# Démarrer Docker au boot
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Cloner le dépôt
```bash
# Installer Git si nécessaire
sudo apt install git -y

# Cloner le dépôt (remplacez VOTRE_USERNAME)
cd ~
git clone https://github.com/VOTRE_USERNAME/oceansentinel-db.git oceansentinel
cd oceansentinel
```

### 3. Configuration de l'environnement
```bash
# Copier le template
cp .env.example .env

# Générer un mot de passe fort
openssl rand -base64 32

# Éditer le fichier .env
nano .env
# Remplacez POSTGRES_PASSWORD par le mot de passe généré
# Ctrl+X, puis Y, puis Entrée pour sauvegarder
```

### 4. Créer le répertoire de données
```bash
sudo mkdir -p /opt/oceansentinel/data
sudo chown -R 999:999 /opt/oceansentinel/data
sudo chmod 700 /opt/oceansentinel/data
```

### 5. Configuration du pare-feu
```bash
# UFW
sudo ufw allow 22/tcp
sudo ufw allow 6543/tcp
sudo ufw enable

# Vérifier
sudo ufw status
```

### 6. Lancer TimescaleDB
```bash
cd ~/oceansentinel
docker compose up -d

# Voir les logs
docker compose logs -f timescaledb
```

### 7. Tuning (optionnel mais recommandé)
```bash
chmod +x scripts/*.sh
./scripts/tune-timescaledb.sh
```

### 8. Vérification de santé
```bash
./scripts/health-check.sh
```

---

## 🔐 Configuration Pare-feu Hostinger (Panel Web)

1. Connectez-vous au panel Hostinger
2. VPS → Pare-feu
3. Ajouter une règle :
   - Port : **6543**
   - Protocole : **TCP**
   - Source : **0.0.0.0/0** (ou votre IP fixe)
   - Action : **Autoriser**

---

## ✅ Test de Connexion

Depuis votre PC Windows :
```powershell
# Installer psql si nécessaire (via PostgreSQL client)
# Ou utiliser DBeaver, pgAdmin, etc.

psql -h VOTRE_IP_VPS -p 6543 -U oceansentinel -d oceansentinelle
```

---

## 📝 Mots de Passe à Changer

Après le premier déploiement, changez les mots de passe par défaut :

```sql
-- Se connecter à la base
\c oceansentinelle

-- Changer le mot de passe readonly
ALTER ROLE oceansentinel_readonly WITH PASSWORD 'NOUVEAU_MOT_DE_PASSE_FORT_1';

-- Changer le mot de passe writer
ALTER ROLE oceansentinel_writer WITH PASSWORD 'NOUVEAU_MOT_DE_PASSE_FORT_2';
```

---

## 🔄 Mises à Jour Futures

```bash
cd ~/oceansentinel
git pull
docker compose down
docker compose up -d
```
