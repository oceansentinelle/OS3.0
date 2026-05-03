# Ocean Sentinelle - Content Audit

Date audit: 2026-05-03  
Doctrine: aucune promesse "temps reel"; simulations en `SCENARIO`, `shadow_mode=true`, `alert_allowed=false`, `decision_ready=false`; aucune publication de secrets.

## Commandes de preuve

```bash
grep -RInoE 'temps réel|real[- ]time|API REST|TimescaleDB|MCP|rafraîchissement|5 min' /var/www/oceansentinelle 2>/dev/null
```

## Occurrences prod dans le webroot

| Mot | Fichier | Ligne | Statut | Action recommandee |
|---|---|---:|---|---|
| `temps réel` | `/var/www/oceansentinelle/assets/Legal-CjFNsjmk.js` | 13 | asset legacy servable | Retirer du prochain deploy ou remplacer par contenu doctrine. |
| `temps réel` | `/var/www/oceansentinelle/assets/Dashboard-9M3DEVC5.js` | 13 | asset legacy servable | Retirer du prochain deploy ou remplacer par dashboard statique actuel. |
| `5 min` | `/var/www/oceansentinelle/assets/Dashboard-9M3DEVC5.js` | 13 | asset legacy servable | Retirer du prochain deploy. |
| `API REST` | `/var/www/oceansentinelle/assets/index-CW28djC1.patch-20260502T210550Z.js` | 22 | backup/patch servable | Supprimer apres validation access logs. |
| `temps réel` | `/var/www/oceansentinelle/assets/index-CW28djC1.patch-20260502T210550Z.js` | 22 | backup/patch servable | Supprimer apres validation access logs. |
| `API REST` | `/var/www/oceansentinelle/assets/index-CW28djC1.patch-20260502T210550Z.patch-20260502T212458Z.js` | 22 | backup/patch servable | Supprimer apres validation access logs. |
| `temps réel` | `/var/www/oceansentinelle/assets/index-CW28djC1.patch-20260502T210550Z.patch-20260502T212458Z.js` | 22 | backup/patch servable | Supprimer apres validation access logs. |
| `API REST` | `/var/www/oceansentinelle/assets/index-CW28djC1.js` | 21 | asset app legacy servable | Retirer si non reference par HTML canonique. |
| `temps réel` | `/var/www/oceansentinelle/assets/index-CW28djC1.js` | 21 | asset app legacy servable | Retirer si non reference par HTML canonique. |
| `API REST` | `/var/www/oceansentinelle/assets/Home-BMcYc-eu.js` | 13 | asset legacy servable | Retirer du prochain deploy. |
| `temps réel` | `/var/www/oceansentinelle/assets/Home-BMcYc-eu.js` | 13 | asset legacy servable | Retirer du prochain deploy. |
| `temps réel` | `/var/www/oceansentinelle/assets/semantic-truth-overlay.js` | 56 | asset legacy servable | Inspecter usage avant suppression. |
| `TimescaleDB` | `/var/www/oceansentinelle/assets/About-DsVNpEbH.js` | 13 | asset legacy servable | Retirer du prochain deploy. |
| `temps réel` | `/var/www/oceansentinelle/assets/About-DsVNpEbH.js` | 13 | asset legacy servable | Retirer du prochain deploy. |
| `5 min` | `/var/www/oceansentinelle/assets/About-DsVNpEbH.js` | 13 | asset legacy servable | Retirer du prochain deploy. |
| `API REST` | `/var/www/oceansentinelle/assets/API-DI_F4z2V.js` | 13 | asset legacy servable | Priorite suppression apres access-log check. |
| `temps réel` | `/var/www/oceansentinelle/assets/API-DI_F4z2V.js` | 13 | asset legacy servable | Priorite suppression apres access-log check. |
| `TimescaleDB` | `/var/www/oceansentinelle/assets/API-DI_F4z2V.js` | 13 | asset legacy servable | Priorite suppression apres access-log check. |
| `MCP` | `/var/www/oceansentinelle/assets/API-DI_F4z2V.js` | 13 | asset legacy servable | Priorite suppression apres access-log check. |
| `rafraîchissement` | `/var/www/oceansentinelle/assets/API-DI_F4z2V.js` | 13 | asset legacy servable | Priorite suppression apres access-log check. |
| `5 min` | `/var/www/oceansentinelle/assets/API-DI_F4z2V.js` | 13 | asset legacy servable | Priorite suppression apres access-log check. |

## Etat repo public apres patch

Scope verifie: `public/`, `dashboard/`, `data/`.

Resultat attendu:

```text
0 occurrence de:
temps réel|real[- ]time|API REST|TimescaleDB|MCP|about\.html|/about\b|href="/api
```

Les documents internes du repo contiennent encore des termes techniques historiques. Ils ne sont pas des pages publiques canoniques et ne doivent pas etre copies tels quels dans le webroot.

