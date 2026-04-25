# 🖼️ Configuration de l'Image Hero - Bassin d'Arcachon

## ✅ Étape 1 : Placer l'Image

**Action requise** : Vous devez manuellement placer l'image du Bassin d'Arcachon dans le dossier suivant :

```
C:\Users\ktprt\Documents\OSwindsurf\ocean-sentinel-v4\public\images\bassin-arcachon-hero.jpg
```

**Nom du fichier** : `bassin-arcachon-hero.jpg` (exactement)

---

## 🎨 Optimisations Appliquées

### 1. **Hero Section Responsive**
- Hauteur : 70vh (mobile) → 80vh (desktop)
- Image en `object-cover` pour adaptation automatique
- Centrage avec `object-center`

### 2. **Performance**
```tsx
loading="eager"          // Chargement immédiat (above the fold)
fetchPriority="high"     // Priorité maximale navigateur
```

### 3. **Lisibilité du Texte**
- Overlay gradient sombre : `from-ocean-950/80 via-ocean-900/70 to-ocean-950/90`
- Texte en blanc avec `drop-shadow-2xl`
- Contraste optimisé pour WCAG AA

### 4. **Responsive Design**
```css
min-h-[70vh]    /* Mobile */
md:min-h-[80vh] /* Desktop */
```

---

## 🚀 Déploiement

### Étape 1 : Vérifier l'image
```bash
ls public/images/bassin-arcachon-hero.jpg
```

### Étape 2 : Build
```bash
npm run build
```

### Étape 3 : Vérifier le build
```bash
ls dist/images/bassin-arcachon-hero.jpg
```

### Étape 4 : Déployer
```bash
scp -r dist/* root@76.13.43.3:/var/www/oceansentinelle/
```

---

## 📊 Optimisations Recommandées (Production)

### 1. Compression de l'Image
**Outils** :
- [TinyPNG](https://tinypng.com/) - Compression intelligente
- [Squoosh](https://squoosh.app/) - Compression avancée
- ImageMagick CLI

**Objectif** : Réduire à < 200KB sans perte de qualité visible

### 2. Format WebP
```bash
# Convertir en WebP (meilleure compression)
cwebp -q 85 bassin-arcachon-hero.jpg -o bassin-arcachon-hero.webp
```

### 3. Versions Responsive
Créer plusieurs tailles :
- **Mobile** : 750px width → `bassin-arcachon-hero-mobile.jpg`
- **Tablet** : 1200px width → `bassin-arcachon-hero-tablet.jpg`
- **Desktop** : 1920px width → `bassin-arcachon-hero-desktop.jpg`

### 4. Implémentation `<picture>` (Futur)
```tsx
<picture>
  <source
    media="(max-width: 768px)"
    srcSet="/images/bassin-arcachon-hero-mobile.webp"
    type="image/webp"
  />
  <source
    media="(max-width: 1200px)"
    srcSet="/images/bassin-arcachon-hero-tablet.webp"
    type="image/webp"
  />
  <source
    srcSet="/images/bassin-arcachon-hero-desktop.webp"
    type="image/webp"
  />
  <img
    src="/images/bassin-arcachon-hero.jpg"
    alt="Bassin d'Arcachon"
    className="w-full h-full object-cover"
  />
</picture>
```

---

## 🎯 Résultat Attendu

### Hero Section
```
┌─────────────────────────────────────────────────┐
│                                                 │
│  [Image du Bassin d'Arcachon en fond]          │
│  [Overlay gradient sombre]                      │
│                                                 │
│     Surveillance Océanographique                │
│            Temps Réel                           │
│                                                 │
│   Données environnementales du Bassin           │
│          d'Arcachon                             │
│   Système SACS • Alertes • API REST             │
│                                                 │
│   [Bouton : Accéder aux données en direct]      │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## ✅ Checklist

- [ ] Image placée dans `public/images/bassin-arcachon-hero.jpg`
- [ ] Image compressée (< 200KB recommandé)
- [ ] Build exécuté (`npm run build`)
- [ ] Image présente dans `dist/images/`
- [ ] Déployé sur le VPS
- [ ] Testé sur mobile et desktop
- [ ] Cache navigateur vidé (Ctrl + Shift + R)

---

## 🔍 Troubleshooting

### L'image ne s'affiche pas
1. Vérifier le chemin : `public/images/bassin-arcachon-hero.jpg`
2. Vérifier le nom exact (sensible à la casse)
3. Rebuild : `npm run build`
4. Vérifier dans DevTools → Network → Images

### L'image est trop lourde
1. Compresser avec TinyPNG
2. Réduire la résolution à 1920px max
3. Convertir en WebP

### Le texte n'est pas lisible
1. Ajuster l'opacité de l'overlay (ligne 23 de Home.tsx)
2. Augmenter le `drop-shadow` du texte
3. Modifier le gradient de l'overlay
