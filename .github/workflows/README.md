# GitHub Actions Workflows

## 📋 Workflows Disponibles

### 1. **CI/CD Pipeline Principal** (`ci-cd.yml`)
- **Déclenchement** : Push sur `main`/`develop`, Pull Requests sur `main`
- **Jobs** :
  - `test-contract` : Tests Newman avec API locale
  - `security-scan` : Scan SAST (Bandit, Safety, Semgrep)
  - `build-and-deploy` : Build Docker + déploiement production (main uniquement)

### 2. **Déploiement Staging** (`deploy-staging.yml`)
- **Déclenchement** : Push sur `develop`, workflow manuel
- **Job** : Déploiement environnement staging

### 3. **Déploiement Production/Staging** (`github-workflows-deploy.yml`)
- **Déclenchement** : Workflow manuel avec choix environnement
- **Jobs** :
  - `deploy` : Déploiement cible (production ou staging)
  - `rollback` : Rollback automatique en cas d'échec

## 🔧 Variables d'Environnement Requises

### GitHub Secrets
```
PRODUCTION_HOST      # VPS production (oceansentinelle.fr)
PRODUCTION_USER      # SSH user production
PRODUCTION_SSH_KEY   # SSH key production
DATABASE_URL         # PostgreSQL production
REDIS_URL            # Redis production
PROMETHEUS_URL       # Prometheus production
SLACK_WEBHOOK_URL     # Webhook Slack alertes

STAGING_HOST         # Serveur staging
STAGING_USER         # SSH user staging
STAGING_SSH_KEY      # SSH key staging
STAGING_DATABASE_URL   # PostgreSQL staging
STAGING_REDIS_URL    # Redis staging
```

## 🚀 Utilisation

### Déploiement Production
```bash
# Push sur main → déploiement automatique
git push origin main
```

### Déploiement Staging
```bash
# Push sur develop → déploiement staging
git push origin develop
```

### Déploiement Manuel
```bash
# Via interface GitHub Actions
# Onglet "Actions" → "Deploy Production" ou "Deploy Staging"
```

## 📊 Étapes CI/CD

1. **Test Contract** : Newman en mode TEST_MODE local
2. **Sécurité** : Bandit + Safety + Semgrep
3. **Build Docker** : Image multi-arch avec tags
4. **Déploiement** : SSH + Docker sur VPS
5. **Health Check** : Vérification post-déploiement
6. **Rollback** : Automatique en cas d'échec
7. **Notification** : Slack en cas de rollback

## 🛡️ Sécurité Intégrée

- Tests contractuels obligatoires avant déploiement
- Scan SAST automatique
- Images Docker scannées (Trivy)
- Secrets GitHub utilisés (jamais en clair)
- Connexions SSH par clés
- Variables d'environnement par secrets
