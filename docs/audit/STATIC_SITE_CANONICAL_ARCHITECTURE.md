# Ocean Sentinelle static site canonical architecture

## Executive summary

The production audit found one root cause behind the confusing public surface: the Nginx fallback `try_files ... /index.html` returns the homepage for unknown routes. This masks missing pages as valid HTTP 200 responses.

Navigation also had two competing systems: a shared injected navigation and inline page-level navigation. The canonical implementation is now `os_nav.css` + `os_nav.js` mounted on `<div id="os-topnav"></div>`.

The public doctrine remains unchanged: shadow mode, non-decisionnel, SCENARIO != MEASURED, SIMULATED != MEASURED, MEASURED != FRESH, no operational alert.

## Architecture map

```text
client
  -> nginx vhost oceansentinelle.fr
    -> root /var/www/oceansentinelle for static HTML/CSS/JS
    -> /data/ alias to public JSON snapshots with Cache-Control: no-store
    -> /api and /api/ preserve current redirect/proxy behavior
    -> explicit static routes resolve to their own index.html
    -> unknown routes should resolve to 404.html, not /index.html
```

## Inventory table

| Route | File served | Mechanism | Status | Action |
| --- | --- | --- | --- | --- |
| `/` | `/var/www/oceansentinelle/index.html` | static root | canonical | keep |
| `/projet/` | `/var/www/oceansentinelle/projet/index.html` | directory index | canonical | keep |
| `/dashboard/` | `/var/www/oceansentinelle/dashboard/index.html` | directory index | canonical | keep |
| `/dashboard/simulations/` | `/var/www/oceansentinelle/dashboard/simulations/index.html` | directory index | canonical | keep and style |
| `/dashboard/simulations/library/` | `/var/www/oceansentinelle/dashboard/simulations/library/index.html` | directory index | canonical | keep |
| `/dashboard/transparence/osint/` | `/var/www/oceansentinelle/dashboard/transparence/osint/index.html` | directory index | canonical | keep |
| `/dashboard/transparence/infrastructure/` | `/var/www/oceansentinelle/dashboard/transparence/infrastructure/index.html` | directory index | canonical | keep |
| `/podcast/` | `/var/www/oceansentinelle/podcast/index.html` | directory index | canonical | keep |
| `/simulations/` | `/var/www/oceansentinelle/simulations/index.html` | directory index | explicit bridge | keep or 301 later |
| `/transparence/` | `/var/www/oceansentinelle/transparence/index.html` | directory index | explicit bridge | keep or 301 later |
| `/about` | none | nginx return 410 | legacy | keep 410 |
| `/about.html` | none | nginx return 410 | legacy | keep 410 |
| `/api.html` | none | nginx return 410 | legacy | keep 410 |
| `/data-status/` | none | nginx return 410 | legacy | keep 410 |
| `/data/BARAG_PROXY.public_status.json` | public JSON snapshot | nginx alias | canonical data | preserve no-store |
| `/api` | redirect to `/api/` | nginx return 301 | API entry | preserve |
| `/api/` | redirect to `/dashboard/` | nginx return 302 | public-safe API root | preserve |
| `/api/*` | backend proxy | nginx proxy | application API | preserve |
| unknown route | `404.html` | `try_files $uri $uri/ =404` + `error_page` | controlled error | implement after validation |

## Findings

- Unknown routes currently return the homepage with HTTP 200 in production; ETag comparison confirmed `/` and an unknown route can share the same entity.
- The simulations route exists in production but was visually broken because the page used light text without a dark body background.
- Dashboard and subpages mixed inline nav and injected nav; that is the source of double bars.
- Legacy JavaScript chunks in deployed assets still contain obsolete public claims. They must not be referenced by canonical HTML and should be purged only after access-log review.

## Canonical UI decision

Use one navigation component everywhere:

- stylesheet: `/assets/os_nav.css`
- script: `/assets/os_nav.js`
- mount point: `<div id="os-topnav"></div>`
- labels, in order: Accueil, Le Projet, Dashboard, Simulations IA, Bibliothèque, OSINT v1.2, Infrastructure Overview, Podcast

## Rollback

- Static files: redeploy the previous Git commit.
- Nginx hardening: restore the timestamped vhost backup, run `sudo nginx -t`, then `sudo systemctl reload nginx`.
- Legacy asset purge: restore the archived tarball into the webroot, then rerun the route audit.
