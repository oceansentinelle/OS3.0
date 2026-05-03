# Ocean Sentinelle - Route Map

Date audit: 2026-05-03  
Mode: lecture seule VPS, patch prepare dans Git uniquement.

## Preuves nginx

Source active: `/etc/nginx/sites-enabled/oceansentinelle`

| Preuve | Valeur |
|---|---|
| Vhost | `server_name oceansentinelle.fr www.oceansentinelle.fr` |
| Webroot | `root /var/www/oceansentinelle` |
| Dashboard redirect | `location = /dashboard { return 301 /dashboard/; }` |
| Data public | `location /data/ { alias /opt/oceansentinel/current/site_data/; Cache-Control: no-store; }` |
| API root | `/api` -> `301 /api/`; `/api/` -> `302 /dashboard/` |
| API proxied | `location /api/ { proxy_pass http://localhost:8000/api/; }` |
| Legacy 410 | `/about`, `/about.html`, `/api.html`, `/data-status`, `/data-status/` |
| Fallback | `location / { try_files $uri $uri/ /index.html; }` |

## Routes testees

| URL | Resolution observee | Fichier reel attendu | Statut | Action recommandee |
|---|---|---|---|---|
| `/` | `200`, `content-length: 14269`, no-store | `/var/www/oceansentinelle/index.html` | canonique | Conserver home principale. |
| `/projet/` | `200`, `content-length: 2784`, no-store | `/var/www/oceansentinelle/projet/index.html` | canonique, a harmoniser | Backport Git de la version premium. |
| `/dashboard/` | `200`, `content-length: 17679`, no-store | `/var/www/oceansentinelle/dashboard/index.html` | canonique | Harmoniser navigation partagee. |
| `/dashboard/simulations/library/` | fichier present | `/var/www/oceansentinelle/dashboard/simulations/library/index.html` | canonique | Backport + nav partagee. |
| `/dashboard/transparence/osint/` | fichier present | `/var/www/oceansentinelle/dashboard/transparence/osint/index.html` | canonique | Backport + nav partagee. |
| `/dashboard/transparence/infrastructure/` | fichier present | `/var/www/oceansentinelle/dashboard/transparence/infrastructure/index.html` | canonique | Nav partagee. |
| `/podcast` | `200`, meme `content-length` et `etag` que `/` | aucun fichier `/podcast/index.html` | fallback_to_index | Creer une vraie page `/podcast/`. |
| `/data/BARAG_PROXY.public_status.json` | `200`, `application/json`, `Cache-Control: no-store` | `/opt/oceansentinel/current/site_data/BARAG_PROXY.public_status.json` | canonique data | Conserver. |
| `/api` | `301` vers `/api/` | regle nginx | technique controlee | Conserver. |
| `/api/` | `302` vers `/dashboard/` | regle nginx | neutralise public | Conserver. |
| `/api/health` | `405` sur HEAD, proxy API | API applicative | technique non page publique | Ne pas lier depuis la navigation publique. |
| `/about` | regle nginx `410` | aucun contenu public | legacy retire | Conserver 410. |
| `/about.html` | regle nginx `410` | tombstone repo uniquement | legacy retire | Ne pas referencer. |
| `/api.html` | regle nginx `410` | supprime prod | legacy retire | Conserver 410. |
| `/data-status/` | regle nginx `410` | supprime prod | legacy retire | Conserver 410. |

## Fichiers publics presents en prod

Fichiers HTML canoniques observes:

- `/var/www/oceansentinelle/index.html`
- `/var/www/oceansentinelle/projet/index.html`
- `/var/www/oceansentinelle/dashboard/index.html`
- `/var/www/oceansentinelle/dashboard/simulations/library/index.html`
- `/var/www/oceansentinelle/dashboard/transparence/osint/index.html`
- `/var/www/oceansentinelle/dashboard/transparence/infrastructure/index.html`

Fichier attendu absent:

- `/var/www/oceansentinelle/podcast/index.html`

## Assets legacy servables

Des chunks JavaScript legacy restent servables sous `/var/www/oceansentinelle/assets/`. Ils ne sont pas des pages canoniques, mais restent accessibles par URL directe et contiennent des formulations obsoletes. Voir `CONTENT_AUDIT.md`.

