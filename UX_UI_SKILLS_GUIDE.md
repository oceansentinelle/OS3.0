# 🎨 Guide des Compétences UX/UI - Ocean Sentinel

## 📋 Vue d'Ensemble

Ocean Sentinel dispose maintenant de **4 compétences professionnelles** pour auditer et améliorer la qualité UX/UI du site oceansentinelle.fr.

---

## 🛠️ Compétences Installées

### 1. **uxui-principles** (168 principes de design)
**Emplacement** : `.agents/skills/uxui-principles/`

**Sous-compétences** :
- `interface-auditor` : Audit structurel des interfaces
- `uxui-evaluator` : Évaluation selon taxonomie UX/UI
- `flow-checker` : Vérification des parcours utilisateurs
- `ai-interface-reviewer` : Revue des interfaces générées par IA

**Utilisation** :
```bash
# Analyser la hiérarchie visuelle
@uxui-principles/interface-auditor audit /opt/oceansentinel/frontend/index.html

# Évaluer selon les 168 principes
@uxui-principles/uxui-evaluator evaluate dashboard.html
```

**Référence** : https://uxuiprinciples.com

---

### 2. **ui-polish** (Raffinement esthétique)
**Emplacement** : `.agents/skills/ui-polish/`

**Sous-compétences** :
- `baseline-ui` : Standards de base UI
- `fixing-accessibility` : Corrections accessibilité
- `fixing-metadata` : Optimisation métadonnées
- `fixing-motion-performance` : Performance animations

**Utilisation** :
```bash
# Corriger l'accessibilité
@ui-polish/fixing-accessibility fix /opt/oceansentinel/frontend/

# Optimiser les métadonnées
@ui-polish/fixing-metadata optimize index.html
```

**Référence** : https://github.com/ibelick/ui-skills

---

### 3. **webapp-uat** (Tests navigateur complets)
**Emplacement** : `.agents/skills/webapp-uat/`

**Fonctionnalités** :
- Tests Playwright automatisés
- Validation WCAG 2.2 AA
- Capture erreurs console/réseau
- Tests responsive (mobile/tablette/desktop)
- Validation i18n

**Utilisation** :
```bash
# Lancer UAT complet
npx playwright test --config=webapp-uat

# Tests accessibilité uniquement
npx playwright test --project=accessibility
```

**Référence** : https://github.com/tsilverberg/webapp-uat

---

### 4. **ocean-ux-audit** (Orchestrateur spécifique)
**Emplacement** : `.agents/skills/ocean-ux-audit/`

**Rôle** : Coordonne les 3 compétences précédentes pour un audit complet d'Ocean Sentinel.

**Phases** :
1. Audit structurel (uxui-principles)
2. Accessibilité WCAG 2.2 AA (ui-polish)
3. Tests navigateur (webapp-uat)
4. Rapport de recommandations

**Utilisation** :
```bash
# Demander à Windsurf/Cascade
"Audit UX/UI complet du site oceansentinelle.fr"
"Vérifier l'accessibilité WCAG 2.2 AA"
"Tester le responsive design"
```

---

## 🎯 Commandes Rapides

### Audit Complet
```bash
# 1. Analyser structure HTML
grep -r 'aria-' /opt/oceansentinel/frontend/*.html

# 2. Vérifier contrastes de couleurs
# (Utiliser extension navigateur : axe DevTools)

# 3. Tester navigation clavier
# (Utiliser Tab, Shift+Tab, Enter, Espace)

# 4. Valider sémantique
grep -r '<header\|<nav\|<main\|<footer' /opt/oceansentinel/frontend/*.html
```

### Checklist Manuelle

#### ✅ Accessibilité WCAG 2.2 AA
- [ ] Tous les liens ont un texte descriptif
- [ ] Toutes les images ont un attribut `alt`
- [ ] Contraste texte/fond ≥ 4.5:1
- [ ] Navigation possible au clavier
- [ ] Focus visible sur tous les éléments interactifs
- [ ] Pas de contenu clignotant > 3 fois/seconde
- [ ] Formulaires avec labels associés

#### ✅ UX Best Practices
- [ ] Hiérarchie visuelle claire (h1 > h2 > h3)
- [ ] Navigation cohérente sur toutes les pages
- [ ] Feedback visuel sur actions (hover, click)
- [ ] Messages d'erreur descriptifs
- [ ] Temps de chargement < 3 secondes
- [ ] Responsive mobile/tablette/desktop

#### ✅ Performance
- [ ] Images optimisées (WebP, compression)
- [ ] CSS/JS minifiés
- [ ] Lazy loading pour images
- [ ] Cache navigateur activé
- [ ] CDN pour assets statiques

---

## 📊 Métriques de Qualité

### Score Lighthouse (Objectif)
- **Performance** : ≥ 90
- **Accessibilité** : 100
- **Best Practices** : ≥ 90
- **SEO** : ≥ 90

### WCAG 2.2 AA (Objectif)
- **Niveau A** : 100% conforme
- **Niveau AA** : 100% conforme

### UX/UI Principles (Objectif)
- **Anti-patterns** : 0
- **Violations critiques** : 0
- **Améliorations recommandées** : < 5

---

## 🔧 Outils Complémentaires

### Extensions Navigateur
- **axe DevTools** : Audit accessibilité
- **WAVE** : Évaluation accessibilité visuelle
- **Lighthouse** : Audit performance/SEO
- **ColorZilla** : Vérification contrastes

### Outils CLI
```bash
# Lighthouse CLI
npm install -g lighthouse
lighthouse https://oceansentinelle.fr --view

# Pa11y (accessibilité)
npm install -g pa11y
pa11y https://oceansentinelle.fr

# Playwright (tests E2E)
npx playwright test
```

---

## 📝 Workflow d'Audit Recommandé

### 1. Audit Initial
```bash
# Demander à Cascade
"Audit UX/UI complet du site oceansentinelle.fr avec ocean-ux-audit"
```

### 2. Corrections Prioritaires
- Traiter les problèmes critiques (P0) en premier
- Valider chaque correction avec tests

### 3. Améliorations Incrémentales
- Implémenter les recommandations P1
- Optimiser progressivement (P2)

### 4. Validation Continue
- Relancer l'audit après chaque modification majeure
- Maintenir un score Lighthouse ≥ 90

---

## 🎓 Références

- **UX/UI Principles** : https://uxuiprinciples.com
- **WCAG 2.2** : https://www.w3.org/WAI/WCAG22/quickref/
- **Material Design** : https://m3.material.io
- **ANSSI Accessibilité** : https://www.ssi.gouv.fr/guide/accessibilite-numerique/
- **WebAIM** : https://webaim.org/resources/

---

**Dernière mise à jour** : 2026-04-22  
**Version** : 1.0.0
