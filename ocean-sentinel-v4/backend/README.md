# 🌊 Ocean Sentinel Backend API

Backend FastAPI pour agrégation données océanographiques temps réel.

## 📋 Architecture

```
Frontend (React)
  └─ fetch('/api/v1/station/{id}/latest')
       ↓
Backend (FastAPI - Ce serveur)
  └─ GET /api/v1/station/{station_id}/latest
       ├─ Fetch COAST-HF API (Ifremer)
       ├─ Fetch Hub'Eau API (BRGM)
       ├─ Transformation données
       └─ Return JSON format Ocean Sentinel
```

## 🚀 Installation

### Prérequis
- Python 3.11+
- pip

### Installation locale

```bash
# Créer virtualenv
python -m venv venv

# Activer virtualenv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Copier configuration
cp .env.example .env

# Éditer .env avec vos clés API (si nécessaire)
nano .env
```

## 🔧 Configuration

Fichier `.env` :

```env
# API Keys (si nécessaire)
COAST_HF_API_KEY=
HUB_EAU_API_KEY=

# URLs API externes
COAST_HF_API_URL=https://coasthf.fr/api/v1
HUB_EAU_API_URL=https://hubeau.eaufrance.fr/api/v1/qualite_eau_littoral

# CORS Origins
ALLOWED_ORIGINS=https://oceansentinelle.fr,http://localhost:5173

# Logs
LOG_LEVEL=INFO
```

## 🏃 Lancement

### Développement local

```bash
# Lancer serveur avec auto-reload
python main.py

# Ou avec uvicorn directement
uvicorn main:app --reload --port 8000
```

API disponible sur : http://localhost:8000

### Production

```bash
# Lancer avec Gunicorn + Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 Documentation API

Une fois le serveur lancé :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI JSON** : http://localhost:8000/openapi.json

## 🔌 Endpoints

### GET /api/v1/station/{station_id}/latest

Récupère les dernières données d'une station.

**Stations disponibles** :
- `BARAG_PROXY` - Bouée COAST-HF Bassin d'Arcachon
- `ARCACHON_EYRAC` - Station Hub'Eau Arcachon Eyrac

**Exemple** :
```bash
curl http://localhost:8000/api/v1/station/BARAG_PROXY/latest
```

**Réponse** :
```json
{
  "station_id": "BARAG_PROXY",
  "timestamp": "2026-04-24T22:30:00Z",
  "parameters": [
    {
      "name": "TEMP",
      "value": 18.5,
      "unit": "°C",
      "status": "measured",
      "source": "COAST-HF Ifremer",
      "timestamp": "2026-04-24T22:30:00Z",
      "quality_score": 0.95,
      "is_critical": false
    },
    {
      "name": "DOX2",
      "value": 135.0,
      "unit": "µmol/kg",
      "status": "measured",
      "source": "COAST-HF Ifremer",
      "timestamp": "2026-04-24T22:30:00Z",
      "quality_score": 0.88,
      "is_critical": true
    }
  ]
}
```

### GET /api/v1/stations

Liste toutes les stations disponibles.

### GET /health

Health check du service.

## 🧪 Tests

```bash
# Test endpoint local
curl http://localhost:8000/api/v1/station/BARAG_PROXY/latest | jq '.'

# Test health check
curl http://localhost:8000/health | jq '.'

# Test liste stations
curl http://localhost:8000/api/v1/stations | jq '.'
```

## 🚀 Déploiement VPS

### 1. Copier fichiers sur VPS

```bash
scp -r backend/* root@76.13.43.3:/var/www/oceansentinel-api/
```

### 2. Installer sur VPS

```bash
ssh root@76.13.43.3

cd /var/www/oceansentinel-api

# Créer virtualenv
python3.11 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
nano .env
```

### 3. Configurer systemd

```bash
nano /etc/systemd/system/oceansentinel-api.service
```

```ini
[Unit]
Description=Ocean Sentinel API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/oceansentinel-api
Environment="PATH=/var/www/oceansentinel-api/venv/bin"
ExecStart=/var/www/oceansentinel-api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer service
systemctl enable oceansentinel-api
systemctl start oceansentinel-api
systemctl status oceansentinel-api
```

### 4. Configurer Nginx

```bash
nano /etc/nginx/sites-available/oceansentinelle.fr
```

Ajouter :

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

```bash
# Tester config Nginx
nginx -t

# Recharger Nginx
systemctl reload nginx
```

### 5. Tester en production

```bash
curl https://oceansentinelle.fr/api/v1/station/BARAG_PROXY/latest | jq '.'
```

## 📊 Monitoring

### Logs

```bash
# Logs systemd
journalctl -u oceansentinel-api -f

# Logs application
tail -f /var/log/oceansentinel-api.log
```

### Métriques

- **Health check** : https://oceansentinelle.fr/health
- **Uptime** : Monitorer avec UptimeRobot ou Pingdom

## 🔒 Sécurité

- ✅ CORS configuré (origins limitées)
- ✅ HTTPS obligatoire en production
- ✅ Clés API stockées dans .env (gitignored)
- ✅ Rate limiting (à implémenter avec slowapi)
- ✅ Logs sécurisés (pas de secrets)

## 🐛 Troubleshooting

### Erreur CORS

Vérifier `ALLOWED_ORIGINS` dans `.env` contient l'origin du frontend.

### Timeout API externe

Augmenter `HTTP_TIMEOUT` dans `.env`.

### Erreur 404 station

Vérifier `station_id` dans `STATION_CONFIG` (routers/stations.py).

## 📝 TODO

- [ ] Implémenter cache Redis (5 min TTL)
- [ ] Ajouter rate limiting (slowapi)
- [ ] Implémenter retry avec exponential backoff
- [ ] Ajouter tests unitaires (pytest)
- [ ] Connecter TimescaleDB pour historique
- [ ] Ajouter endpoint `/api/v1/station/{id}/history`
- [ ] Implémenter WebSocket pour données temps réel
- [ ] Ajouter métriques Prometheus

## 📄 Licence

MIT - Ocean Sentinel 2026
