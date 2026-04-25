# 🚀 QUICKSTART - Backend Ocean Sentinel

Guide de démarrage rapide pour lancer le backend en 5 minutes.

## ⚡ Installation rapide

```bash
# 1. Aller dans le dossier backend
cd backend/

# 2. Créer virtualenv Python
python -m venv venv

# 3. Activer virtualenv
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 4. Installer dépendances
pip install -r requirements.txt

# 5. Créer fichier .env
copy .env.example .env
# Ou sur Linux/Mac:
cp .env.example .env

# 6. Lancer serveur
python main.py
```

## ✅ Vérification

Le serveur devrait afficher :

```
INFO:     🌊 Ocean Sentinel API starting...
INFO:     CORS origins: ['https://oceansentinelle.fr', 'http://localhost:5173']
INFO:     COAST-HF API: https://coasthf.fr/api/v1
INFO:     Hub'Eau API: https://hubeau.eaufrance.fr/api/v1/qualite_eau_littoral
INFO:     ✅ Ocean Sentinel API ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🧪 Test rapide

Ouvrir un nouveau terminal :

```bash
# Test health check
curl http://localhost:8000/health

# Test liste stations
curl http://localhost:8000/api/v1/stations

# Test données station (va fallback sur mock si API externe down)
curl http://localhost:8000/api/v1/station/BARAG_PROXY/latest
```

## 📚 Documentation

Ouvrir dans le navigateur :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🔧 Configuration (optionnel)

Éditer `.env` pour personnaliser :

```env
# Si vous avez des clés API
COAST_HF_API_KEY=votre_cle_ici
HUB_EAU_API_KEY=votre_cle_ici

# Changer niveau logs
LOG_LEVEL=DEBUG

# Ajouter origins CORS
ALLOWED_ORIGINS=https://oceansentinelle.fr,http://localhost:5173,http://localhost:3000
```

## 🐛 Problèmes courants

### Erreur "No module named 'fastapi'"

```bash
# Vérifier virtualenv activé
which python  # Linux/Mac
where python  # Windows

# Réinstaller dépendances
pip install -r requirements.txt
```

### Port 8000 déjà utilisé

```bash
# Changer port dans main.py ligne finale
uvicorn.run("main:app", host="0.0.0.0", port=8001)
```

### Erreur CORS

Ajouter l'origin du frontend dans `.env` :

```env
ALLOWED_ORIGINS=http://localhost:5173
```

## 🎯 Prochaines étapes

1. Tester les endpoints dans Swagger UI
2. Connecter le frontend React
3. Vérifier les données affichées dans le Dashboard
4. Déployer sur VPS (voir README.md)

## 📞 Support

En cas de problème, vérifier :
- Logs dans le terminal
- Documentation : http://localhost:8000/docs
- README.md pour guide complet
