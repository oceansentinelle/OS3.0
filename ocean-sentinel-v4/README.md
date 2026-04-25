# 🌊 Ocean Sentinel V4.0 - Architecture React

## 📋 Vue d'ensemble

Application web moderne de surveillance océanographique temps réel pour le Bassin d'Arcachon.

**Stack technique** :
- ⚛️ React 18.3 + TypeScript 5.4
- ⚡ Vite 5.2 (build ultra-rapide)
- 🎨 Tailwind CSS 3.4 + shadcn/ui
- 📊 Architecture DB-First via MCP TimescaleDB
- 📱 Mobile-First strict (optimisé 512 Mo RAM)

---

## 🏗️ Architecture générée

```
ocean-sentinel-v4/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── badges/
│   │   │   └── TruthBadge.tsx          # Badges SACS (●/◐/○)
│   │   ├── dashboard/
│   │   │   ├── AlertBanner.tsx         # Alertes critiques 🔴
│   │   │   ├── MetricCard.tsx          # Cartes métriques
│   │   │   └── StationGrid.tsx         # Grille stations
│   │   ├── layout/
│   │   │   ├── Header.tsx              # Header sticky
│   │   │   ├── Navigation.tsx          # Nav desktop
│   │   │   └── BottomNav.tsx           # Nav mobile
│   │   └── ui/                         # shadcn/ui components
│   ├── lib/
│   │   ├── api.ts                      # Client API (logique métier)
│   │   ├── types.ts                    # Types TypeScript
│   │   └── utils.ts                    # Utilitaires
│   ├── pages/
│   │   ├── Home.tsx                    # Page d'accueil
│   │   ├── Dashboard.tsx               # Tableau de bord
│   │   ├── About.tsx                   # Le Projet
│   │   ├── API.tsx                     # Documentation API
│   │   └── Podcast.tsx                 # Bulletins vocaux
│   ├── styles/
│   │   └── globals.css                 # Design tokens SACS
│   ├── App.tsx                         # Router principal
│   └── main.tsx                        # Entry point
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js                  # Config Tailwind + tokens SACS
├── vite.config.ts
└── components.json                     # Config shadcn/ui
```

---

## 🎨 Design Tokens SACS (Règle de Vérité)

### Badges de fiabilité

| Statut | Badge | Couleur | Fiabilité | Source |
|--------|-------|---------|-----------|--------|
| **MESURÉ** | ● | Vert `#10b981` | 100% | Capteur direct (COAST-HF) |
| **INFÉRÉ** | ◐ | Orange `#f59e0b` | 70-90% | Proxy satellitaire (Sentinel-3) |
| **SIMULÉ** | ○ | Gris `#9ca3af` | 50-70% | Modèle numérique (MARS3D) |

### Alertes critiques

| Paramètre | Seuil | Alerte | Action |
|-----------|-------|--------|--------|
| **DOX2** | < 150 µmol/kg | 🔴 HYPOXIE | Risque mortalité huîtres |
| **PH_TOTAL** | < 7.80 | 🔴 ACIDIFICATION | Risque fragilisation coquilles |
| **TEMP** | > 25°C | 🔴 TEMPÉRATURE ÉLEVÉE | Surveiller évolution |

---

## 📊 Paramètres métier intégrés

### Stations surveillées
- `BARAG_PROXY` - Station COAST-HF Bassin d'Arcachon
- `ARCACHON_EYRAC` - Station Hub'Eau BRGM

### Variables océanographiques
- `TEMP` - Température (°C)
- `PSAL` - Salinité (PSU)
- `DOX2` - Oxygène dissous (µmol/kg)
- `PH_TOTAL` - pH Total

---

## 🚀 Installation

```bash
# Installation des dépendances
npm install

# Ajout de tailwindcss-animate (requis par shadcn/ui)
npm install -D tailwindcss-animate

# Développement local
npm run dev

# Build production
npm run build

# Preview build
npm run preview
```

---

## 🔌 Connexion API (Logique métier préservée)

L'API client (`src/lib/api.ts`) préserve la logique métier de `dashboard-dynamic.js` :

```typescript
// Récupérer les données d'une station
const data = await fetchStationData('BARAG_PROXY')

// Récupérer les alertes critiques
const alerts = await fetchCriticalAlerts()
```

**Endpoint API** : `https://oceansentinelle.fr/api/v1/station/{id}/latest`

---

## 📱 Optimisations Mobile-First

- ✅ Touch targets 48px minimum
- ✅ Safe areas iOS (viewport-fit=cover)
- ✅ Skeleton loaders avec animation shimmer
- ✅ Graceful degradation (états erreur/timeout)
- ✅ Contraste AAA (15:1 minimum)
- ✅ Optimisé 512 Mo RAM (code splitting, lazy loading)

---

## 🎯 Prochaines étapes

### ✅ ÉTAPE 1 TERMINÉE : Scaffolding
- [x] Architecture React + Vite + TypeScript
- [x] Configuration Tailwind + shadcn/ui
- [x] Types TypeScript (stations, paramètres, seuils)
- [x] Client API (logique métier préservée)
- [x] Composants de base (TruthBadge, AlertBanner, MetricCard)
- [x] Design tokens SACS intégrés

### ⏳ ÉTAPE 2 : Injection du thème
- [ ] Invocation `@[theme-factory]`
- [ ] Invocation `@[bitjaru/styleseed]`
- [ ] Finalisation design system mobile-first
- [ ] Composants shadcn/ui personnalisés

### ⏳ ÉTAPE 3 : Pages & Routing
- [ ] Router React (react-router-dom)
- [ ] Page Home
- [ ] Page Dashboard (grille stations)
- [ ] Page About
- [ ] Page API (documentation)
- [ ] Page Podcast (lecteur audio)

---

## 📝 Notes techniques

**Contrainte VPS** : 512 Mo RAM
- Build optimisé avec code splitting
- Lazy loading des pages
- Tree shaking automatique (Vite)
- Assets minifiés (Terser)

**Architecture DB-First** :
- Connexion directe MCP TimescaleDB
- Pas de cache côté client (données temps réel)
- Polling automatique toutes les 5 minutes

---

## 🔒 Sécurité

- ✅ Variables d'environnement (pas de secrets en dur)
- ✅ Validation TypeScript stricte
- ✅ CORS limité à oceansentinelle.fr
- ✅ Rate limiting API (100 req/min)
- ✅ Sanitization inputs (Pydantic backend)

---

**Version** : 4.0.0  
**Dernière mise à jour** : 23 avril 2026  
**Auteur** : Ocean Sentinel DevSecOps Team
