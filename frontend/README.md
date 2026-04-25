# Ocean Sentinelle V3.1 - Frontend

Plateforme de surveillance océanographique du Bassin d'Arcachon avec Agentic UX.

**Domaine** : [oceansentinelle.fr](https://oceansentinelle.fr)  
**API** : [api.oceansentinelle.fr](https://api.oceansentinelle.fr)

## 🚀 Installation

```bash
cd frontend
npm install
```

## 🛠️ Développement

```bash
npm run dev
```

Serveur de développement : http://localhost:3000

## 🏗️ Build Production

```bash
npm run build
npm run preview
```

## 📦 Stack Technique

- **Framework** : React 18.3 + TypeScript 5.4
- **Build** : Vite 5.2
- **Styles** : TailwindCSS 3.4 + tailwindcss-animate
- **Icons** : Lucide React
- **Linting** : ESLint + TypeScript strict mode

## 🎯 Architecture

```
frontend/
├── src/
│   ├── main.tsx          # Point d'entrée React
│   └── App.tsx           # Composant racine
├── components/
│   └── os/
│       └── intent-preview.tsx  # Agentic UX component
├── app/
│   └── globals.css       # Styles Tailwind + Design System
├── lib/
│   └── utils.ts          # Utilitaires
└── assets/
    ├── css/
    └── js/
```

## 🔧 Configuration

- `vite.config.ts` : Configuration Vite + alias paths
- `tailwind.config.ts` : Design System Ocean Sentinel
- `tsconfig.json` : TypeScript strict mode
- `postcss.config.js` : TailwindCSS + Autoprefixer

## 🧪 Test Intent Preview

Le composant `intent-preview.tsx` implémente le pattern **Human-in-the-Loop** pour l'Agentic UX :
- Affiche les intentions de l'IA avant exécution
- Permet validation/rejet par l'utilisateur
- Conforme directive M-23-22 (transparence IA)
