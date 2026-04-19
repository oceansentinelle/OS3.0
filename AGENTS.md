# 🤖 AGENTS.md - Architecture DevSecOps AZTRM-D
# Ocean Sentinel - Agent Governance & Security Rules

## 📋 Table des Matières
1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Zero Trust](#architecture-zero-trust)
3. [Règles d'Architecture](#règles-darchitecture)
4. [Gestion des Dépendances](#gestion-des-dépendances)
5. [Validation des Inputs](#validation-des-inputs)
6. [Pipeline de Sécurité](#pipeline-de-sécurité)
7. [Rôles des Agents](#rôles-des-agents)
8. [Enforcement & Audit](#enforcement--audit)

---

## Vue d'Ensemble

Ce document définit les **règles d'architecture DevSecOps** que tous les agents IA (Cascade, CI/CD bots, code reviewers) doivent respecter sur le dépôt Ocean Sentinel. L'approche est basée sur le principe **AZTRM-D** (Automated Zero Trust Risk Management).

### Principe Fondamental
**Aucun code n'est fiable par défaut.** Toute génération, modification ou déploiement doit passer par une validation mécanique stricte avant d'atteindre la production.

### Quality Gates (Inner Loop → Outer Loop)
```
┌─────────────────────────────────────────────────────────────┐
│ INNER LOOP (IDE - Windsurf/Cascade)                         │
│ ├─ .windsurfrules enforcement                               │
│ ├─ Type checking (mypy, TypeScript strict)                  │
│ ├─ Linting (pylint, flake8, ESLint)                         │
│ ├─ Unit tests (pytest, Jest)                                │
│ └─ Secret scanning (local)                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │ git commit
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ OUTER LOOP (CI/CD - GitHub Actions / GitLab CI)             │
│ ├─ SAST (Semgrep, Bandit, ESLint security)                  │
│ ├─ Dependency scanning (Safety, Snyk, npm audit)            │
│ ├─ Container scanning (Trivy, Grype)                        │
│ ├─ Integration tests (pytest, Playwright)                   │
│ ├─ DAST (OWASP ZAP, Burp Suite)                             │
│ └─ Compliance checks (RGPD, WCAG 2.2, ANSSI)                │
└──────────────────┬──────────────────────────────────────────┘
                   │ deployment
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ PRODUCTION (VPS Hostinger)                                   │
│ ├─ Runtime monitoring (Prometheus, Grafana)                 │
│ ├─ WAF (ModSecurity, Cloudflare)                            │
│ ├─ Intrusion detection (Fail2ban, OSSEC)                    │
│ └─ Audit logging (ELK stack, Loki)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Zero Trust

### Principes AZTRM-D

1. **Never Trust, Always Verify**
   - Aucun code généré par IA n'est exécuté sans validation
   - Aucune dépendance n'est installée sans scan de vulnérabilités
   - Aucun secret n'est stocké en clair (variables d'environnement uniquement)

2. **Least Privilege**
   - Utilisateurs PostgreSQL avec permissions minimales (read-only pour workers)
   - Conteneurs Docker non-root (USER directive)
   - API keys avec scopes limités (read-only, write-only, admin)

3. **Defense in Depth**
   - Validation côté client (JavaScript) + côté serveur (Pydantic)
   - Firewall UFW + Nginx rate limiting + application-level RBAC
   - Chiffrement en transit (TLS 1.3) + au repos (PostgreSQL encryption)

4. **Fail Securely**
   - En cas d'erreur, refuser l'accès par défaut (deny-by-default)
   - Logs détaillés pour debugging, messages génériques pour utilisateurs
   - Rollback automatique si health check échoue après déploiement

---

## Règles d'Architecture

### 1. Séparation des Responsabilités (Microservices)

**OBLIGATOIRE** : Chaque service doit avoir une responsabilité unique et bien définie.

```yaml
# ✅ BON (docker-compose.yml)
services:
  postgres:        # Stockage données
  redis:           # Cache & queues
  api:             # Endpoints REST
  orchestrator:    # Coordination workers
  ingest_worker:   # Ingestion ERDDAP
  transform_worker: # Transformation données
  alert_worker:    # Notifications utilisateurs
```

```yaml
# ❌ MAUVAIS (monolithe)
services:
  app:  # Fait tout (DB + API + workers + cache)
```

### 2. Communication Inter-Services

**OBLIGATOIRE** : Utiliser un réseau Docker privé avec DNS interne.

```yaml
# ✅ BON
networks:
  ocean_net:
    driver: bridge
    internal: false  # Accès Internet pour workers
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

**INTERDIT** : Exposition directe des services internes sur 0.0.0.0.

```yaml
# ❌ MAUVAIS
ports:
  - "0.0.0.0:5432:5432"  # PostgreSQL accessible publiquement

# ✅ BON
ports:
  - "127.0.0.1:5432:5432"  # Localhost uniquement
```

### 3. Gestion des Secrets

**OBLIGATOIRE** : Utiliser des variables d'environnement avec fichier `.env` (gitignored).

```python
# ✅ BON
import os
DATABASE_URL = os.getenv("DATABASE_URL")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
```

```python
# ❌ MAUVAIS
DATABASE_URL = "postgresql://admin:password123@localhost/db"
STRIPE_SECRET_KEY = "sk_live_51AbCdEf..."
```

**OBLIGATOIRE** : Rotation des secrets tous les 90 jours (automatisée via CI/CD).

### 4. Gestion des Erreurs

**OBLIGATOIRE** : Séparer les logs internes des messages utilisateurs.

```python
# ✅ BON
import logging
logger = logging.getLogger(__name__)

try:
    user = authenticate(email, password)
except AuthenticationError as e:
    logger.error(f"Auth failed for {email}: {e}", exc_info=True)
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

```python
# ❌ MAUVAIS
try:
    user = authenticate(email, password)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # Fuite d'info
```

---

## Gestion des Dépendances

### Politique de Versioning

**OBLIGATOIRE** : Versions exactes (pinned) dans `requirements.txt` et `package.json`.

```txt
# ✅ BON (requirements.txt)
fastapi==0.115.0
pydantic==2.9.2
sqlalchemy==2.0.36
```

```txt
# ❌ MAUVAIS
fastapi>=0.100.0
pydantic~=2.0
sqlalchemy
```

### Scan de Vulnérabilités

**OBLIGATOIRE** : Exécuter `safety check` (Python) ou `npm audit` (Node.js) avant chaque commit.

```bash
# Python
pip install safety
safety check --json

# Node.js
npm audit --audit-level=moderate
```

**INTERDIT** : Installer des dépendances avec des CVEs critiques sans plan de mitigation documenté.

### Dépendances Approuvées

**Liste blanche** (mise à jour mensuelle) :

**Python** :
- FastAPI (API REST)
- Pydantic (validation)
- SQLAlchemy (ORM)
- Alembic (migrations)
- pytest (tests)
- httpx (HTTP client)
- python-jose (JWT)
- passlib (hashing)
- stripe (paiements)

**JavaScript** :
- React (frontend)
- Axios (HTTP client)
- Zod (validation)
- TailwindCSS (styling)
- Lucide React (icons)

**INTERDIT** : Dépendances non maintenues (dernière release > 2 ans).

---

## Validation des Inputs

### Principe : Validate Early, Validate Often

**OBLIGATOIRE** : Valider TOUS les inputs utilisateurs (API, formulaires, uploads).

### 1. Validation API (Pydantic)

```python
# ✅ BON
from pydantic import BaseModel, Field, EmailStr, validator

class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    station_id: str = Field(..., regex=r'^[A-Z0-9_-]+$')
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### 2. Protection SQL Injection

**OBLIGATOIRE** : Utiliser des requêtes paramétrées (SQLAlchemy ORM ou placeholders).

```python
# ✅ BON (SQLAlchemy ORM)
from sqlalchemy import select
stmt = select(User).where(User.email == email)
user = session.execute(stmt).scalar_one_or_none()
```

```python
# ✅ BON (psycopg2 avec placeholders)
cursor.execute(
    "SELECT * FROM users WHERE email = %s",
    (email,)
)
```

```python
# ❌ MAUVAIS (SQL injection)
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)
```

### 3. Protection XSS (Frontend)

**OBLIGATOIRE** : Échapper les inputs avant affichage.

```javascript
// ✅ BON (React échappe automatiquement)
<div>{userInput}</div>

// ❌ MAUVAIS (dangerouslySetInnerHTML)
<div dangerouslySetInnerHTML={{__html: userInput}} />
```

### 4. Upload de Fichiers

**OBLIGATOIRE** : Valider MIME type, extension, et taille.

```python
# ✅ BON
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {'.csv', '.json', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def upload_file(file: UploadFile):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")
    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    
    # Vérifier MIME type
    import magic
    mime = magic.from_buffer(content, mime=True)
    if mime not in ['text/csv', 'application/json']:
        raise HTTPException(400, "Invalid MIME type")
```

---

## Pipeline de Sécurité

### Phase 1 : Pre-Commit (Local - Windsurf)

```bash
# Exécuté automatiquement par /aztrm-scan
1. Linting (pylint, flake8, ESLint)
2. Type checking (mypy --strict, tsc --noEmit)
3. Unit tests (pytest -v, npm test)
4. Secret scanning (detect-secrets, gitleaks)
5. Dependency check (safety, npm audit)
```

### Phase 2 : CI/CD (GitHub Actions)

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Semgrep SAST
        run: semgrep --config=auto --json > semgrep.json
      - name: Bandit (Python)
        run: bandit -r backend/ -f json -o bandit.json
      - name: Trivy (Docker)
        run: trivy image oceansentinel-api:latest
```

### Phase 3 : Production (Runtime)

```yaml
# docker-compose.yml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## Rôles des Agents

### 1. Code Security Agent (Cascade - Windsurf)

**Responsabilités** :
- Appliquer `.windsurfrules` à chaque génération de code
- Refuser la génération de code non conforme
- Suggérer des alternatives sécurisées
- Documenter les décisions de sécurité

**Exemples d'Interventions** :

```python
# ❌ Code proposé par l'utilisateur
def get_user(user_id):
    return db.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ Code généré par Cascade
def get_user(user_id: int) -> Optional[User]:
    """Retrieve user by ID with SQL injection protection.
    
    Args:
        user_id: User ID (validated as integer)
    
    Returns:
        User object or None if not found
    """
    stmt = select(User).where(User.id == user_id)
    return session.execute(stmt).scalar_one_or_none()
```

### 2. CI/CD Agent (GitHub Actions)

**Responsabilités** :
- Exécuter SAST, DAST, dependency scanning
- Bloquer les PRs avec vulnérabilités critiques
- Générer des rapports de sécurité
- Notifier l'équipe en cas de régression

### 3. Monitoring Agent (Prometheus + Grafana)

**Responsabilités** :
- Surveiller les métriques de sécurité (taux d'erreur 401/403, latence)
- Détecter les anomalies (spike de requêtes, tentatives de brute-force)
- Déclencher des alertes (PagerDuty, Slack)

---

## Enforcement & Audit

### Mécanismes d'Enforcement

1. **Pre-commit hooks** : Bloquent les commits non conformes
2. **CI/CD gates** : Bloquent les déploiements avec vulnérabilités
3. **Runtime policies** : OPA (Open Policy Agent) pour RBAC dynamique

### Audit Trail

**OBLIGATOIRE** : Tous les événements de sécurité doivent être loggés.

```python
# ✅ BON
import structlog
logger = structlog.get_logger()

logger.info("user_login_success", user_id=user.id, ip=request.client.host)
logger.warning("user_login_failed", email=email, reason="invalid_password")
logger.error("api_key_revoked", key_id=key.id, reason="compromised")
```

### Métriques de Conformité

**KPIs** (mesurés mensuellement) :
- % de code avec tests (objectif : >80%)
- Nombre de vulnérabilités critiques (objectif : 0)
- Temps moyen de résolution des CVEs (objectif : <7 jours)
- Taux de faux positifs SAST (objectif : <10%)

---

## Références

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [ANSSI Recommandations 2026](https://www.ssi.gouv.fr/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [RGPD (GDPR)](https://gdpr.eu/)

---

**Version** : 1.0.0  
**Dernière mise à jour** : 19 avril 2026  
**Propriétaire** : Équipe DevSecOps Ocean Sentinel
