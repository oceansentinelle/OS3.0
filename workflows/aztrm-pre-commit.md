---
description: AZTRM-D Pre-Commit Security Scan - Validation locale avant commit
---

# 🔒 AZTRM-D Pre-Commit Security Workflow

Ce workflow exécute une validation de sécurité complète avant chaque commit.
Commande personnalisée : `/aztrm-scan`

## 📋 Étapes de Validation

### 1. Linting et Formatage

**Python** :
```bash
# Linting avec pylint
pylint backend/ --rcfile=.pylintrc --exit-zero

# Formatage avec black (vérification uniquement)
black backend/ --check --diff

# Flake8 pour style PEP 8
flake8 backend/ --max-line-length=100 --exclude=__pycache__,venv
```

**JavaScript/TypeScript** :
```bash
# ESLint
eslint frontend/ --ext .js,.jsx,.ts,.tsx

# Prettier (vérification)
prettier --check "frontend/**/*.{js,jsx,ts,tsx,css,md}"
```

### 2. Type Checking

**Python** :
```bash
# mypy en mode strict
mypy backend/ --strict --ignore-missing-imports
```

**TypeScript** :
```bash
# TypeScript compiler (no emit)
tsc --noEmit --project frontend/tsconfig.json
```

### 3. Tests Unitaires

**Python** :
```bash
# pytest avec couverture
pytest backend/tests/ -v --cov=backend --cov-report=term-missing --cov-fail-under=80
```

**JavaScript** :
```bash
# Jest
npm test -- --coverage --coverageThreshold='{"global":{"lines":80}}'
```

### 4. Détection de Secrets

```bash
# detect-secrets (scan uniquement les fichiers modifiés)
git diff --name-only --cached | xargs detect-secrets-hook --baseline .secrets.baseline

# Alternative : gitleaks
gitleaks detect --source . --verbose --no-git
```

### 5. Scan de Dépendances

**Python** :
```bash
# Safety check (vulnérabilités CVE)
safety check --json --file requirements.txt

# pip-audit (alternative)
pip-audit --requirement requirements.txt
```

**JavaScript** :
```bash
# npm audit
npm audit --audit-level=moderate --json

# Snyk (si configuré)
snyk test --severity-threshold=high
```

### 6. Analyse SAST Locale (Optionnel)

**Semgrep** :
```bash
# Scan avec règles OWASP
semgrep --config=auto backend/ frontend/ --json --output=semgrep-report.json

# Afficher uniquement les erreurs critiques
semgrep --config=auto backend/ --severity=ERROR
```

**Bandit (Python)** :
```bash
# Scan de sécurité Python
bandit -r backend/ -f json -o bandit-report.json

# Afficher les résultats
bandit -r backend/ -ll
```

### 7. Validation Docker (si applicable)

```bash
# Hadolint (Dockerfile linting)
hadolint backend/Dockerfile
hadolint frontend/Dockerfile

# Trivy (scan d'image locale)
trivy image oceansentinel-api:latest --severity HIGH,CRITICAL
```

### 8. Auto-Remediation

**Corrections automatiques** :
```bash
# Python : black pour formatage
black backend/

# JavaScript : prettier
prettier --write "frontend/**/*.{js,jsx,ts,tsx,css,md}"

# Python : isort pour imports
isort backend/

# Ajouter les fichiers corrigés
git add -u
```

---

## 🚀 Utilisation

### Commande Manuelle

```bash
# Exécuter le scan complet
./workflows/aztrm-scan.sh

# Ou via Windsurf (si configuré)
/aztrm-scan
```

### Script d'Exécution

Créer `workflows/aztrm-scan.sh` :

```bash
#!/bin/bash
set -e

echo "🔒 AZTRM-D Pre-Commit Security Scan"
echo "===================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
ERRORS=0
WARNINGS=0

# 1. Linting Python
echo "📝 [1/8] Linting Python..."
if pylint backend/ --exit-zero --score=y | grep "Your code has been rated"; then
    echo -e "${GREEN}✓ Linting Python OK${NC}"
else
    echo -e "${RED}✗ Linting Python FAILED${NC}"
    ((ERRORS++))
fi
echo ""

# 2. Type Checking
echo "🔍 [2/8] Type Checking..."
if mypy backend/ --strict --ignore-missing-imports; then
    echo -e "${GREEN}✓ Type Checking OK${NC}"
else
    echo -e "${RED}✗ Type Checking FAILED${NC}"
    ((ERRORS++))
fi
echo ""

# 3. Tests Unitaires
echo "🧪 [3/8] Tests Unitaires..."
if pytest backend/tests/ -v --cov=backend --cov-fail-under=80 -q; then
    echo -e "${GREEN}✓ Tests OK${NC}"
else
    echo -e "${RED}✗ Tests FAILED${NC}"
    ((ERRORS++))
fi
echo ""

# 4. Détection de Secrets
echo "🔐 [4/8] Détection de Secrets..."
if git diff --name-only --cached | xargs -r detect-secrets-hook --baseline .secrets.baseline; then
    echo -e "${GREEN}✓ Aucun secret détecté${NC}"
else
    echo -e "${RED}✗ SECRETS DÉTECTÉS - COMMIT BLOQUÉ${NC}"
    ((ERRORS++))
fi
echo ""

# 5. Scan de Dépendances
echo "📦 [5/8] Scan de Dépendances..."
if safety check --file requirements.txt --json > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Dépendances sécurisées${NC}"
else
    echo -e "${YELLOW}⚠ Vulnérabilités détectées${NC}"
    safety check --file requirements.txt
    ((WARNINGS++))
fi
echo ""

# 6. SAST Semgrep
echo "🛡️ [6/8] Analyse SAST (Semgrep)..."
if command -v semgrep &> /dev/null; then
    if semgrep --config=auto backend/ --severity=ERROR --quiet; then
        echo -e "${GREEN}✓ SAST OK${NC}"
    else
        echo -e "${RED}✗ Vulnérabilités SAST détectées${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠ Semgrep non installé (ignoré)${NC}"
fi
echo ""

# 7. Bandit (Python Security)
echo "🐍 [7/8] Bandit Security Scan..."
if command -v bandit &> /dev/null; then
    if bandit -r backend/ -ll -q; then
        echo -e "${GREEN}✓ Bandit OK${NC}"
    else
        echo -e "${YELLOW}⚠ Problèmes de sécurité détectés${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠ Bandit non installé (ignoré)${NC}"
fi
echo ""

# 8. Docker Linting
echo "🐳 [8/8] Docker Linting..."
if command -v hadolint &> /dev/null; then
    if find . -name "Dockerfile*" -exec hadolint {} \; 2>&1 | grep -q "error"; then
        echo -e "${YELLOW}⚠ Problèmes Dockerfile détectés${NC}"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓ Dockerfiles OK${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Hadolint non installé (ignoré)${NC}"
fi
echo ""

# Résumé
echo "===================================="
echo "📊 Résumé du Scan"
echo "===================================="
echo -e "Erreurs critiques : ${RED}${ERRORS}${NC}"
echo -e "Avertissements : ${YELLOW}${WARNINGS}${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ SCAN ÉCHOUÉ - Commit bloqué${NC}"
    echo "Corrigez les erreurs critiques avant de commiter."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️ SCAN RÉUSSI AVEC AVERTISSEMENTS${NC}"
    echo "Considérez corriger les avertissements."
    exit 0
else
    echo -e "${GREEN}✅ SCAN RÉUSSI - Code prêt pour commit${NC}"
    exit 0
fi
```

### Installation des Outils

**Python** :
```bash
pip install pylint black flake8 mypy pytest pytest-cov safety detect-secrets bandit
```

**JavaScript** :
```bash
npm install -g eslint prettier @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

**Sécurité** :
```bash
# Semgrep
pip install semgrep

# Gitleaks
brew install gitleaks  # macOS
# ou télécharger depuis https://github.com/gitleaks/gitleaks/releases

# Hadolint
brew install hadolint  # macOS
# ou télécharger depuis https://github.com/hadolint/hadolint/releases
```

---

## 🔧 Configuration

### Pre-Commit Hook (Git)

Créer `.git/hooks/pre-commit` :

```bash
#!/bin/bash
# turbo
./workflows/aztrm-scan.sh
```

Rendre exécutable :
```bash
chmod +x .git/hooks/pre-commit
chmod +x workflows/aztrm-scan.sh
```

### Baseline Secrets

Initialiser le baseline pour detect-secrets :
```bash
detect-secrets scan > .secrets.baseline
```

### Configuration Pylint

Créer `.pylintrc` :
```ini
[MASTER]
ignore=venv,env,__pycache__

[MESSAGES CONTROL]
disable=C0111,C0103,R0903

[FORMAT]
max-line-length=100
```

---

## 📊 Rapports

Les rapports sont générés dans :
- `semgrep-report.json` (SAST)
- `bandit-report.json` (Python security)
- `.coverage` (couverture de tests)

---

## ⚙️ Intégration CI/CD

Ce workflow local doit être **synchronisé** avec le pipeline CI/CD distant :

```yaml
# .github/workflows/security.yml
name: AZTRM-D Security Pipeline

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pylint mypy pytest safety semgrep bandit
      
      - name: Run AZTRM-D Scan
        run: ./workflows/aztrm-scan.sh
      
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            semgrep-report.json
            bandit-report.json
```

---

## 🎯 Indicateurs de Réussite

✅ **Le workflow est réussi si** :
1. Aucun secret détecté dans le code
2. Tous les tests passent avec >80% de couverture
3. Aucune vulnérabilité critique (CVE) dans les dépendances
4. Type checking strict réussi
5. Linting sans erreur critique
6. SAST sans vulnérabilité de sévérité ERROR

---

**Version** : 1.0.0  
**Dernière mise à jour** : 19 avril 2026  
**Propriétaire** : Équipe DevSecOps Ocean Sentinel
