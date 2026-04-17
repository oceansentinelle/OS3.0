# Ocean Sentinel V2.0 - Architecture UI/UX Agentique

## Vision

**Ocean Sentinel V2.0** n'est pas un dashboard contemplatif, mais un **poste de commandement agentique** orienté décision.

### Principes Directeurs

1. **Digital-First** (M-23-22) - Expérience simple, fluide, mobile
2. **WCAG 2.2** - Accessibilité by default, usages mobiles
3. **Zero Trust** (NIST) - Protection centrée ressources, contrôle contextuel
4. **Intent Preview** - L'IA annonce avant d'agir
5. **Human-in-the-Loop** - Contrôles humains toujours visibles

### Temps de Réponse Cible

L'interface doit répondre en **< 5 secondes** à 3 questions :

1. **Quel est le risque maintenant ?**
2. **Que recommande l'IA ?**
3. **Quelle action humaine est attendue ?**

---

## 1. Arborescence Complète

### 1.1 Site Public

#### A. Accueil `/`
- Hero orienté mission
- Résumé proposition de valeur
- Démo agents IA
- Cas d'usage
- CTA : Demander démo / Se connecter

#### B. Produit `/produit`
- Vue d'ensemble
- Surveillance in-situ
- Proxys satellitaires Sentinel-3
- Détection de dérives
- Recommandation d'actions
- Journal d'audit IA

#### C. Solutions `/solutions`
- Ostréiculture `/solutions/ostreiculture`
- Ports et zones côtières `/solutions/ports`
- Recherche et observatoires `/solutions/recherche`
- Institutions / collectivités `/solutions/institutions`
- Assurance / risque environnemental `/solutions/assurance`

#### D. Sécurité, Conformité, Confiance `/securite`
- Secure by Design
- Contrôle d'accès Zero Trust
- Journalisation et audit
- Gouvernance des données
- Accessibilité WCAG
- Gestion de l'incertitude IA

#### E. Ressources `/ressources`
- Documentation produit
- Méthodologie
- API / intégrations
- Notes scientifiques
- Centre d'aide

#### F. Entreprise `/entreprise`
- Vision
- Équipe
- Partenaires
- Contact

#### G. Authentification `/auth`
- Connexion `/auth/login`
- SSO `/auth/sso`
- Réinitialisation `/auth/reset`
- Sélection workspace `/auth/workspace`

---

### 1.2 Application Authentifiée

#### A. Centre de Commandement `/app/command`
- Résumé situationnel
- Alertes prioritaires
- Recommandations IA
- Intent Preview
- Progress Ledger
- Contrôles humains
- Carte décisionnelle

#### B. Zones & Actifs `/app/zones`
- Vue Bassin / littoral `/app/zones/overview`
- Zones surveillées `/app/zones/monitored`
- Stations in-situ `/app/zones/stations`
- Couche satellite `/app/zones/satellite`
- Détail station `/app/zones/stations/:id`
- Détail zone `/app/zones/:id`
- Historique santé capteurs `/app/zones/stations/:id/health`

#### C. Alertes & Incidents `/app/alerts`
- File des alertes `/app/alerts/queue`
- Incidents ouverts `/app/alerts/incidents`
- Chronologie `/app/alerts/timeline`
- Validation opérateur `/app/alerts/:id/validate`
- Actions proposées `/app/alerts/:id/actions`
- Actions exécutées `/app/alerts/:id/executed`
- Post-mortem `/app/alerts/:id/postmortem`

#### D. Missions & Plans d'Action `/app/missions`
- Missions recommandées `/app/missions/recommended`
- Plans en attente validation `/app/missions/pending`
- Plans en exécution `/app/missions/active`
- Plans interrompus `/app/missions/interrupted`
- Escalade expert `/app/missions/:id/escalate`
- Rétroaction opérateur `/app/missions/:id/feedback`

#### E. Agents IA `/app/agents`
- Agents actifs `/app/agents/active`
- Intentions en cours `/app/agents/intents`
- Capacités par agent `/app/agents/capabilities`
- Règles de déclenchement `/app/agents/rules`
- Historique d'exécution `/app/agents/history`
- Niveau d'autonomie `/app/agents/autonomy`

#### F. Données & Modèles `/app/data`
- Flux in-situ `/app/data/insitu`
- Flux satellites `/app/data/satellite`
- Variables thermodynamiques `/app/data/variables`
- Prédictions `/app/data/predictions`
- Signaux de confiance `/app/data/confidence`
- Versions de modèles `/app/data/models`
- Jeux de données référence `/app/data/reference`

#### G. Audit & Conformité `/app/audit`
- Journal complet `/app/audit/log`
- Décisions IA `/app/audit/ai-decisions`
- Décisions humaines `/app/audit/human-decisions`
- Traçabilité des accès `/app/audit/access`
- Export de preuves `/app/audit/export`
- Rapports d'audit `/app/audit/reports`

#### H. Organisation `/app/org`
- Utilisateurs `/app/org/users`
- Rôles `/app/org/roles`
- Cercles de confiance `/app/org/trust-circles`
- Escalade `/app/org/escalation`
- Notifications `/app/org/notifications`
- Paramètres de sécurité `/app/org/security`

#### I. Paramètres `/app/settings`
- Préférences d'affichage `/app/settings/display`
- Seuils d'alerte `/app/settings/thresholds`
- Fréquence de mise à jour `/app/settings/refresh`
- API / intégrations `/app/settings/api`
- Gestion des appareils `/app/settings/devices`
- Langue et accessibilité `/app/settings/accessibility`

---

## 2. Structure Interface Principale - Centre de Commandement

### Architecture Mobile-First

**Mobile** : Pile verticale  
**Desktop** : Grille 12 colonnes

### 2.1 En-tête Global

**Position** : Fixe en haut  
**Hauteur** : 56px mobile / 64px desktop

**Contenu** :
```
[Logo] [Workspace ▾] [Status ●] [Search 🔍] [Notif 🔔] [Avatar]
```

**Règles UX** :
- Ultra compact
- Aucun décor inutile
- Toujours visible (sticky)
- Statut sécurité et synchro sans jargon

**Éléments** :
- Logo discret (32x32px)
- Sélecteur workspace/zone
- État système global (●)
- Recherche universelle
- Notifications (badge count)
- Avatar + rôle utilisateur

---

### 2.2 Bandeau de Situation Critique

**Position** : Tout en haut du contenu principal  
**Hauteur** : Auto (min 80px)

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ [!] RISQUE ÉLEVÉ                                        │
│                                                         │
│ Arcachon Nord - Dérive thermique + baisse O₂           │
│ 3 alertes ouvertes • 2 agents actifs • Sync: 2min      │
│                                                         │
│ → Validation opérateur requise                         │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- Une seule phrase synthétique
- Lisible instantanément
- Code couleur sobre (saturation forte si urgence réelle)
- Langage clair, pas de jargon

**Niveaux de Risque** :
- 🟢 **Normal** - Vert désaturé
- 🟡 **Attention** - Jaune désaturé
- 🟠 **Élevé** - Orange saturé
- 🔴 **Critique** - Rouge saturé

---

### 2.3 Bloc "Intent Preview"

**Position** : Juste sous bandeau critique  
**Hauteur** : Auto (min 120px)

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ 🤖 INTENTION DE L'AGENT                                 │
├─────────────────────────────────────────────────────────┤
│ Objectif : Confirmer dérive thermique Ferret-02         │
│ Sources : Capteur in-situ + Sentinel-3 proxy            │
│ Durée estimée : 5 minutes                               │
│ Confiance : 87%                                         │
│                                                         │
│ Impact attendu : Validation ou infirmation anomalie     │
│                                                         │
│ [Valider] [Corriger] [Interrompre] [Différer]          │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- Remplace le "widget IA magique"
- L'IA annonce ce qu'elle va faire AVANT de le faire
- Humain toujours au-dessus de l'automatisation
- Actions claires et immédiates

**Actions** :
- **Valider** - Approuver et lancer
- **Corriger** - Modifier paramètres
- **Interrompre** - Stopper immédiatement
- **Différer** - Reporter à plus tard

---

### 2.4 Bloc "Recommandation Prioritaire"

**Position** : Centre gauche desktop / Après Intent Preview mobile  
**Largeur** : 6 colonnes desktop / 100% mobile

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ 🎯 ACTION PRIORITAIRE                                   │
├─────────────────────────────────────────────────────────┤
│ Inspecter station Ferret-02                             │
│                                                         │
│ Raison : Écart +3.2°C vs moyenne saisonnière            │
│ Fenêtre : 20 minutes                                    │
│ Opérateur : Équipe Arcachon Nord                        │
│                                                         │
│ Si inaction : Risque de perte de données critiques      │
│                                                         │
│ [Confirmer inspection]                                  │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- Carte sans chrome inutile
- 1 décision par carte
- CTA principal unique
- Conséquences claires

---

### 2.5 Carte Décisionnelle

**Position** : Centre droit desktop / Après recommandation mobile  
**Largeur** : 6 colonnes desktop / 100% mobile

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ 🗺️  BASSIN D'ARCACHON                    [Layers ▾]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         ●  Ferret-02 (ALERTE)                          │
│            Halo incertitude: ±0.5°C                     │
│                                                         │
│      ●  Arcachon-01 (OK)                               │
│                                                         │
│   [Sentinel-3 overlay]                                  │
│   Température surface: 18.5°C ±0.3°C                    │
│                                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- Pas une carte SIG brute
- Carte orientée action
- Layers utiles à la décision immédiate visibles par défaut
- Détails avancés en second niveau

**Layers Disponibles** :
- Stations in-situ
- Zones surveillées
- Sentinel-3 proxy
- Halos d'incertitude
- Foyers de dérive
- Trajectoire propagation

---

### 2.6 Bloc "Signaux de Confiance"

**Position** : À côté ou sous la carte  
**Hauteur** : Auto (min 100px)

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ 📊 CONFIANCE                                            │
├─────────────────────────────────────────────────────────┤
│ Modèle : ████████░░ 87%                                 │
│ Qualité capteurs : ██████████ 98%                       │
│ Cohérence inter-sources : ███████░░░ 76%                │
│ Fraîcheur données : ████████░░ 85% (2min)               │
│ Stabilité prédiction : ██████░░░░ 65%                   │
│                                                         │
│ ⚠️  Incertitude élevée sur stabilité                    │
└─────────────────────────────────────────────────────────┘
```

**Codage Visuel** :
- **Saturation** = Niveau de confiance
- **Transparence** = Incertitude
- **Taille** = Importance opérationnelle
- **Motif/Texture** = Données estimées ou proxy

**Règles UX** :
- Ne jamais cacher l'incertitude
- Prédiction peu fiable visible en 1 seconde
- Warnings explicites

---

### 2.7 Bloc "Progress Ledger"

**Position** : Colonne latérale desktop / Accordéon mobile  
**Largeur** : 3 colonnes desktop / 100% mobile

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ 📋 JOURNAL OPÉRATIONNEL                                 │
├─────────────────────────────────────────────────────────┤
│ 12:45 Détection anomalie Ferret-02                      │
│       Confiance: 87%                                    │
│       Règle: TEMP_DRIFT_THRESHOLD                       │
│                                                         │
│ 12:46 Consultation Sentinel-3                           │
│       Proxy SST: 18.5°C ±0.3°C                          │
│       Cohérence: 76%                                    │
│                                                         │
│ 12:47 Comparaison capteur voisin                        │
│       Arcachon-01: 15.2°C (normal)                      │
│       Écart confirmé: +3.3°C                            │
│                                                         │
│ 12:48 Recommandation générée                            │
│       Action: Inspection physique                       │
│       Fenêtre: 20 minutes                               │
│                                                         │
│ 12:49 En attente validation opérateur...                │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- Pas de chaîne de pensée brute
- Journal opérationnel compréhensible
- Chaque étape répond à : **Quoi, Pourquoi, Confiance**
- Horodatage précis

---

### 2.8 Bloc "Contrôles Humains"

**Position** : Fixe en bas mobile / Flottant à droite desktop  
**Hauteur** : 64px mobile / Auto desktop

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ [⏸️  Interrompre] [✏️  Corriger] [❌ Annuler]            │
│                                                         │
│ [⬆️  Escalader Expert] [👤 Validation Manuelle]         │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- Actions de reprise en main toujours visibles
- Verbes de contrôle, pas décoratifs
- Design calme, pas alarmiste
- Sticky sur mobile

**Actions** :
- **Interrompre** - Stopper agent immédiatement
- **Corriger** - Modifier paramètres/plan
- **Annuler** - Annuler action en cours
- **Escalader** - Transférer à expert
- **Validation Manuelle** - Forcer approbation humaine

---

### 2.9 Bloc "Alertes en File"

**Position** : Sous carte décisionnelle  
**Hauteur** : Auto (max 400px scroll)

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ 🚨 ALERTES (3)                    [Filtres ▾] [Tri ▾]   │
├─────────────────────────────────────────────────────────┤
│ 🔴 Dérive thermique • Ferret-02 • 12:45 • 87% • OUVERT │
│    → Inspection requise                                 │
│                                                         │
│ 🟠 Baisse O₂ • Arcachon-01 • 12:30 • 72% • EN COURS    │
│    → Surveillance renforcée                             │
│                                                         │
│ 🟡 Qualité capteur • Banc-03 • 11:15 • 65% • VALIDÉ    │
│    → Maintenance planifiée                              │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- Une alerte = une ligne = une décision potentielle
- Zéro surcharge visuelle
- Tri par criticité + fraîcheur
- Filtres : zone, capteur, agent, confiance

**Format Ligne** :
- Type de dérive
- Zone/Station
- Heure
- Confiance
- Statut
- Prochaine action

---

### 2.10 Bloc "Drill-down Incident"

**Position** : Modal ou page dédiée  
**Déclenchement** : Clic sur alerte

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ INCIDENT #2024-04-18-001                        [✕]     │
├─────────────────────────────────────────────────────────┤
│ Dérive thermique - Station Ferret-02                    │
│                                                         │
│ CHRONOLOGIE                                             │
│ 12:45 Détection anomalie (+3.2°C)                       │
│ 12:46 Validation Sentinel-3 (cohérence 76%)             │
│ 12:47 Comparaison capteur voisin (écart confirmé)       │
│ 12:49 Recommandation inspection (20min)                 │
│ 13:05 Validation opérateur (Dupont)                     │
│ 13:25 Inspection physique (capteur défaillant)          │
│ 13:40 Remplacement capteur                              │
│ 14:00 Retour à la normale                               │
│                                                         │
│ COURBES                                                 │
│ [Graphique température 12h]                             │
│ [Comparaison multi-sources]                             │
│                                                         │
│ DÉCISION HUMAINE                                        │
│ Opérateur: J. Dupont                                    │
│ Action: Inspection physique confirmée                   │
│ Résultat: Capteur défaillant remplacé                   │
│                                                         │
│ [Export PDF] [Export JSON] [Fermer]                     │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- Progressive disclosure stricte
- Par défaut : résumé
- Au clic : détails analytiques
- Au second clic : données brutes et logs

---

### 2.11 Bloc "Audit Rapide"

**Position** : Sidebar ou section dédiée  
**Accès** : Toujours visible (icône 📋)

**Contenu** :
```
┌─────────────────────────────────────────────────────────┐
│ 📋 AUDIT RAPIDE                                         │
├─────────────────────────────────────────────────────────┤
│ QUI                                                     │
│ Agent: ThermalDriftDetector v2.3.1                      │
│ Opérateur: J. Dupont (Arcachon Nord)                    │
│                                                         │
│ QUOI                                                    │
│ Détection dérive thermique                              │
│ Recommandation inspection                               │
│ Validation humaine                                      │
│                                                         │
│ QUAND                                                   │
│ Détection: 2024-04-18 12:45:23 UTC                      │
│ Validation: 2024-04-18 13:05:12 UTC                     │
│                                                         │
│ DONNÉES SOURCES                                         │
│ Capteur Ferret-02: 21.4°C                               │
│ Sentinel-3 proxy: 18.5°C ±0.3°C                         │
│ Capteur Arcachon-01: 15.2°C                             │
│                                                         │
│ MODÈLE                                                  │
│ ThermalDriftModel v2.3.1                                │
│ Entraîné: 2024-03-15                                    │
│ Confiance: 87%                                          │
│                                                         │
│ [Export PDF] [Export JSON] [Preuve Cryptographique]     │
└─────────────────────────────────────────────────────────┘
```

**Règles UX** :
- L'audit n'est pas un sous-menu oublié
- Fait partie du cœur de l'expérience
- Traçabilité complète
- Export facile

---

## 3. Hiérarchie d'Information

### Niveau 1 — Réponse Immédiate (< 5s)
- État global
- Action à faire
- Niveau de confiance
- Bouton de contrôle

### Niveau 2 — Vérification (< 30s)
- Résumé des causes
- Carte
- Alertes liées
- Qualité des données

### Niveau 3 — Analyse (< 5min)
- Séries temporelles
- Comparaison inter-sources
- Historique des incidents
- Détail modèle

### Niveau 4 — Audit (< 15min)
- Logs complets
- Versions
- Preuve d'action
- Export

---

## 4. Variante Mobile-First

### Ordre de Pile Mobile

1. **Bandeau critique** (toujours visible)
2. **Intent Preview** (action immédiate)
3. **Recommandation prioritaire** (décision)
4. **Contrôles humains sticky** (reprise en main)
5. **Carte décisionnelle condensée** (contexte spatial)
6. **Alertes en file** (autres incidents)
7. **Progress Ledger en accordéon** (détails)
8. **Audit rapide** (traçabilité)

### Pourquoi c'est Clean

- Mobile sert d'abord à **agir**, pas à analyser 20 minutes
- Cibles tactiles WCAG 2.2 (min 44x44px)
- Authentification accessible
- Cohérence des aides
- Taille des cibles appropriée

---

## 5. Conformité et Sécurité

### M-23-22 - Digital-First
✅ Expérience simple et fluide  
✅ Mobile-first  
✅ Accessible by default  
✅ Secure by design  

### WCAG 2.2
✅ Contraste minimum 4.5:1  
✅ Cibles tactiles 44x44px  
✅ Navigation clavier  
✅ Lecteurs d'écran  
✅ Authentification accessible  
✅ Cohérence des aides  

### Zero Trust (NIST)
✅ Protection centrée ressources  
✅ Contrôle d'accès contextuel  
✅ Pas de confiance implicite  
✅ Vérification continue  
✅ Journalisation complète  

---

## 6. Justification Architecture

Cette architecture réduit le temps de réaction en remplaçant :

**Observer → Interpréter → Décider**

Par :

**Voir → Valider → Agir**

### Amélioration de la Confiance IA

1. **Intent Preview** - L'IA annonce son intention avant exécution
2. **Progress Ledger** - Chemin opérationnel visible sans opacité
3. **Signaux de Confiance** - Incertitude affichée, pas masquée
4. **Contrôles Humains** - Humain dans la boucle en permanence

### Résultat

Interface **digital-first, simple, mobile, accessible et secure-by-design** conforme à M-23-22, WCAG 2.2 et posture Zero Trust.

---

## 7. Prochaines Étapes

1. **Wireframes détaillés** - Page par page
2. **Design system** - Composants réutilisables
3. **Prototypes interactifs** - Figma/Sketch
4. **Tests utilisateurs** - Validation UX
5. **Implémentation** - React + TailwindCSS + shadcn/ui
