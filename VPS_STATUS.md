# Ocean Sentinel - Status VPS

## Informations VPS

**IP** : `76.13.43.3`  
**Provider** : Hostinger  
**Status** : ✅ **Accessible**

## Tests de Connexion

### ✅ Port SSH (22)
- **Status** : Ouvert
- **Test** : `Test-NetConnection -ComputerName 76.13.43.3 -Port 22`
- **Résultat** : `TcpTestSucceeded : True`

### ⚠️ Ping ICMP
- **Status** : Timeout (normal, ICMP souvent bloqué)
- **Impact** : Aucun, SSH fonctionne

### ✅ Port HTTP (80)
- **Status** : Ouvert et fonctionnel
- **Test** : `curl -I http://76.13.43.3`
- **Résultat** : `HTTP/1.1 200 OK` - Nginx 1.24.0
- **Validation** : 18 avril 2026 23:20 UTC

### ✅ Port HTTPS (443)
- **Status** : Ouvert (certificat SSL à configurer)
- **Test** : `curl -I https://76.13.43.3`
- **Résultat** : Port accessible, erreur SSL normale
- **Action requise** : Configurer Let's Encrypt

### ✅ Nginx
- **Version** : nginx/1.24.0 (Ubuntu)
- **Status** : Actif (PID: 603591)
- **Workers** : 3 processus
- **Ports** : 80, 443 en écoute sur 0.0.0.0

## Prochaines Étapes

### Option A - Déploiement Automatique (Recommandé)

**1 commande pour tout déployer** :

```powershell
.\deploy_to_vps.ps1
```

Ce script va :
1. ✅ Installer Docker sur le VPS
2. ✅ Cloner le repository
3. ✅ Générer mots de passe sécurisés
4. ✅ Configurer l'environnement
5. ✅ Déployer l'application
6. ✅ Valider le déploiement

**Durée estimée** : 3-5 minutes

---

### Option B - Déploiement Manuel

#### 1. Connexion SSH

```bash
ssh root@76.13.43.3
```

#### 2. Installation Docker

```bash
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin git curl jq
```

#### 3. Clonage Repository

```bash
mkdir -p /opt/oceansentinel
cd /opt/oceansentinel
git clone https://github.com/oceansentinelle/OS3.0.git .
```

#### 4. Configuration

```bash
cp .env.full.example .env
vim .env  # Éditer mots de passe
```

**Variables à modifier** :
- `POSTGRES_PASSWORD` : Générer avec `openssl rand -base64 32`
- `MINIO_ROOT_PASSWORD` : Générer avec `openssl rand -base64 32`
- `API_SECRET_KEY` : Générer avec `openssl rand -base64 64`

**Sources à activer** (commencer avec 2) :
```bash
ENABLE_ERDDAP_COAST_HF=true
ENABLE_HUBEAU=true
```

#### 5. Déploiement

```bash
chmod +x deploy.sh
./deploy.sh
```

#### 6. Validation

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Pipeline status
curl http://localhost:8000/api/v1/pipeline/status | jq

# Smoke tests
./scripts/smoke_tests.sh
```

---

## Endpoints Disponibles (après déploiement)

- **API Health** : http://76.13.43.3:8000/api/v1/health
- **Pipeline Status** : http://76.13.43.3:8000/api/v1/pipeline/status
- **API Docs** : http://76.13.43.3:8000/docs
- **MinIO Console** : http://76.13.43.3:9001

---

## Commandes Utiles

### Logs en Temps Réel

```bash
# Tous les services
docker compose -f docker-compose-full.yml logs -f

# Orchestrateur
docker compose -f docker-compose-full.yml logs -f orchestrator

# API
docker compose -f docker-compose-full.yml logs -f api
```

### Vérifier Données

```bash
# Ingestions récentes
docker exec os_postgres psql -U admin -d oceansentinel -c "
SELECT source_name, COUNT(*) 
FROM raw_ingestion_log 
WHERE fetched_at > NOW() - INTERVAL '1 hour' 
GROUP BY source_name;
"

# Mesures validées
docker exec os_postgres psql -U admin -d oceansentinel -c "
SELECT COUNT(*) FROM validated_measurements;
"
```

### Monitoring

```bash
# Status conteneurs
docker compose -f docker-compose-full.yml ps

# Stats ressources
docker stats

# Espace disque
df -h
```

---

## Fichiers Créés

- `.vps_ip` : IP du VPS sauvegardée
- `.vps_credentials` : Mots de passe générés (après déploiement auto)
- `check_vps.ps1` : Script de vérification connexion
- `deploy_to_vps.ps1` : Script de déploiement automatique

---

## Recommandation

**Utilisez le déploiement automatique** :

```powershell
.\deploy_to_vps.ps1
```

C'est le plus rapide et le plus sûr. Le script :
- Génère des mots de passe forts automatiquement
- Configure tout correctement
- Sauvegarde les credentials localement
- Valide le déploiement

**Temps total** : ~5 minutes
