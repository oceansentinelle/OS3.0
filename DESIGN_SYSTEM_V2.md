# Ocean Sentinel V2.0 - Design System

## Vision

Design System pour **poste de commandement agentique** orienté décision rapide.

**Principes** :
- Clarté > Décoration
- Confiance > Mystère
- Action > Contemplation
- Mobile-first
- Accessible by default (WCAG 2.2 AA)

---

## 1. Tokens de Design

### 1.1 Couleurs

#### Palette Primaire

```css
/* Brand */
--os-brand-primary: #0066CC;      /* Bleu océan */
--os-brand-secondary: #00A3E0;    /* Bleu clair */
--os-brand-dark: #003D7A;         /* Bleu profond */

/* Neutral */
--os-neutral-50: #F8FAFC;
--os-neutral-100: #F1F5F9;
--os-neutral-200: #E2E8F0;
--os-neutral-300: #CBD5E1;
--os-neutral-400: #94A3B8;
--os-neutral-500: #64748B;
--os-neutral-600: #475569;
--os-neutral-700: #334155;
--os-neutral-800: #1E293B;
--os-neutral-900: #0F172A;
```

#### Palette Sémantique - États de Risque

```css
/* Critical - Rouge saturé */
--os-critical-50: #FEF2F2;
--os-critical-100: #FEE2E2;
--os-critical-500: #EF4444;       /* Alerte critique */
--os-critical-600: #DC2626;
--os-critical-700: #B91C1C;
--os-critical-900: #7F1D1D;

/* High - Orange saturé */
--os-high-50: #FFF7ED;
--os-high-100: #FFEDD5;
--os-high-500: #F97316;           /* Risque élevé */
--os-high-600: #EA580C;
--os-high-700: #C2410C;

/* Attention - Jaune désaturé */
--os-attention-50: #FEFCE8;
--os-attention-100: #FEF9C3;
--os-attention-500: #EAB308;      /* Attention */
--os-attention-600: #CA8A04;
--os-attention-700: #A16207;

/* Normal - Vert désaturé */
--os-normal-50: #F0FDF4;
--os-normal-100: #DCFCE7;
--os-normal-500: #22C55E;         /* Normal */
--os-normal-600: #16A34A;
--os-normal-700: #15803D;
```

#### Palette Fonctionnelle

```css
/* Success */
--os-success-500: #10B981;
--os-success-600: #059669;

/* Info */
--os-info-500: #3B82F6;
--os-info-600: #2563EB;

/* Warning */
--os-warning-500: #F59E0B;
--os-warning-600: #D97706;

/* Error */
--os-error-500: #EF4444;
--os-error-600: #DC2626;
```

#### Palette Confiance IA

```css
/* High Confidence - Vert saturé */
--os-confidence-high: #10B981;

/* Medium Confidence - Jaune */
--os-confidence-medium: #F59E0B;

/* Low Confidence - Orange */
--os-confidence-low: #F97316;

/* Very Low Confidence - Rouge */
--os-confidence-verylow: #EF4444;

/* Uncertainty - Gris avec transparence */
--os-uncertainty: rgba(148, 163, 184, 0.3);
```

---

### 1.2 Typographie

#### Familles

```css
/* Primary - Interface */
--os-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace - Code, données */
--os-font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

/* Numeric - Métriques */
--os-font-numeric: 'Roboto Mono', monospace;
```

#### Échelle Typographique

```css
/* Display */
--os-text-display: 3rem;          /* 48px - Titres hero */
--os-text-display-weight: 700;

/* H1 */
--os-text-h1: 2.25rem;            /* 36px */
--os-text-h1-weight: 700;

/* H2 */
--os-text-h2: 1.875rem;           /* 30px */
--os-text-h2-weight: 600;

/* H3 */
--os-text-h3: 1.5rem;             /* 24px */
--os-text-h3-weight: 600;

/* H4 */
--os-text-h4: 1.25rem;            /* 20px */
--os-text-h4-weight: 600;

/* Body Large */
--os-text-lg: 1.125rem;           /* 18px */
--os-text-lg-weight: 400;

/* Body */
--os-text-base: 1rem;             /* 16px */
--os-text-base-weight: 400;

/* Body Small */
--os-text-sm: 0.875rem;           /* 14px */
--os-text-sm-weight: 400;

/* Caption */
--os-text-xs: 0.75rem;            /* 12px */
--os-text-xs-weight: 500;

/* Line Heights */
--os-leading-tight: 1.25;
--os-leading-normal: 1.5;
--os-leading-relaxed: 1.75;
```

---

### 1.3 Espacements

```css
/* Échelle 4px */
--os-space-1: 0.25rem;    /* 4px */
--os-space-2: 0.5rem;     /* 8px */
--os-space-3: 0.75rem;    /* 12px */
--os-space-4: 1rem;       /* 16px */
--os-space-5: 1.25rem;    /* 20px */
--os-space-6: 1.5rem;     /* 24px */
--os-space-8: 2rem;       /* 32px */
--os-space-10: 2.5rem;    /* 40px */
--os-space-12: 3rem;      /* 48px */
--os-space-16: 4rem;      /* 64px */
--os-space-20: 5rem;      /* 80px */
```

---

### 1.4 Radius

```css
--os-radius-none: 0;
--os-radius-sm: 0.25rem;    /* 4px - Badges */
--os-radius-md: 0.5rem;     /* 8px - Cartes, boutons */
--os-radius-lg: 0.75rem;    /* 12px - Modals */
--os-radius-xl: 1rem;       /* 16px - Sections */
--os-radius-full: 9999px;   /* Pilules */
```

---

### 1.5 Ombres

```css
/* Minimalistes - Design calme */
--os-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--os-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--os-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--os-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* Ombres critiques - Alertes */
--os-shadow-critical: 0 4px 12px 0 rgba(239, 68, 68, 0.2);
--os-shadow-high: 0 4px 12px 0 rgba(249, 115, 22, 0.2);
```

---

### 1.6 Transitions

```css
--os-transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--os-transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
--os-transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
```

---

### 1.7 Breakpoints

```css
/* Mobile-first */
--os-screen-sm: 640px;    /* Tablette portrait */
--os-screen-md: 768px;    /* Tablette paysage */
--os-screen-lg: 1024px;   /* Desktop */
--os-screen-xl: 1280px;   /* Desktop large */
--os-screen-2xl: 1536px;  /* Desktop XL */
```

---

## 2. Composants UI de Base

### 2.1 Button

#### Variantes

**Primary** - Actions principales
```tsx
<Button variant="primary">
  Valider
</Button>
```

**Secondary** - Actions secondaires
```tsx
<Button variant="secondary">
  Annuler
</Button>
```

**Destructive** - Actions dangereuses
```tsx
<Button variant="destructive">
  Interrompre
</Button>
```

**Ghost** - Actions tertiaires
```tsx
<Button variant="ghost">
  Détails
</Button>
```

**Link** - Liens texte
```tsx
<Button variant="link">
  En savoir plus →
</Button>
```

#### Tailles

```tsx
<Button size="sm">Small</Button>      /* 32px height */
<Button size="md">Medium</Button>     /* 40px height - défaut */
<Button size="lg">Large</Button>      /* 48px height */
```

#### États

```css
/* Default */
background: var(--os-brand-primary);
color: white;

/* Hover */
background: var(--os-brand-dark);

/* Focus */
outline: 2px solid var(--os-brand-primary);
outline-offset: 2px;

/* Disabled */
opacity: 0.5;
cursor: not-allowed;

/* Loading */
opacity: 0.7;
cursor: wait;
/* + spinner icon */

/* Critical (pour Interrompre, Annuler) */
background: var(--os-critical-500);
hover: var(--os-critical-600);
```

#### Accessibilité

- Taille minimale tactile : **44x44px** (WCAG 2.2)
- Contraste texte/fond : **4.5:1 minimum**
- Focus visible obligatoire
- États disabled avec `aria-disabled`
- Loading avec `aria-busy`

---

### 2.2 Card

#### Variantes

**Default** - Carte standard
```tsx
<Card>
  <CardHeader>
    <CardTitle>Titre</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Contenu
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

**Elevated** - Carte surélevée
```tsx
<Card variant="elevated">
  ...
</Card>
```

**Outlined** - Carte bordure
```tsx
<Card variant="outlined">
  ...
</Card>
```

#### États Sémantiques

```tsx
<Card status="critical">   /* Bordure rouge */
<Card status="high">       /* Bordure orange */
<Card status="attention">  /* Bordure jaune */
<Card status="normal">     /* Bordure verte */
```

---

### 2.3 Badge

#### Variantes

```tsx
<Badge variant="default">Default</Badge>
<Badge variant="critical">Critique</Badge>
<Badge variant="high">Élevé</Badge>
<Badge variant="attention">Attention</Badge>
<Badge variant="normal">Normal</Badge>
<Badge variant="outline">Outline</Badge>
```

#### Tailles

```tsx
<Badge size="sm">Small</Badge>
<Badge size="md">Medium</Badge>
<Badge size="lg">Large</Badge>
```

---

### 2.4 Input

#### Types

```tsx
<Input type="text" placeholder="Email" />
<Input type="password" placeholder="Mot de passe" />
<Input type="number" placeholder="Seuil" />
<Input type="search" placeholder="Rechercher..." />
```

#### États

```tsx
<Input error="Champ requis" />
<Input disabled />
<Input readOnly />
```

#### Accessibilité

- Label obligatoire (visible ou `aria-label`)
- Erreurs avec `aria-invalid` et `aria-describedby`
- Taille minimale : **44px height**

---

### 2.5 Alert

#### Variantes

```tsx
<Alert variant="info">
  <AlertTitle>Information</AlertTitle>
  <AlertDescription>Message informatif</AlertDescription>
</Alert>

<Alert variant="success">...</Alert>
<Alert variant="warning">...</Alert>
<Alert variant="error">...</Alert>
```

#### Avec Action

```tsx
<Alert variant="warning">
  <AlertTitle>Attention</AlertTitle>
  <AlertDescription>Dérive détectée</AlertDescription>
  <AlertAction>
    <Button size="sm">Voir détails</Button>
  </AlertAction>
</Alert>
```

---

### 2.6 Table

#### Structure

```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Station</TableHead>
      <TableHead>Température</TableHead>
      <TableHead>Statut</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Ferret-02</TableCell>
      <TableCell>21.4°C</TableCell>
      <TableCell><Badge variant="critical">Alerte</Badge></TableCell>
    </TableRow>
  </TableBody>
</Table>
```

#### Responsive

Mobile : Passer en cartes empilées
Desktop : Table classique

---

### 2.7 Tabs

```tsx
<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
    <TabsTrigger value="details">Détails</TabsTrigger>
    <TabsTrigger value="history">Historique</TabsTrigger>
  </TabsList>
  <TabsContent value="overview">
    Contenu vue d'ensemble
  </TabsContent>
  <TabsContent value="details">
    Contenu détails
  </TabsContent>
</Tabs>
```

---

### 2.8 Sheet / Drawer

#### Mobile Drawer (bottom)

```tsx
<Sheet>
  <SheetTrigger>Ouvrir</SheetTrigger>
  <SheetContent side="bottom">
    <SheetHeader>
      <SheetTitle>Titre</SheetTitle>
      <SheetDescription>Description</SheetDescription>
    </SheetHeader>
    Contenu
  </SheetContent>
</Sheet>
```

#### Desktop Drawer (right)

```tsx
<Sheet>
  <SheetContent side="right">
    ...
  </SheetContent>
</Sheet>
```

---

## 3. Composants Métier Ocean Sentinel

### 3.1 IntentPreview

**Objectif** : Afficher l'intention de l'agent avant exécution

```tsx
<IntentPreview
  agent="ThermalDriftDetector v2.3.1"
  objective="Confirmer dérive thermique Ferret-02"
  sources={["Capteur in-situ", "Sentinel-3 proxy"]}
  duration="5 minutes"
  confidence={87}
  impact="Validation ou infirmation anomalie"
  onValidate={() => {}}
  onCorrect={() => {}}
  onInterrupt={() => {}}
  onDefer={() => {}}
/>
```

#### Structure

```
┌─────────────────────────────────────────────────┐
│ 🤖 INTENTION DE L'AGENT                         │
├─────────────────────────────────────────────────┤
│ Agent: ThermalDriftDetector v2.3.1              │
│ Objectif: Confirmer dérive thermique Ferret-02  │
│ Sources: Capteur in-situ + Sentinel-3 proxy     │
│ Durée estimée: 5 minutes                        │
│ Confiance: 87%                                  │
│                                                 │
│ Impact attendu: Validation ou infirmation       │
│                                                 │
│ [Valider] [Corriger] [Interrompre] [Différer]  │
└─────────────────────────────────────────────────┘
```

#### États

- **Pending** - En attente validation
- **Validated** - Validé par opérateur
- **Corrected** - Modifié par opérateur
- **Interrupted** - Interrompu
- **Deferred** - Différé

---

### 3.2 ProgressLedger

**Objectif** : Journal opérationnel du raisonnement agent

```tsx
<ProgressLedger
  steps={[
    {
      timestamp: "12:45:23",
      type: "detection",
      message: "Détection anomalie Ferret-02",
      confidence: 87,
      rule: "TEMP_DRIFT_THRESHOLD"
    },
    {
      timestamp: "12:46:15",
      type: "validation",
      message: "Consultation Sentinel-3",
      confidence: 76,
      data: { sst: "18.5°C ±0.3°C" }
    },
    // ...
  ]}
/>
```

#### Structure

```
┌─────────────────────────────────────────────────┐
│ 📋 JOURNAL OPÉRATIONNEL                         │
├─────────────────────────────────────────────────┤
│ 12:45 Détection anomalie Ferret-02              │
│       Confiance: 87%                            │
│       Règle: TEMP_DRIFT_THRESHOLD               │
│                                                 │
│ 12:46 Consultation Sentinel-3                   │
│       Proxy SST: 18.5°C ±0.3°C                  │
│       Cohérence: 76%                            │
│                                                 │
│ 12:47 Comparaison capteur voisin                │
│       Arcachon-01: 15.2°C (normal)              │
│       Écart confirmé: +3.3°C                    │
│                                                 │
│ 12:48 Recommandation générée                    │
│       Action: Inspection physique               │
│       Fenêtre: 20 minutes                       │
└─────────────────────────────────────────────────┘
```

---

### 3.3 ConfidenceSignal

**Objectif** : Afficher signaux de confiance avec incertitude

```tsx
<ConfidenceSignal
  model={87}
  sensors={98}
  coherence={76}
  freshness={85}
  stability={65}
  warnings={["Incertitude élevée sur stabilité"]}
/>
```

#### Codage Visuel

- **Saturation** = Niveau de confiance (0-100%)
- **Transparence** = Incertitude
- **Couleur** = Vert (>80%), Jaune (60-80%), Orange (40-60%), Rouge (<40%)

```
┌─────────────────────────────────────────────────┐
│ 📊 CONFIANCE                                    │
├─────────────────────────────────────────────────┤
│ Modèle:           ████████░░ 87%                │
│ Qualité capteurs: ██████████ 98%                │
│ Cohérence:        ███████░░░ 76%                │
│ Fraîcheur:        ████████░░ 85% (2min)         │
│ Stabilité:        ██████░░░░ 65%                │
│                                                 │
│ ⚠️  Incertitude élevée sur stabilité            │
└─────────────────────────────────────────────────┘
```

---

### 3.4 AlertRow

**Objectif** : Ligne d'alerte dans file

```tsx
<AlertRow
  severity="critical"
  type="Dérive thermique"
  station="Ferret-02"
  timestamp="12:45"
  confidence={87}
  status="open"
  nextAction="Inspection requise"
  onClick={() => {}}
/>
```

#### Structure

```
🔴 Dérive thermique • Ferret-02 • 12:45 • 87% • OUVERT
   → Inspection requise
```

#### Variantes Severity

- `critical` - 🔴 Rouge saturé
- `high` - 🟠 Orange saturé
- `attention` - 🟡 Jaune désaturé
- `normal` - 🟢 Vert désaturé

---

### 3.5 ActionCard

**Objectif** : Carte de recommandation prioritaire

```tsx
<ActionCard
  priority={1}
  title="Inspecter station Ferret-02"
  reason="Écart +3.2°C vs moyenne saisonnière"
  window="20 minutes"
  operator="Équipe Arcachon Nord"
  consequence="Risque de perte de données critiques"
  onConfirm={() => {}}
/>
```

#### Structure

```
┌─────────────────────────────────────────────────┐
│ 🎯 ACTION PRIORITAIRE                           │
├─────────────────────────────────────────────────┤
│ Inspecter station Ferret-02                     │
│                                                 │
│ Raison: Écart +3.2°C vs moyenne saisonnière     │
│ Fenêtre: 20 minutes                             │
│ Opérateur: Équipe Arcachon Nord                 │
│                                                 │
│ Si inaction: Risque de perte de données         │
│                                                 │
│ [Confirmer inspection]                          │
└─────────────────────────────────────────────────┘
```

---

### 3.6 AuditTrail

**Objectif** : Entrée de journal d'audit

```tsx
<AuditTrail
  timestamp="2024-04-18 13:05:12 UTC"
  type="human_decision"
  operator="J. Dupont"
  role="Arcachon Nord"
  action="Validation inspection Ferret-02"
  incident="#2024-04-18-001"
  onViewDetails={() => {}}
/>
```

#### Structure

```
┌─────────────────────────────────────────────────┐
│ 2024-04-18 13:05:12 UTC                         │
│ DÉCISION HUMAINE                                │
│ Opérateur: J. Dupont (Arcachon Nord)            │
│ Action: Validation inspection Ferret-02         │
│ Incident: #2024-04-18-001                       │
│ [Voir détails →]                                │
└─────────────────────────────────────────────────┘
```

---

### 3.7 RiskBanner

**Objectif** : Bandeau de situation critique

```tsx
<RiskBanner
  level="high"
  zone="Arcachon Nord"
  alerts={3}
  activeAgents={2}
  lastSync="2min"
  summary="Dérive thermique + baisse O₂ nécessitent validation opérateur"
/>
```

#### Structure

```
┌─────────────────────────────────────────────────┐
│ [!] RISQUE ÉLEVÉ                                │
│                                                 │
│ Arcachon Nord - Dérive thermique + baisse O₂   │
│ 3 alertes ouvertes • 2 agents actifs • 2min     │
│                                                 │
│ → Validation opérateur requise                 │
└─────────────────────────────────────────────────┘
```

#### Niveaux

- `critical` - Rouge saturé, texte blanc
- `high` - Orange saturé, texte blanc
- `attention` - Jaune désaturé, texte noir
- `normal` - Vert désaturé, texte noir

---

### 3.8 DecisionMap

**Objectif** : Carte décisionnelle (pas SIG brut)

```tsx
<DecisionMap
  center={[44.65, -1.25]}
  zoom={11}
  stations={[
    { id: "ferret-02", status: "critical", temp: 21.4 },
    { id: "arcachon-01", status: "normal", temp: 15.2 }
  ]}
  layers={["stations", "sentinel3", "uncertainty"]}
  onStationClick={(id) => {}}
/>
```

#### Layers Disponibles

- `stations` - Stations in-situ
- `zones` - Zones surveillées
- `sentinel3` - Overlay Sentinel-3
- `uncertainty` - Halos d'incertitude
- `drift` - Foyers de dérive
- `trajectory` - Trajectoire propagation

---

## 4. Conventions Desktop / Mobile

### 4.1 Layout

**Desktop** (≥1024px)
- Grille 12 colonnes
- Sidebar fixe 280px
- Contenu principal fluide
- Modals centrées

**Mobile** (<1024px)
- Pile verticale
- Sidebar → Bottom sheet
- Sticky header 56px
- Sticky controls 64px

---

### 4.2 Navigation

**Desktop**
- Sidebar avec sections
- Breadcrumbs
- Tabs horizontales

**Mobile**
- Bottom navigation (5 items max)
- Hamburger menu
- Tabs scrollables

---

### 4.3 Interactions

**Desktop**
- Hover states
- Tooltips
- Context menus
- Drag & drop

**Mobile**
- Tap (44x44px min)
- Swipe
- Long press
- Pull to refresh

---

## 5. États Critiques

### 5.1 Confiance IA

```tsx
/* High (>80%) */
color: var(--os-confidence-high);
opacity: 1;

/* Medium (60-80%) */
color: var(--os-confidence-medium);
opacity: 0.9;

/* Low (40-60%) */
color: var(--os-confidence-low);
opacity: 0.8;

/* Very Low (<40%) */
color: var(--os-confidence-verylow);
opacity: 0.7;
```

---

### 5.2 Incertitude

```tsx
/* Données estimées ou proxy */
background-pattern: diagonal-stripes;
opacity: 0.7;

/* Incertitude quantifiée */
text: "±0.3°C";
color: var(--os-neutral-500);
```

---

### 5.3 Loading

```tsx
/* Skeleton */
background: linear-gradient(
  90deg,
  var(--os-neutral-200) 25%,
  var(--os-neutral-100) 50%,
  var(--os-neutral-200) 75%
);
animation: shimmer 2s infinite;

/* Spinner */
border: 2px solid var(--os-neutral-200);
border-top-color: var(--os-brand-primary);
animation: spin 1s linear infinite;
```

---

### 5.4 Empty States

```tsx
<EmptyState
  icon="📊"
  title="Aucune alerte"
  description="Toutes les stations fonctionnent normalement"
  action={<Button>Voir historique</Button>}
/>
```

---

### 5.5 Error States

```tsx
<ErrorState
  icon="⚠️"
  title="Erreur de connexion"
  description="Impossible de récupérer les données"
  action={<Button onClick={retry}>Réessayer</Button>}
/>
```

---

## 6. Accessibilité WCAG 2.2 AA

### 6.1 Contraste

- Texte normal : **4.5:1 minimum**
- Texte large (≥18px) : **3:1 minimum**
- Composants UI : **3:1 minimum**

### 6.2 Cibles Tactiles

- Taille minimale : **44x44px**
- Espacement : **8px minimum**

### 6.3 Navigation Clavier

- Tous les composants accessibles au clavier
- Focus visible obligatoire (outline 2px)
- Ordre de tabulation logique
- Skip links pour navigation rapide

### 6.4 ARIA

```tsx
/* Boutons */
<button aria-label="Interrompre l'agent">
  <StopIcon />
</button>

/* États */
<div role="alert" aria-live="assertive">
  Alerte critique détectée
</div>

/* Loading */
<button aria-busy="true" aria-label="Chargement...">
  <Spinner />
</button>

/* Disabled */
<button aria-disabled="true">
  Action indisponible
</button>
```

### 6.5 Couleur

- Ne jamais utiliser la couleur seule
- Toujours ajouter icône ou texte
- Motifs/textures pour données estimées

---

## 7. Nomenclature

### 7.1 Composants

```
os-button
os-card
os-badge
os-input
os-alert
os-table
os-tabs
os-sheet
os-intent-preview
os-progress-ledger
os-confidence-signal
os-alert-row
os-action-card
os-audit-trail
os-risk-banner
os-decision-map
```

### 7.2 Variantes

```
variant="primary"
variant="secondary"
variant="destructive"
variant="ghost"
variant="link"
variant="critical"
variant="high"
variant="attention"
variant="normal"
```

### 7.3 Tailles

```
size="sm"
size="md"
size="lg"
```

### 7.4 États

```
state="default"
state="hover"
state="focus"
state="disabled"
state="loading"
state="error"
```

---

## 8. Livrables

### 8.1 Figma

- [ ] Tokens de design
- [ ] Composants UI base (8)
- [ ] Composants métier (8)
- [ ] Variantes desktop/mobile
- [ ] États complets
- [ ] Documentation inline

### 8.2 Code (React + Tailwind + shadcn/ui)

```
components/
├── ui/
│   ├── button.tsx
│   ├── card.tsx
│   ├── badge.tsx
│   ├── input.tsx
│   ├── alert.tsx
│   ├── table.tsx
│   ├── tabs.tsx
│   └── sheet.tsx
├── os/
│   ├── intent-preview.tsx
│   ├── progress-ledger.tsx
│   ├── confidence-signal.tsx
│   ├── alert-row.tsx
│   ├── action-card.tsx
│   ├── audit-trail.tsx
│   ├── risk-banner.tsx
│   └── decision-map.tsx
└── lib/
    ├── tokens.ts
    ├── utils.ts
    └── cn.ts
```

---

## 9. Prochaines Étapes

1. ✅ **Design System défini**
2. → **Créer UI kit Figma**
3. → **Implémenter composants React**
4. → **Tests accessibilité**
5. → **Documentation Storybook**

---

**Le Design System Ocean Sentinel V2.0 est maintenant complet et prêt pour implémentation Figma + React !** 🎨🚀
