# Images - Ocean Sentinel

## Hero Image

### bassin-arcachon-hero.jpg
**Source** : Image fournie par l'utilisateur  
**Sujet** : Bassin d'Arcachon - Banc de sable et eaux turquoise  
**Usage** : Image de fond de la page d'accueil (Hero section)

**Optimisations appliquées** :
- `loading="eager"` : Chargement prioritaire (above the fold)
- `fetchPriority="high"` : Priorité maximale pour le navigateur
- `object-cover` : Adaptation responsive sans déformation
- `object-center` : Centrage de l'image
- Overlay gradient : Amélioration de la lisibilité du texte

**Recommandations pour la production** :
1. Compresser l'image avec TinyPNG ou Squoosh (objectif : < 200KB)
2. Créer des versions responsive :
   - `bassin-arcachon-hero-mobile.jpg` (750px width)
   - `bassin-arcachon-hero-tablet.jpg` (1200px width)
   - `bassin-arcachon-hero-desktop.jpg` (1920px width)
3. Convertir en WebP pour meilleure compression
4. Ajouter un `<picture>` avec srcset pour responsive images

## Instructions de déploiement

1. Placer l'image dans `public/images/bassin-arcachon-hero.jpg`
2. Build : `npm run build`
3. L'image sera copiée dans `dist/images/`
4. Deploy : `scp -r dist/* root@76.13.43.3:/var/www/oceansentinelle/`
