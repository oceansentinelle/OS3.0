# 🌊 Ocean Sentinel V3.0 - Accès et Configuration Finale

**Date** : 18 avril 2026, 03:28 UTC+2  
**VPS** : 76.13.43.3 (Hostinger)  
**Status** : Backend opérationnel, Firewall à configurer

---

## ✅ Ce Qui Fonctionne

### API REST (Port 8000)
✅ **Accessible** : http://76.13.43.3:8000

**Endpoints disponibles** :
- Health : http://76.13.43.3:8000/api/v1/health
- Documentation : http://76.13.43.3:8000/docs
- Root : http://76.13.43.3:8000/

**Test PowerShell** :
```powershell
Invoke-RestMethod -Uri "http://76.13.43.3:8000/api/v1/health"
```

### Backend Services
✅ PostgreSQL/TimescaleDB (Port 5432)  
✅ Redis (Port 6379)  
✅ MinIO (Ports 9000-9001)  
✅ Orchestrateur (2 jobs actifs)  
✅ Workers (3 placeholders)

---

## ❌ Problème Actuel : Firewall Hostinger

### Symptôme
- Port 80 (HTTP) : ❌ Timeout
- Port 8080 (HTTP alternatif) : ❌ Timeout
- Port 8000 (API) : ✅ Fonctionne

### Cause
Le firewall Hostinger bloque les ports 80 et 8080.

### Solution : Configurer le Firewall Hostinger

#### Étapes dans le Panel Hostinger

1. **Connexion**
   - URL : https://hpanel.hostinger.com
   - Connectez-vous avec vos identifiants

2. **Navigation**
   - Cliquez sur **"VPS"** dans le menu principal
   - Sélectionnez votre VPS (76.13.43.3)

3. **Firewall**
   - Cherchez dans le menu latéral :
     - **"Firewall"** OU
     - **"Security"** OU
     - **"Network Settings"** OU
     - **"Advanced"** → **"Firewall"**

4. **Ajouter Règles**
   
   **Règle 1 - HTTP (Port 80)** :
   - Port : `80`
   - Protocol : `TCP`
   - Action : `Allow` / `Autoriser`
   - Source : `0.0.0.0/0` (Anywhere)
   - Description : `HTTP Web Server`
   
   **Règle 2 - HTTPS (Port 443)** :
   - Port : `443`
   - Protocol : `TCP`
   - Action : `Allow`
   - Source : `0.0.0.0/0`
   - Description : `HTTPS Secure Web`
   
   **Règle 3 - HTTP Alternatif (Port 8080)** :
   - Port : `8080`
   - Protocol : `TCP`
   - Action : `Allow`
   - Source : `0.0.0.0/0`
   - Description : `HTTP Alternative`

5. **Sauvegarder**
   - Cliquez sur **"Save"** / **"Enregistrer"**
   - Attendez 1-2 minutes pour la propagation

---

## 🌐 URLs Après Configuration Firewall

### Site Web Principal
- **Accueil** : http://76.13.43.3/
- **Le Projet** : http://76.13.43.3/about.html
- **API & Alertes** : http://76.13.43.3/api.html

### API REST
- **Health** : http://76.13.43.3:8000/api/v1/health
- **Documentation** : http://76.13.43.3:8000/docs

### Alternative (Port 8080)
Si le port 80 ne fonctionne pas :
- http://76.13.43.3:8080/

---

## 🔧 Configuration Actuelle VPS

### Firewall UFW (Linux)
```
Status: active

Ports ouverts :
- 22/tcp (SSH)
- 80/tcp (HTTP) ✅
- 443/tcp (HTTPS) ✅
- 3000/tcp (Grafana)
- 6543/tcp
- 8000/tcp (API) ✅
- 8080/tcp (HTTP Alt) ✅
```

### Nginx
```
Écoute sur :
- Port 80 → /opt/oceansentinel/public
- Port 8080 → /opt/oceansentinel/public

Proxy :
- /api/ → http://localhost:8000
- /docs → http://localhost:8000
```

### Services Docker
```
os_api                ✅ Healthy (Port 8000)
os_postgres           ✅ Healthy (Port 5432)
os_redis              ✅ Healthy (Port 6379)
os_minio              ✅ Healthy (Ports 9000-9001)
os_orchestrator       ✅ Running (2 jobs)
os_ingest_worker      ✅ Running
os_transform_worker   ✅ Running
os_alert_worker       ✅ Running
```

---

## 📊 Jobs Planifiés

### Actifs
1. **ERDDAP COAST-HF** : Toutes les heures
2. **Hub'Eau** : Toutes les 6 heures

### Désactivés
- ERDDAP SOMLIT
- SEANOE Loader
- SIBA Enki
- SHOM Reference
- INSEE Geo
- INSEE Sirene

---

## 🔐 Credentials

**Emplacement** : `/root/.oceansentinel_credentials` sur le VPS

**Récupération** :
```bash
ssh root@76.13.43.3 'cat /root/.oceansentinel_credentials'
```

---

## 📞 Support et Documentation

### Repository GitHub
https://github.com/oceansentinelle/OS3.0

### Documentation Déploiement
- `DEPLOYMENT_GUIDE_VPS.md` - Guide complet
- `DEPLOYMENT_SUCCESS_VPS.md` - Rapport de succès
- `DEPLOIEMENT_RAPIDE.md` - Guide rapide

### Commandes Utiles

**SSH** :
```bash
ssh root@76.13.43.3
```

**Logs** :
```bash
docker compose -f docker-compose-full.yml logs -f orchestrator
docker compose -f docker-compose-full.yml logs -f api
```

**Status** :
```bash
docker compose -f docker-compose-full.yml ps
systemctl status nginx
ufw status
```

**Redémarrer** :
```bash
docker compose -f docker-compose-full.yml restart
systemctl restart nginx
```

---

## ⚡ Action Immédiate Requise

### 🔥 PRIORITÉ 1 : Configurer Firewall Hostinger

**Sans cette étape, le site web ne sera PAS accessible publiquement.**

1. Allez sur https://hpanel.hostinger.com
2. VPS → Firewall
3. Ajoutez les ports 80, 443, 8080
4. Sauvegardez

**Durée estimée** : 5 minutes

---

## ✅ Checklist Finale

- [x] Backend déployé
- [x] API fonctionnelle (port 8000)
- [x] Base de données initialisée
- [x] Orchestrateur actif
- [x] Site web créé
- [x] Nginx configuré
- [x] Firewall UFW configuré
- [ ] **Firewall Hostinger configuré** ← ACTION REQUISE
- [ ] Site web accessible publiquement
- [ ] Tests utilisateur finaux

---

**Une fois le firewall Hostinger configuré, Ocean Sentinel V3.0 sera 100% opérationnel et accessible au public !** 🌊🚀
