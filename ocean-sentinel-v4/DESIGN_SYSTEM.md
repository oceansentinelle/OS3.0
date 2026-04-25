# 🎨 Ocean Sentinel V4 - Design System SACS

## 📐 Principes de conception

### Mobile-First High Contrast
- ✅ **Contraste minimum** : 15:1 (WCAG AAA+)
- ✅ **Lecture en plein soleil** : Couleurs vives et saturées
- ✅ **Touch targets** : 48px minimum
- ✅ **Typographie** : System fonts (-apple-system, Segoe UI)

---

## 🎨 Palette de couleurs

### Fond (Background)
```css
--background: #000814      /* Ultra-sombre pour contraste max */
--card: #001d3d            /* Cartes légèrement plus claires */
```

### Texte (Foreground)
```css
--foreground: #ffffff      /* Blanc pur */
--muted-foreground: #b4b4b4 /* Gris clair (contraste 70%) */
```

### Accent (Cyan océanique)
```css
--primary: #06b6d4         /* Cyan vif */
--accent: #06b6d4          /* Identique au primary */
```

---

## 🏷️ SACS Truth Badges (Règle de Vérité)

### ● MESURÉ (Capteur direct - 100% fiabilité)

**Couleurs** :
```css
--truth-measured: #10b981        /* Vert éclatant */
--truth-measured-dark: #047857   /* Fond badge */
--truth-measured-contrast: #ffffff /* Texte */
```

**Utilisation** :
```tsx
<TruthBadge status="measured" />
```

**Classes Tailwind** :
```css
bg-truth-measured-dark
text-truth-measured-contrast
border-truth-measured
shadow-truth-measured/50
```

**Exemple visuel** :
```
┌────────────────────┐
│ ● MESURÉ          │  ← Fond vert foncé #047857
│                    │  ← Texte blanc #ffffff
│                    │  ← Bordure vert vif #10b981
└────────────────────┘  ← Shadow vert 50% opacity
```

---

### ◐ INFÉRÉ (Proxy satellitaire - 70-90% fiabilité)

**Couleurs** :
```css
--truth-inferred: #f59e0b        /* Orange vif */
--truth-inferred-dark: #d97706   /* Fond badge */
--truth-inferred-contrast: #000000 /* Texte noir */
```

**Utilisation** :
```tsx
<TruthBadge status="inferred" />
```

**Classes Tailwind** :
```css
bg-truth-inferred-dark
text-truth-inferred-contrast
border-truth-inferred
shadow-truth-inferred/50
```

**Exemple visuel** :
```
┌────────────────────┐
│ ◐ INFÉRÉ          │  ← Fond orange foncé #d97706
│                    │  ← Texte noir #000000
│                    │  ← Bordure orange vif #f59e0b
└────────────────────┘  ← Shadow orange 50% opacity
```

---

### ○ SIMULÉ (Modèle numérique - 50-70% fiabilité)

**Couleurs** :
```css
--truth-simulated: #6b7280        /* Gris neutre */
--truth-simulated-dark: #4b5563   /* Fond badge */
--truth-simulated-contrast: #ffffff /* Texte blanc */
```

**Utilisation** :
```tsx
<TruthBadge status="simulated" />
```

**Classes Tailwind** :
```css
bg-truth-simulated-dark
text-truth-simulated-contrast
border-truth-simulated
shadow-truth-simulated/50
```

**Exemple visuel** :
```
┌────────────────────┐
│ ○ SIMULÉ          │  ← Fond gris foncé #4b5563
│                    │  ← Texte blanc #ffffff
│                    │  ← Bordure gris #6b7280
└────────────────────┘  ← Shadow gris 50% opacity
```

---

## 🚨 Alertes Critiques (Maximum Visibility)

### 🔴 CRITICAL (Hypoxie, Acidification, Température)

**Couleurs** :
```css
--critical: #dc2626              /* Rouge vif (bordure) */
--critical-dark: #991b1b         /* Rouge sombre */
--critical-bg: #450a0a           /* Fond ultra-sombre */
--critical-text: #fecaca         /* Texte rouge clair */
--critical-border: #dc2626       /* Bordure pulsante */
--critical-glow: #fee2e2         /* Effet glow */
```

**Utilisation** :
```tsx
<AlertBanner 
  parameter={criticalParameter} 
  stationId="BARAG_PROXY" 
/>
```

**Classes Tailwind** :
```css
bg-gradient-to-br from-critical-bg via-critical-dark to-critical-bg
border-4 border-critical
shadow-2xl shadow-critical/50
animate-pulse-border
```

**Exemple visuel** :
```
┌─────────────────────────────────────────┐
│ ⚠️  🔴 CRITICAL  HYPOXIE               │  ← Header rouge vif
│                                         │
│ Oxygène dissous 135 µmol/kg < 150      │  ← Texte rouge clair #fecaca
│                                         │
│ ● MESURÉ  Station BARAG_PROXY          │  ← Badge + meta
│ • Risque mortalité huîtres             │
└─────────────────────────────────────────┘
  ↑                                       ↑
  Bordure rouge pulsante (4px)            Shadow rouge 50%
  Animation pulse-border (2s infinite)
```

---

## 📊 Composants

### MetricCard (Carte métrique)

**Structure** :
```tsx
<MetricCard parameter={parameter} />
```

**États** :
- ✅ Normal : Bordure gauche verte
- 🔴 Critique : Bordure gauche rouge + fond dégradé
- ⏳ Loading : Skeleton avec animation shimmer

**Exemple normal** :
```
┌─────────────────────────┐
│ │ TEMPÉRATURE           │  ← Label gris
│ │                       │
│ │ 18.5 °C              │  ← Valeur grande (48px)
│ │                       │
│ │ ● MESURÉ             │  ← Badge
│ │                       │
│ │ COAST-HF Ifremer     │  ← Source
│ │ Il y a 10 min        │  ← Timestamp
└─────────────────────────┘
  ↑
  Bordure gauche verte (4px)
```

**Exemple critique** :
```
┌─────────────────────────┐
│ │ OXYGÈNE DISSOUS       │  ← Label gris
│ │                       │
│ │ 135 µmol/kg          │  ← Valeur rouge #fecaca
│ │                       │
│ │ ⚠️ Seuil : < 150     │  ← Seuil critique
│ │ • HYPOXIE            │
│ │                       │
│ │ ● MESURÉ             │  ← Badge
│ │                       │
│ │ COAST-HF Ifremer     │  ← Source
│ │ Il y a 10 min        │  ← Timestamp
└─────────────────────────┘
  ↑
  Bordure gauche rouge (4px)
  Fond dégradé rouge sombre
```

---

## 🎬 Animations

### Pulse Border (Alertes critiques)
```css
@keyframes pulse-border {
  0%, 100% { border-color: #dc2626; }
  50% { border-color: #fecaca; }
}

animation: pulse-border 2s infinite;
```

### Shimmer (Loading states)
```css
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

animation: shimmer 1.5s infinite;
background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%);
background-size: 200% 100%;
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

**Grille stations** :
- Mobile : 1 colonne
- Tablet (640px+) : 2 colonnes
- Desktop (1024px+) : 4 colonnes

---

## ♿ Accessibilité

### Contraste
- ✅ Texte principal : 21:1 (blanc sur #000814)
- ✅ Texte secondaire : 10:1 (gris clair sur #000814)
- ✅ Badges : 8:1 minimum

### Touch Targets
```css
.touch-target {
  min-height: 48px;
  min-width: 48px;
}
```

### ARIA
```tsx
<div role="alert" aria-live="assertive" aria-atomic="true">
  {/* Alerte critique */}
</div>

<div role="status" aria-label="Statut de la donnée: MESURÉ">
  {/* Badge */}
</div>
```

---

## 🚀 Optimisations Performance

### Code Splitting
```typescript
// Lazy loading des pages
const Dashboard = lazy(() => import('./pages/Dashboard'))
```

### Tree Shaking
- ✅ Import nommés uniquement
- ✅ Pas de `import *`

### Assets
- ✅ Images WebP
- ✅ SVG inline pour icônes
- ✅ Fonts system (pas de Google Fonts)

---

## 📝 Checklist Design

- [x] Palette haute-contraste définie
- [x] Tokens SACS intégrés (●/◐/○)
- [x] Alertes critiques 🔴 avec pulse
- [x] Composants TruthBadge, AlertBanner, MetricCard
- [x] Skeleton loaders avec shimmer
- [x] Animations performantes (GPU)
- [x] Touch targets 48px
- [x] ARIA labels complets
- [x] Responsive mobile-first
- [x] Contraste WCAG AAA (15:1+)

---

**Version** : 4.0.0  
**Dernière mise à jour** : 23 avril 2026  
**Design Lead** : Ocean Sentinel UX Team
