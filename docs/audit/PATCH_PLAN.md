# Ocean Sentinelle - Patch Plan

Date: 2026-05-03  
Branche: `docs/home-nav-doctrine`

## Objectifs

1. Supprimer les fallbacks trompeurs des routes publiques attendues.
2. Uniformiser la navigation avec un composant unique.
3. Garder la homepage comme page principale.
4. Aligner les pages publiques sur la doctrine: donnees publiques ou historiques, shadow mode, non decisionnel, simulation != mesure.
5. Ne pas modifier la prod sans validation.

## Modifications preparees

| Fichier | Modification | Raison |
|---|---|---|
| `public/assets/nav.js` | Nouveau composant de navigation partage, horizontal et scrollable. | Eviter les divergences de nav entre pages. |
| `public/index.html` | Remplacement nav inline par `data-os-nav`; lien podcast vers `/podcast/`. | Home conservee, nav unique. |
| `public/projet/index.html` | Remplacement nav inline par composant partage. | Harmonisation UI. |
| `public/about.html` | Tombstone conservee, nav partagee, `noindex`. | Eviter legacy visible tout en gardant une sortie propre si servie hors nginx. |
| `public/podcast/index.html` | Nouvelle page canonique podcast. | Eviter le fallback silencieux vers `/index.html`. |
| `dashboard/index.html` | Nav partagee. | Dashboard coherent. |
| `dashboard/simulations/library/index.html` | Nav partagee. | Bibliotheque coherente. |
| `dashboard/transparence/osint/index.html` | Nav partagee; retrait de liens docs absents. | Eviter references mortes et contenu interne non publie. |
| `dashboard/transparence/infrastructure/index.html` | Nav partagee. | Transparence coherente. |
| `docs/audit/ROUTE_MAP.md` | Rapport route -> fichier/statut/action. | Preuve audit. |
| `docs/audit/CONTENT_AUDIT.md` | Occurrences interdites et actions. | Preuve audit. |
| `docs/audit/PATCH_PLAN.md` | Plan de patch. | Traçabilite. |

## Non applique en prod

Aucune commande d'ecriture prod n'est incluse dans ce patch.

## Follow-up prod apres validation

1. Deployer les fichiers statiques depuis Git.
2. Verifier `/podcast/` puis `/podcast`.
3. Confirmer que les HTML canoniques ne referencent pas les chunks legacy sous `/assets/`.
4. Avant toute suppression d'assets legacy, verifier les access logs:

```bash
sudo grep -E 'API-DI_F4z2V|About-DsVNpEbH|Dashboard-9M3DEVC5|Home-BMcYc-eu|index-CW28djC1|semantic-truth-overlay' /var/log/nginx/access.log* || true
```

5. Si aucun usage legitime n'est observe, archiver puis supprimer les chunks legacy servables.

## Checks de securite

- Aucun secret, token, cle privee ou chemin d'administration ajoute.
- Les pages publiques n'exposent pas d'endpoints admin.
- Les routes `/api` restent gerees par nginx, mais ne sont pas promues comme page publique.
- Toute simulation publique affiche les flags `SCENARIO`, `shadow_mode=true`, `alert_allowed=false`, `decision_ready=false` quand elle est dans le JSON de scenarios.

