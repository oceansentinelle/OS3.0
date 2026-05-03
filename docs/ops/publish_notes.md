# Notes de publication du site statique

## Source de vérité

La page publique canonique **Le Projet** est :

- `public/projet/index.html`
- URL publique attendue : `/projet/`

Les fichiers historiques suivants ne doivent pas être utilisés comme source de vérité :

- `public/about.html`
- `public/fr/about.html`

Ils servent uniquement de pages de retrait/redirection statique vers `/projet/` afin d'éviter un retour du contenu legacy après publication.

## Règles de contenu public

- Ne pas publier de promesse de fraîcheur instantanée.
- Utiliser le framing : données publiques ou historiques, shadow mode, non décisionnel.
- Afficher les rappels : `SCENARIO ≠ MEASURED`, shadow mode, non décisionnel, alertes interdites.
- Ne pas publier de secret, token, endpoint admin, chemin serveur sensible ou détail d'infrastructure exploitable.

## Déploiement

Lors d'un publish du site statique, copier le contenu de `public/` vers la racine statique servie par le site.

Contrôles avant publication :

```bash
grep -RInE "temps.r..el|temps-reel|real[- ]time" public/ && exit 1 || true
grep -RInE "about\\.html" public/index.html public/projet/index.html && exit 1 || true
test -f public/projet/index.html
test -f public/about.html
test -f public/fr/about.html
```

Ces contrôles empêchent la régression où une publication réécrit `about.html` avec l'ancienne page projet.
