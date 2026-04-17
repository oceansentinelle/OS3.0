# Ocean Sentinel V2.0 - Wireframes Compacts

## 1. Centre de Commandement (Page Principale)

### Desktop Layout (1440px)

```
┌──────────────────────────────────────────────────────────────┐
│ [Logo] [Workspace▾] [●Status] [🔍] [🔔3] [@User]            │
├──────────────────────────────────────────────────────────────┤
│ [!] RISQUE ÉLEVÉ - Arcachon Nord                            │
│ Dérive thermique +3.2°C • 3 alertes • Validation requise    │
├──────────────────────────────────────────────────────────────┤
│ 🤖 INTENTION AGENT                    │ 🗺️ CARTE BASSIN     │
│ Objectif: Confirmer dérive Ferret-02  │                     │
│ Sources: In-situ + Sentinel-3         │  ● Ferret-02 🔴     │
│ Durée: 5min • Confiance: 87%          │  ● Arcachon-01 🟢   │
│                                       │                     │
│ [Valider] [Corriger] [Interrompre]    │  [Layers▾]          │
├───────────────────────────────────────┼─────────────────────┤
│ 🎯 ACTION PRIORITAIRE                 │ 📊 CONFIANCE        │
│ Inspecter Ferret-02 (20min)           │ Modèle: 87%         │
│ Raison: Écart +3.2°C vs moyenne       │ Capteurs: 98%       │
│ Si inaction: Perte données            │ Cohérence: 76%      │
│ [Confirmer inspection]                │ Fraîcheur: 85%      │
├───────────────────────────────────────┴─────────────────────┤
│ 🚨 ALERTES (3)                                              │
│ 🔴 Dérive thermique • Ferret-02 • 12:45 • 87% • OUVERT     │
│ 🟠 Baisse O₂ • Arcachon-01 • 12:30 • 72% • EN COURS        │
│ 🟡 Qualité capteur • Banc-03 • 11:15 • 65% • VALIDÉ        │
├─────────────────────────────────────────────────────────────┤
│ 📋 JOURNAL OPÉRATIONNEL                                     │
│ 12:45 Détection anomalie (87%)                              │
│ 12:46 Consultation Sentinel-3 (cohérence 76%)               │
│ 12:47 Comparaison capteur voisin (écart +3.3°C)             │
│ 12:48 Recommandation générée                                │
│ 12:49 En attente validation...                              │
├─────────────────────────────────────────────────────────────┤
│ [⏸️ Interrompre] [✏️ Corriger] [❌ Annuler] [⬆️ Escalader]  │
└─────────────────────────────────────────────────────────────┘
```

### Mobile Layout (375px)

```
┌─────────────────────────────┐
│ [☰] Ocean [●] [🔔3] [@]     │
├─────────────────────────────┤
│ [!] RISQUE ÉLEVÉ            │
│ Arcachon Nord               │
│ 3 alertes • Validation req. │
├─────────────────────────────┤
│ 🤖 INTENTION AGENT          │
│ Confirmer dérive Ferret-02  │
│ Confiance: 87%              │
│ [Valider] [Corriger]        │
├─────────────────────────────┤
│ 🎯 ACTION PRIORITAIRE       │
│ Inspecter Ferret-02 (20min) │
│ [Confirmer]                 │
├─────────────────────────────┤
│ 🗺️ CARTE                    │
│ ● Ferret-02 🔴              │
│ ● Arcachon-01 🟢            │
├─────────────────────────────┤
│ 🚨 ALERTES (3)              │
│ 🔴 Dérive thermique         │
│ 🟠 Baisse O₂                │
│ 🟡 Qualité capteur          │
├─────────────────────────────┤
│ [⏸️] [✏️] [❌] [⬆️]          │
└─────────────────────────────┘
```

## 2. Détail Incident

```
┌─────────────────────────────────────────────────────────┐
│ INCIDENT #2024-04-18-001                        [✕]     │
├─────────────────────────────────────────────────────────┤
│ Dérive thermique - Ferret-02                            │
│                                                         │
│ CHRONOLOGIE                                             │
│ 12:45 Détection (+3.2°C)                                │
│ 12:46 Validation Sentinel-3 (76%)                       │
│ 12:49 Recommandation inspection                         │
│ 13:05 Validation opérateur (Dupont)                     │
│ 13:25 Capteur défaillant identifié                      │
│ 14:00 Retour normal                                     │
│                                                         │
│ [Graphique température 12h]                             │
│                                                         │
│ DÉCISION                                                │
│ Opérateur: J. Dupont                                    │
│ Action: Remplacement capteur                            │
│                                                         │
│ [Export PDF] [Export JSON]                              │
└─────────────────────────────────────────────────────────┘
```

## 3. Agents IA

```
┌─────────────────────────────────────────────────────────┐
│ AGENTS IA ACTIFS (3)                                    │
├─────────────────────────────────────────────────────────┤
│ 🤖 ThermalDriftDetector v2.3.1          [●] ACTIF       │
│    Surveillance: 5 stations                             │
│    Confiance moyenne: 87%                               │
│    Dernière détection: 12:45                            │
│    [Voir détails →]                                     │
├─────────────────────────────────────────────────────────┤
│ 🤖 OxygenDropDetector v1.8.2            [●] ACTIF       │
│    Surveillance: 5 stations                             │
│    Confiance moyenne: 92%                               │
│    Dernière détection: 12:30                            │
│    [Voir détails →]                                     │
├─────────────────────────────────────────────────────────┤
│ 🤖 QualitySensorMonitor v3.1.0          [●] ACTIF       │
│    Surveillance: 8 capteurs                             │
│    Confiance moyenne: 95%                               │
│    Dernière alerte: 11:15                               │
│    [Voir détails →]                                     │
└─────────────────────────────────────────────────────────┘
```

## 4. Audit

```
┌─────────────────────────────────────────────────────────┐
│ JOURNAL D'AUDIT                     [Filtres▾] [Export] │
├─────────────────────────────────────────────────────────┤
│ 2024-04-18 13:05:12 UTC                                 │
│ DÉCISION HUMAINE                                        │
│ Opérateur: J. Dupont (Arcachon Nord)                    │
│ Action: Validation inspection Ferret-02                 │
│ Incident: #2024-04-18-001                               │
│ [Voir détails →]                                        │
├─────────────────────────────────────────────────────────┤
│ 2024-04-18 12:48:45 UTC                                 │
│ DÉCISION IA                                             │
│ Agent: ThermalDriftDetector v2.3.1                      │
│ Recommandation: Inspection Ferret-02 (20min)            │
│ Confiance: 87%                                          │
│ [Voir détails →]                                        │
├─────────────────────────────────────────────────────────┤
│ 2024-04-18 12:45:23 UTC                                 │
│ DÉTECTION                                               │
│ Agent: ThermalDriftDetector v2.3.1                      │
│ Anomalie: Dérive thermique +3.2°C                       │
│ Station: Ferret-02                                      │
│ [Voir détails →]                                        │
└─────────────────────────────────────────────────────────┘
```

## 5. Principes UX Clés

### Hiérarchie Information
1. **Niveau 1** (< 5s): État, Action, Confiance, Contrôle
2. **Niveau 2** (< 30s): Causes, Carte, Alertes, Qualité
3. **Niveau 3** (< 5min): Séries, Comparaisons, Historique
4. **Niveau 4** (< 15min): Logs, Versions, Preuves

### Conformité
- **M-23-22**: Digital-first, Mobile, Simple
- **WCAG 2.2**: Contraste 4.5:1, Cibles 44px, Clavier
- **Zero Trust**: Contexte, Vérification, Audit

### Codes Couleur
- 🔴 Critique (rouge saturé)
- 🟠 Élevé (orange saturé)
- 🟡 Attention (jaune désaturé)
- 🟢 Normal (vert désaturé)
