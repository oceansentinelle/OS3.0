# 🚀 DÉPLOIEMENT VPS - Backend Ocean Sentinel

Guide complet pour déployer le backend FastAPI sur VPS Hostinger (76.13.43.3).

## ⚠️ IMPORTANT

**Python 3.11 requis** (pas 3.14) car Pydantic nécessite des wheels pré-compilés.

---

## 📋 ÉTAPE 1 : PRÉPARATION VPS

### Connexion SSH

```bash
ssh root@76.13.43.3
```

### Installation Python 3.11

```bash
# Update système
apt update && apt upgrade -y

# Installer Python 3.11
apt install -y python3.11 python3.11-venv python3.11-dev

# Vérifier version
python3.11 --version
# Doit afficher: Python 3.11.x
```

### Installer dépendances système

```bash
# Build tools (si nécessaire)
apt install -y build-essential gcc

# Nginx (si pas déjà installé)
apt install -y nginx

# Certbot pour SSL (si pas déjà installé)
apt install -y certbot python3-certbot-nginx
```

---

## 📦 ÉTAPE 2 : COPIER FICHIERS BACKEND

### Depuis votre machine locale

```bash
# Créer archive backend
cd C:\Users\ktprt\Documents\OSwindsurf\ocean-sentinel-v4
tar -czf backend.tar.gz backend/

# Copier sur VPS
scp backend.tar.gz root@76.13.43.3:/tmp/
```

### Sur le VPS

```bash
# Créer dossier application
mkdir -p /var/www/oceansentinel-api
cd /var/www/oceansentinel-api

# Extraire archive
tar -xzf /tmp/backend.tar.gz --strip-components=1

# Nettoyer
rm /tmp/backend.tar.gz
```

---

## 🐍 ÉTAPE 3 : INSTALLATION PYTHON

### Créer virtualenv

```bash
cd /var/www/oceansentinel-api

# Créer venv avec Python 3.11
python3.11 -m venv venv

# Activer venv
source venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip
```

### Installer dépendances

```bash
# Installer requirements
pip install -r requirements.txt

# Vérifier installation
python -c "import fastapi; print(fastapi.__version__)"
```

---

## ⚙️ ÉTAPE 4 : CONFIGURATION

### Créer fichier .env

```bash
cd /var/www/oceansentinel-api

# Copier exemple
cp .env.example .env

# Éditer configuration
nano .env
```

**Contenu `.env`** :

```env
# API Keys (laisser vide si pas nécessaire)
COAST_HF_API_KEY=
HUB_EAU_API_KEY=

# URLs API externes
COAST_HF_API_URL=https://coasthf.fr/api/v1
HUB_EAU_API_URL=https://hubeau.eaufrance.fr/api/v1/qualite_eau_littoral

# CORS Origins
ALLOWED_ORIGINS=https://oceansentinelle.fr,https://ocean-sentinelle.org

# Logs
LOG_LEVEL=INFO
```

Sauvegarder : `Ctrl+X`, `Y`, `Enter`

---

## 🔧 ÉTAPE 5 : SYSTEMD SERVICE

### Créer service systemd

```bash
nano /etc/systemd/system/oceansentinel-api.service
```

**Contenu** :

```ini
[Unit]
Description=Ocean Sentinel API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/oceansentinel-api
Environment="PATH=/var/www/oceansentinel-api/venv/bin"
ExecStart=/var/www/oceansentinel-api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Sauvegarder : `Ctrl+X`, `Y`, `Enter`

### Configurer permissions

```bash
# Changer propriétaire
chown -R www-data:www-data /var/www/oceansentinel-api

# Permissions
chmod -R 755 /var/www/oceansentinel-api
```

### Activer et démarrer service

```bash
# Recharger systemd
systemctl daemon-reload

# Activer au démarrage
systemctl enable oceansentinel-api

# Démarrer service
systemctl start oceansentinel-api

# Vérifier statut
systemctl status oceansentinel-api
```

**Résultat attendu** :

```
● oceansentinel-api.service - Ocean Sentinel API
   Loaded: loaded (/etc/systemd/system/oceansentinel-api.service; enabled)
   Active: active (running) since Thu 2026-04-24 22:40:00 UTC
```

---

## 🌐 ÉTAPE 6 : NGINX REVERSE PROXY

### Éditer configuration Nginx

```bash
nano /etc/nginx/sites-available/oceansentinelle.fr
```

**Ajouter dans le bloc `server`** :

```nginx
# API Backend
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # Buffers
    proxy_buffering off;
}

# Health check
location /health {
    proxy_pass http://127.0.0.1:8000/health;
    proxy_set_header Host $host;
}

# API Docs (optionnel, à sécuriser en production)
location /docs {
    proxy_pass http://127.0.0.1:8000/docs;
    proxy_set_header Host $host;
}
```

### Tester et recharger Nginx

```bash
# Tester configuration
nginx -t

# Recharger Nginx
systemctl reload nginx
```

---

## ✅ ÉTAPE 7 : TESTS

### Test local (sur VPS)

```bash
# Test health check
curl http://127.0.0.1:8000/health

# Test liste stations
curl http://127.0.0.1:8000/api/v1/stations

# Test données station
curl http://127.0.0.1:8000/api/v1/station/BARAG_PROXY/latest
```

### Test public (depuis votre machine)

```bash
# Test health check
curl https://oceansentinelle.fr/health

# Test API
curl https://oceansentinelle.fr/api/v1/station/BARAG_PROXY/latest | jq '.'
```

**Résultat attendu** :

```json
{
  "station_id": "BARAG_PROXY",
  "timestamp": "2026-04-24T22:45:00Z",
  "parameters": [
    {
      "name": "TEMP",
      "value": 18.5,
      "unit": "°C",
      "status": "measured",
      "source": "COAST-HF Ifremer",
      "timestamp": "2026-04-24T22:45:00Z",
      "quality_score": 0.95,
      "is_critical": false
    }
  ]
}
```

---

## 📊 ÉTAPE 8 : MONITORING

### Logs systemd

```bash
# Voir logs en temps réel
journalctl -u oceansentinel-api -f

# Voir dernières 100 lignes
journalctl -u oceansentinel-api -n 100

# Logs depuis aujourd'hui
journalctl -u oceansentinel-api --since today
```

### Logs application

```bash
# Si logs dans fichier (à configurer)
tail -f /var/log/oceansentinel-api.log
```

### Commandes utiles

```bash
# Redémarrer service
systemctl restart oceansentinel-api

# Arrêter service
systemctl stop oceansentinel-api

# Statut service
systemctl status oceansentinel-api

# Recharger config (sans redémarrer)
systemctl reload oceansentinel-api
```

---

## 🔒 ÉTAPE 9 : SÉCURITÉ

### Firewall UFW

```bash
# Vérifier UFW actif
ufw status

# Autoriser HTTP/HTTPS (si pas déjà fait)
ufw allow 80/tcp
ufw allow 443/tcp

# NE PAS exposer port 8000 directement
# (déjà accessible via Nginx reverse proxy)
```

### SSL/TLS

```bash
# Si pas déjà configuré, obtenir certificat Let's Encrypt
certbot --nginx -d oceansentinelle.fr -d www.oceansentinelle.fr

# Renouvellement automatique (cron)
certbot renew --dry-run
```

---

## 🐛 TROUBLESHOOTING

### Service ne démarre pas

```bash
# Vérifier logs
journalctl -u oceansentinel-api -n 50

# Vérifier permissions
ls -la /var/www/oceansentinel-api

# Tester manuellement
cd /var/www/oceansentinel-api
source venv/bin/activate
python main.py
```

### Erreur "Module not found"

```bash
# Réinstaller dépendances
cd /var/www/oceansentinel-api
source venv/bin/activate
pip install -r requirements.txt
```

### Erreur CORS

Vérifier `.env` contient les bonnes origins :

```env
ALLOWED_ORIGINS=https://oceansentinelle.fr,https://ocean-sentinelle.org
```

Redémarrer service :

```bash
systemctl restart oceansentinel-api
```

### Port 8000 déjà utilisé

```bash
# Trouver processus
lsof -i :8000

# Tuer processus
kill -9 <PID>

# Redémarrer service
systemctl restart oceansentinel-api
```

---

## 📈 ÉTAPE 10 : MISE À JOUR

### Déployer nouvelle version

```bash
# Sur votre machine locale
cd C:\Users\ktprt\Documents\OSwindsurf\ocean-sentinel-v4
tar -czf backend.tar.gz backend/
scp backend.tar.gz root@76.13.43.3:/tmp/

# Sur le VPS
systemctl stop oceansentinel-api
cd /var/www/oceansentinel-api
tar -xzf /tmp/backend.tar.gz --strip-components=1
source venv/bin/activate
pip install -r requirements.txt
systemctl start oceansentinel-api
systemctl status oceansentinel-api
```

---

## ✅ VALIDATION FINALE

**Checklist** :

- [ ] Service systemd actif : `systemctl status oceansentinel-api`
- [ ] Health check OK : `curl https://oceansentinelle.fr/health`
- [ ] API répond : `curl https://oceansentinelle.fr/api/v1/stations`
- [ ] Logs propres : `journalctl -u oceansentinel-api -n 20`
- [ ] Frontend connecté : Dashboard affiche données réelles
- [ ] SSL actif : `https://` fonctionne
- [ ] CORS configuré : Pas d'erreur dans console navigateur

---

## 🎉 DÉPLOIEMENT RÉUSSI !

**Backend Ocean Sentinel opérationnel sur VPS Hostinger !**

**URLs** :
- API : https://oceansentinelle.fr/api/v1/
- Health : https://oceansentinelle.fr/health
- Docs : https://oceansentinelle.fr/docs (si activé)

**Prochaines étapes** :
1. Tester frontend avec données réelles
2. Monitorer logs pendant 24h
3. Configurer alertes uptime
4. Implémenter cache Redis (optionnel)
5. Ajouter tests automatisés
