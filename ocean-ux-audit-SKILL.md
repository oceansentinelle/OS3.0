---
name: ocean-ux-audit
description: Use this skill when the user asks to "audit the UX/UI", "check design quality", "improve interface", or "validate accessibility". This skill orchestrates comprehensive UX/UI analysis using professional design principles and WCAG 2.2 AA standards for oceansentinelle.fr.
version: 1.0.0
compatibility: Requires access to frontend files and browser testing capabilities.
dependencies:
  - uxui-principles/interface-auditor
  - ui-polish/fixing-accessibility
  - webapp-uat
allowed-tools: read_file, grep_search, run_command
---

# Ocean Sentinel UX/UI Audit Skill

## Objectif
Analyser et améliorer la qualité UX/UI du site oceansentinelle.fr selon les standards professionnels de design, d'accessibilité (WCAG 2.2 AA) et de performance.

## Instructions d'Exécution

### Phase 1 : Audit Structurel (Interface Auditor)

Utilisez la compétence **uxui-principles/interface-auditor** pour analyser :

1. **Hiérarchie Visuelle**
   - Vérifier la cohérence des tailles de titres (h1 > h2 > h3)
   - Valider le contraste des couleurs (ratio 4.5:1 minimum pour texte)
   - Analyser l'espacement et la densité d'information

2. **Navigation & Architecture**
   - Tester la clarté du menu principal
   - Vérifier la cohérence des liens entre pages
   - Valider le fil d'Ariane si applicable

3. **Feedback Utilisateur**
   - États hover/focus/active des éléments interactifs
   - Messages d'erreur et de succès
   - Indicateurs de chargement

4. **Responsive Design**
   - Breakpoints mobile (< 768px)
   - Breakpoints tablette (768px - 1024px)
   - Breakpoints desktop (> 1024px)

### Phase 2 : Accessibilité (WCAG 2.2 AA)

Utilisez la compétence **ui-polish/fixing-accessibility** pour vérifier :

1. **Sémantique HTML**
   - Balises ARIA appropriées
   - Landmarks (<header>, <nav>, <main>, <footer>)
   - Attributs alt sur images

2. **Navigation Clavier**
   - Ordre de tabulation logique
   - Focus visible sur tous les éléments interactifs
   - Skip links pour navigation rapide

3. **Contrastes de Couleurs**
   - Texte normal : ratio 4.5:1
   - Texte large (18pt+) : ratio 3:1
   - Éléments UI : ratio 3:1

4. **Formulaires**
   - Labels associés aux inputs
   - Messages d'erreur descriptifs
   - Validation accessible

### Phase 3 : Tests Navigateur (Webapp UAT)

Utilisez la compétence **webapp-uat** pour :

1. **Tests Fonctionnels**
   - Charger toutes les pages (index, about, podcast, dashboard, api)
   - Vérifier l'absence d'erreurs console
   - Valider les requêtes réseau (200 OK)

2. **Tests Visuels**
   - Captures d'écran mobile/desktop
   - Détection de contenu tronqué
   - Vérification des images cassées

3. **Performance**
   - Temps de chargement < 3s
   - Absence de layout shift (CLS)
   - Optimisation des assets

### Phase 4 : Rapport de Recommandations

Générer un rapport structuré :

```markdown
# Audit UX/UI Ocean Sentinelle - [DATE]

## Résumé Exécutif
- Score global : X/100
- Problèmes critiques : X
- Améliorations recommandées : X

## Problèmes Critiques (P0)
1. [Titre du problème]
   - **Impact** : [Description]
   - **Principe violé** : [Référence UX/UI Principles]
   - **Correction** : [Code ou action]

## Améliorations Recommandées (P1)
...

## Optimisations (P2)
...

## Checklist WCAG 2.2 AA
- [ ] 1.1.1 Non-text Content
- [ ] 1.3.1 Info and Relationships
- [ ] 1.4.3 Contrast (Minimum)
- [ ] 2.1.1 Keyboard
- [ ] 2.4.7 Focus Visible
- [ ] 3.2.3 Consistent Navigation
- [ ] 4.1.2 Name, Role, Value
```

## Contraintes de Sécurité

- **JAMAIS** modifier le code sans validation explicite de l'utilisateur
- **TOUJOURS** créer un backup avant toute modification
- **RESPECTER** les règles AZTRM-D (Zero Trust)
- **DOCUMENTER** chaque changement dans un fichier CHANGELOG

## Exemples de Commandes

### Audit Complet
```bash
# 1. Analyser la structure HTML
grep -r 'class=' /opt/oceansentinel/frontend/*.html

# 2. Vérifier les contrastes
# (Utiliser outil externe ou analyse visuelle)

# 3. Tester accessibilité
npx playwright test --project=accessibility

# 4. Générer rapport
cat > /opt/oceansentinel/docs/UX_AUDIT_YYYYMMDD.md
```

## Métriques de Succès

- ✅ **Accessibilité** : 100% WCAG 2.2 AA
- ✅ **Performance** : Lighthouse score > 90
- ✅ **UX** : 0 anti-patterns détectés
- ✅ **Responsive** : Fonctionnel sur mobile/tablette/desktop

## Références

- [UX/UI Principles - 168 principes](https://uxuiprinciples.com)
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [Material Design](https://m3.material.io)
- [ANSSI - Accessibilité](https://www.ssi.gouv.fr/guide/accessibilite-numerique/)
