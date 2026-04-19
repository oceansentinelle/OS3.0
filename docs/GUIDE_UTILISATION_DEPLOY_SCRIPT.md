# Guide d'Utilisation - Script de Déploiement Automatisé

## 📋 Vue d'Ensemble

Le script `deploy-sentinel.ps1` orchestre le déploiement complet de la plateforme Ocean Sentinel sur le VPS Hostinger en **5 phases automatisées**.

**Conformité** : ABACODE 2.0 (Stabilité > Sécurité > Clarté)  
**Durée estimée** : 5-10 minutes  
**Prérequis** : Windows 10/11 avec PowerShell 5.1+

---

## 🎯 Architecture du Script

### Gouvernance ABACODE 2.0

```
┌─────────────────────────────────────────────────────────────┐
│                    PRIORITÉ HIÉRARCHIQUE                     │
├─────────────────────────────────────────────────────────────┤
│  1. STABILITÉ   → Services opérationnels 24/7              │
│  2. SÉCURITÉ    → Anti-UFW bypass, secrets chiffrés        │
│  3. CLARTÉ      → Logs structurés, traçabilité Git         │
└─────────────────────────────────────────────────────────────┘
```

### 5 Phases d'Exécution

```
Phase 1: VALIDATION
  ├─ Prérequis locaux (Git, SSH, SCP)
  ├─ Vérification .env.production
  ├─ Test connectivité réseau
  └─ Récupération commit Git

Phase 2: PROVISIONING
  ├─ Installation Docker/Compose
  ├─ Création structure répertoires
  └─ Configuration UFW

Phase 3: DÉPLOIEMENT
  ├─ Génération docker-compose.prod.yml
  ├─ Transfert fichiers (SCP sécurisé)
  ├─ Build conteneurs
  └─ Démarrage services

Phase 4: POST-INSTALLATION
  ├─ Installation pgvector
  ├─ Configuration Nginx + SSL
  ├─ Obtention certificat Let's Encrypt
  └─ Tests de santé API

Phase 5: RAPPORT
  ├─ Audit accessibilité (axe-core)
  ├─ Génération rapport Sandwich
  └─ Logs structurés
```

---

## 🚀 Utilisation

### Préparation (À faire UNE SEULE FOIS)

#### 1. Créer le Fichier `.env.production`

```powershell
# Dans C:\Users\ktprt\Documents\OSwindsurf\
New-Item -ItemType File -Path .env.production
```

**Contenu minimal requis** :

```bash
# Database
POSTGRES_PASSWORD=<GÉNÉRER_AVEC_openssl_rand_-base64_32>
POSTGRES_DB=oceansentinel
POSTGRES_USER=oceansentinel

# JWT
API_JWT_SECRET=<GÉNÉRER_AVEC_openssl_rand_-base64_64>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe
STRIPE_SECRET_KEY=sk_live_VOTRE_CLE_STRIPE
STRIPE_WEBHOOK_SECRET=whsec_VOTRE_SECRET_WEBHOOK

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@oceansentinel.fr
SMTP_PASSWORD=VOTRE_MOT_DE_PASSE
ADMIN_EMAIL=admin@oceansentinel.fr

# Application
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=oceansentinel.fr,www.oceansentinel.fr,76.13.43.3
CORS_ORIGINS=https://oceansentinel.fr,https://www.oceansentinel.fr

# Worker Stripe
WORKER_POLL_INTERVAL=5
MAX_RETRY_COUNT=3
BATCH_SIZE=10
DLQ_ALERT_THRESHOLD=10

# Database URL (généré automatiquement)
DATABASE_URL=postgresql+asyncpg://oceansentinel:${POSTGRES_PASSWORD}@postgres:5432/oceansentinel
```

#### 2. Générer les Secrets

**Sur Windows (PowerShell)** :

```powershell
# POSTGRES_PASSWORD (32 bytes base64)
$bytes = New-Object byte[] 32
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
$postgresPassword = [Convert]::ToBase64String($bytes)
Write-Host "POSTGRES_PASSWORD=$postgresPassword"

# API_JWT_SECRET (64 bytes base64)
$bytes = New-Object byte[] 64
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
$jwtSecret = [Convert]::ToBase64String($bytes)
Write-Host "API_JWT_SECRET=$jwtSecret"
```

**Sur Linux/WSL** :

```bash
# POSTGRES_PASSWORD
openssl rand -base64 32

# API_JWT_SECRET
openssl rand -base64 64
```

#### 3. Configurer SSH (Si pas déjà fait)

```powershell
# Générer une clé SSH (si nécessaire)
ssh-keygen -t rsa -b 4096 -C "deploy@oceansentinel.fr"

# Copier la clé publique sur le VPS
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh root@76.13.43.3 "cat >> ~/.ssh/authorized_keys"

# Tester la connexion
ssh root@76.13.43.3 "echo 'SSH OK'"
```

---

### Exécution du Script

#### Mode Standard (Recommandé)

```powershell
cd C:\Users\ktprt\Documents\OSwindsurf

# Exécuter le script
.\deploy-sentinel.ps1
```

**Résultat attendu** :

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           OCEAN SENTINEL - DÉPLOIEMENT AUTOMATISÉ        ║
║                                                           ║
║   Gouvernance: ABACODE 2.0                               ║
║   Priorité: Stabilité > Sécurité > Clarté                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

ℹ️  Démarrage du déploiement Ocean Sentinel
ℹ️  VPS cible: 76.13.43.3 (srv1341436.hstgr.cloud)
ℹ️  Domaine: oceansentinel.fr

========================================
PHASE 1 - VALIDATION
========================================

✅ Prérequis locaux validés
✅ Fichier .env.production validé
✅ Connexion SSH réussie
ℹ️  Déploiement du commit a3f7b2c (main)

========================================
PHASE 2 - PROVISIONING
========================================

✅ Docker déjà installé: Docker version 24.0.7
✅ Docker Compose déjà installé: v2.23.0
✅ Structure de répertoires créée
✅ UFW configuré

========================================
PHASE 3 - DÉPLOIEMENT
========================================

✅ docker-compose.prod.yml créé
ℹ️  Transfert du backend...
ℹ️  Transfert de docker-compose.prod.yml...
ℹ️  Transfert de .env.production (sécurisé)...
✅ Fichiers transférés avec succès
✅ Conteneurs démarrés avec succès

========================================
PHASE 4 - POST-INSTALLATION
========================================

✅ Extension pgvector installée
✅ Nginx configuré
✅ Certificat SSL obtenu avec succès
✅ API opérationnelle

========================================
PHASE 5 - RAPPORT ET AUDIT
========================================

✅ Rapport d'accessibilité généré
✅ Rapport sauvegardé: .\logs\deployment-report-20260419-013500.txt

═══════════════════════════════════════════════════════════
✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS
✅ Durée totale: 08:42
═══════════════════════════════════════════════════════════
```

#### Mode Développement (Sans SSL)

```powershell
.\deploy-sentinel.ps1 -SkipSSL
```

**Usage** : Pour tester le déploiement sans configurer Let's Encrypt.

#### Mode Simulation (Dry Run)

```powershell
.\deploy-sentinel.ps1 -DryRun
```

**Usage** : Simuler le déploiement sans exécuter les commandes SSH.

#### Mode Sans Validation

```powershell
.\deploy-sentinel.ps1 -SkipValidation
```

**⚠️ Déconseillé** : Ignore la phase de validation (risque d'échec).

---

## 🔒 Sécurité - Anti-UFW Bypass

### Problème Docker + UFW

Par défaut, Docker **contourne UFW** en modifiant directement les règles iptables.

```
Internet → [UFW] → [iptables] → [Docker]
                      ↑ Docker écrit ici directement
```

### Solution Implémentée

Le script configure **tous les ports internes** sur `127.0.0.1` uniquement :

```yaml
services:
  postgres:
    ports:
      - "127.0.0.1:5432:5432"  # ✅ Localhost uniquement
  
  api:
    ports:
      - "127.0.0.1:8000:8000"  # ✅ Localhost uniquement
```

**Résultat** :
- Seul **Nginx** (port 80/443) est exposé publiquement
- Tous les services internes sont **inaccessibles depuis l'extérieur**
- Le trafic **doit passer par Nginx** (reverse proxy)

### Vérification

```bash
# Sur le VPS
netstat -tlnp | grep -E ':(5432|8000|6379)'

# Résultat attendu:
# tcp  0  0 127.0.0.1:5432  0.0.0.0:*  LISTEN  postgres
# tcp  0  0 127.0.0.1:8000  0.0.0.0:*  LISTEN  api
# tcp  0  0 127.0.0.1:6379  0.0.0.0:*  LISTEN  redis

# ✅ Tous sur 127.0.0.1 (pas 0.0.0.0)
```

---

## 🗄️ Base de Données - pgvector pour RAG

### Extension pgvector

Le script installe automatiquement l'extension **pgvector** pour supporter les embeddings vectoriels (RAG).

```sql
-- Exécuté automatiquement
CREATE EXTENSION IF NOT EXISTS vector;

-- Table documents avec vecteurs
CREATE TABLE embeddings (
  id UUID PRIMARY KEY,
  document_id UUID,
  embedding vector(384),  -- Dimension 384 (all-MiniLM-L6-v2)
  chunk_text TEXT
);

-- Index HNSW pour recherche rapide (O(log n))
CREATE INDEX idx_embeddings_hnsw ON embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### Vérification

```bash
# Sur le VPS
docker exec oceansentinel_postgres psql -U oceansentinel -d oceansentinel -c '\dx'

# Résultat attendu:
#   Name   | Version |   Schema   |         Description
# ---------+---------+------------+------------------------------
#  vector  | 0.5.1   | public     | vector data type and ivfflat
```

---

## 🔐 Certificats SSL - Let's Encrypt

### Obtention Automatique

Le script utilise **Certbot** en mode `--nginx` pour :

1. Obtenir un certificat SSL valide
2. Configurer Nginx automatiquement
3. Activer la redirection HTTP → HTTPS

```bash
certbot --nginx \
  -d oceansentinel.fr \
  -d www.oceansentinel.fr \
  --non-interactive \
  --agree-tos \
  --email admin@oceansentinel.fr \
  --redirect
```

### Renouvellement Automatique

Certbot installe un **cron job** automatique :

```bash
# Vérifier le timer systemd
systemctl list-timers | grep certbot

# Résultat:
# certbot.timer  ... left  ...  certbot.service
```

### Vérification Manuelle

```bash
# Tester le renouvellement
certbot renew --dry-run

# Vérifier le certificat
openssl s_client -connect oceansentinel.fr:443 -servername oceansentinel.fr < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## 💳 Stripe Webhooks & Dead Letter Queue

### Architecture Worker

Le script déploie **2 réplicas** du worker Stripe avec DLQ :

```yaml
stripe-worker:
  deploy:
    replicas: 2  # Redondance
    resources:
      limits:
        memory: 512MB
```

### Flux de Traitement

```
1. Stripe → /api/webhooks/stripe (< 1s)
   ↓ Validation signature
   
2. Écriture en queue (< 1s)
   ↓ Idempotence via stripe_event_id
   
3. HTTP 200 → Stripe
   ↓ Stripe considère l'événement reçu
   
4. Worker poll (5s)
   ↓ Batch de 10 événements
   
5. Traitement
   ↓ Retry 3x si échec
   
6. DLQ si 3 échecs
   ↓ Alerte admin
```

### Monitoring DLQ

```bash
# Vérifier les événements en échec
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://oceansentinel.fr/api/admin/stripe/failed-events

# Logs du worker
docker logs -f oceansentinel_stripe_worker
```

---

## ♿ Audit d'Accessibilité WCAG 2.2

### Exécution Automatique

Si **npm** et **@axe-core/cli** sont installés, le script exécute un audit automatique :

```powershell
# Installation (si nécessaire)
npm install -g @axe-core/cli

# Exécuté par le script
axe https://oceansentinel.fr --save .\logs\accessibility-audit.json
```

### Rapport Généré

```json
{
  "violations": [
    {
      "id": "color-contrast",
      "impact": "serious",
      "description": "Ensures the contrast between foreground and background colors meets WCAG 2 AA contrast ratio thresholds",
      "nodes": [...]
    }
  ],
  "passes": [...],
  "incomplete": [...]
}
```

### Critères Validés

- ✅ Contraste minimum 4.5:1 (texte)
- ✅ Labels ARIA complets
- ✅ Navigation clavier
- ✅ Structure sémantique HTML5
- ✅ Messages d'erreur accessibles

---

## 📊 Logs et Traçabilité

### Structure des Logs

Chaque entrée de log contient :

```
[2026-04-19 01:35:42] [SUCCESS] [commit:a3f7b2c] Conteneurs démarrés avec succès
 ↑ Timestamp         ↑ Niveau    ↑ Commit Git  ↑ Message
```

### Fichiers Générés

```
logs/
├── deploy-20260419-013500.log          # Log complet du déploiement
├── deployment-report-20260419-013500.txt  # Rapport Sandwich
└── accessibility-audit-20260419-013500.json  # Audit WCAG
```

### Consultation

```powershell
# Dernier déploiement
Get-Content .\logs\deploy-*.log | Select-Object -Last 50

# Rechercher les erreurs
Select-String -Path .\logs\deploy-*.log -Pattern "ERROR"

# Rapport complet
Get-Content .\logs\deployment-report-*.txt
```

---

## 🔧 Dépannage

### Erreur : "Fichier .env.production manquant"

**Solution** :

```powershell
# Créer le fichier
New-Item -ItemType File -Path .env.production

# Ajouter les variables (voir section Préparation)
notepad .env.production
```

### Erreur : "SSH command failed"

**Causes possibles** :
1. Clé SSH non configurée
2. Firewall bloque le port 22
3. Mauvais nom d'utilisateur/IP

**Solution** :

```powershell
# Tester SSH manuellement
ssh root@76.13.43.3 "echo 'Test OK'"

# Vérifier la clé SSH
Test-Path $env:USERPROFILE\.ssh\id_rsa

# Copier la clé publique
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh root@76.13.43.3 "cat >> ~/.ssh/authorized_keys"
```

### Erreur : "Docker build failed"

**Solution** :

```bash
# Sur le VPS, vérifier les logs
cd /opt/oceansentinel
docker compose logs api

# Reconstruire manuellement
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

### Erreur : "Certificat SSL non obtenu"

**Causes possibles** :
1. DNS non configuré
2. Ports 80/443 bloqués
3. Limite Let's Encrypt atteinte

**Solution** :

```bash
# Vérifier DNS
nslookup oceansentinel.fr

# Tester manuellement
certbot certonly --standalone -d oceansentinel.fr --dry-run

# Vérifier les logs
tail -f /var/log/letsencrypt/letsencrypt.log
```

---

## 📋 Checklist Post-Déploiement

```markdown
## Infrastructure
- [ ] VPS accessible (SSH, HTTP, HTTPS)
- [ ] Docker et Docker Compose opérationnels
- [ ] UFW configuré (ports 22, 80, 443)
- [ ] Certificat SSL valide

## Services
- [ ] PostgreSQL healthy (pgvector installé)
- [ ] Redis healthy
- [ ] API FastAPI accessible (/api/health)
- [ ] Worker Stripe actif (2 réplicas)

## Sécurité
- [ ] Ports internes sur 127.0.0.1 uniquement
- [ ] .env sécurisé (chmod 600)
- [ ] HTTPS forcé (redirect HTTP)
- [ ] Headers de sécurité configurés

## Stripe
- [ ] Webhook endpoint créé dans dashboard
- [ ] Signing secret configuré
- [ ] Test avec Stripe CLI réussi
- [ ] DLQ opérationnelle

## Tests
- [ ] API health check: GET /api/health
- [ ] Inscription: POST /api/auth/register
- [ ] Audit accessibilité: Aucune violation critique
- [ ] Logs accessibles et structurés
```

---

## 🚀 Commandes Utiles Post-Déploiement

### Vérifier l'État des Services

```bash
# Sur le VPS
cd /opt/oceansentinel

# Statut des conteneurs
docker compose ps

# Logs en temps réel
docker compose logs -f

# Logs d'un service spécifique
docker compose logs -f api
docker compose logs -f stripe-worker
```

### Tester l'API

```bash
# Health check
curl https://oceansentinel.fr/api/health

# Swagger UI
curl https://oceansentinel.fr/api/docs

# Inscription test
curl -X POST https://oceansentinel.fr/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "consent": true,
    "consent_timestamp": "2026-04-19T01:30:00Z"
  }'
```

### Redémarrer les Services

```bash
# Redémarrer tous les services
docker compose restart

# Redémarrer un service spécifique
docker compose restart api
docker compose restart stripe-worker

# Reconstruire et redémarrer
docker compose up -d --build --force-recreate
```

### Sauvegardes

```bash
# Backup PostgreSQL
docker exec oceansentinel_postgres pg_dump -U oceansentinel oceansentinel | gzip > backup-$(date +%Y%m%d).sql.gz

# Backup .env
cp /opt/oceansentinel/.env /opt/oceansentinel/backups/env-$(date +%Y%m%d)
```

---

**Document créé le** : 19 avril 2026  
**Version** : 1.0  
**Auteur** : SRE Team - Ocean Sentinel
