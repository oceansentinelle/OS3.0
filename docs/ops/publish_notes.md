# Notes de publication du site statique

## Source de vérité

La page publique canonique **Le Projet** est :

- `public/projet/index.html`
- URL publique attendue : `/projet/`

`public/about.html` est une page de retrait/redirection statique. Elle ne doit pas être utilisée comme source de vérité lors d'un publish.

## Règles publiques

- Utiliser le framing : données publiques ou historiques, shadow mode, non décisionnel.
- Afficher les rappels : `SCENARIO ≠ MEASURED`, shadow mode, non décisionnel, alertes interdites.
- Ne pas publier de secret, token, endpoint admin, chemin serveur sensible ou détail d'infrastructure exploitable.

## Contrôles avant publication

```bash
grep -RInE "temps.r..el|real[- ]time" public/ && exit 1 || true
grep -RInE "href=\"[^\"]*about\\.html|href=\"/about" public/index.html public/projet/index.html && exit 1 || true
test -f public/projet/index.html
test -f public/about.html
```
