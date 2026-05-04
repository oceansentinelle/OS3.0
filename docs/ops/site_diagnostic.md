# Ocean Sentinelle Site Diagnostic

Date: 2026-05-04
Target: `oceansentinelle.fr`
Mode: read-only production diagnostic, no destructive action

## Current 10-Line Diagnostic

1. Production now returns `404` for `/no-such-route`, so the phantom route bug is partly mitigated.
2. Nginx currently has `location / { try_files $uri $uri/ =404; }`.
3. `/data/` remains `403` and `/data/BARAG_PROXY.public_status.json` remains `200` with `no-store`.
4. `/api` remains `301`, `/api/` remains `302 /dashboard/`, and `/api/health` reaches the proxied app.
5. Canonical pages still use `os_nav_v2.css/js`, while backup pages and repo artifacts use `os_nav.css/js`.
6. Several canonical pages still contain inline `<nav>`/`<header>` blocks, producing double-source navigation.
7. No broken escaped mount was found in the latest prod scan, but the patch script still repairs `id=\"os-topnav\"`.
8. `/dashboard/simulations/` now has a minimal dark theme, but remains a placeholder and should use the shared theme.
9. `podcast/index.html` still contains a forbidden phrase; several legacy assets also contain forbidden claims.
10. Recommendation: converge all canonical pages to `os_nav` only, remove inline nav, quarantine legacy forbidden assets.

## Diagnostic

### Nginx Effective Config

Command:

```sh
sudo nginx -T 2>/dev/null | sed -n '1,260p'
sudo nginx -T 2>/dev/null | sed -n '260,330p'
```

Relevant excerpt:

```text
server_name oceansentinelle.fr www.oceansentinelle.fr;
root /var/www/oceansentinelle;
index index.html;

location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    try_files $uri =404;
}

location = /dashboard { return 301 /dashboard/; }

location /data/ {
    alias /opt/oceansentinel/current/site_data/;
    add_header Cache-Control "no-store" always;
    default_type application/json;
}

location = /api { return 301 /api/; }
location = /api/ { return 302 /dashboard/; }

location /api/ {
    proxy_pass http://localhost:8000/api/;
}

location = /about { return 410; }
location = /about.html { return 410; }
location = /api.html { return 410; }
location = /data-status { return 410; }
location ^~ /data-status/ { return 410; }
location = /podcast { return 301 /podcast/; }

location / {
    try_files $uri $uri/ /index.html;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

Finding: `location /` falls back to `/index.html`, so unknown routes are served as the homepage
with HTTP 200.

### File Inventory

Command:

```sh
sudo find /var/www/oceansentinelle -maxdepth 6 -type f -name '*.html' -print | sort
```

Current canonical HTML:

```text
/var/www/oceansentinelle/dashboard/index.html
/var/www/oceansentinelle/dashboard/simulations/index.html
/var/www/oceansentinelle/dashboard/simulations/library/index.html
/var/www/oceansentinelle/dashboard/transparence/infrastructure/index.html
/var/www/oceansentinelle/dashboard/transparence/osint/index.html
/var/www/oceansentinelle/index.html
/var/www/oceansentinelle/podcast/index.html
/var/www/oceansentinelle/projet/index.html
/var/www/oceansentinelle/simulations/index.html
/var/www/oceansentinelle/transparence/index.html
```

Assets inventory command:

```sh
sudo find /var/www/oceansentinelle/assets -maxdepth 2 -type f -print | head -n 200
```

Relevant assets observed:

```text
/var/www/oceansentinelle/assets/os_nav_v2.css
/var/www/oceansentinelle/assets/os_nav_v2.js
/var/www/oceansentinelle/assets/os_nav.css
/var/www/oceansentinelle/assets/os_nav.js
/var/www/oceansentinelle/assets/index-maddHTH3.css
/var/www/oceansentinelle/assets/API-DI_F4z2V.js
/var/www/oceansentinelle/assets/Dashboard-9M3DEVC5.js
/var/www/oceansentinelle/assets/Legal-CjFNsjmk.js
```

Note: `rg` is not installed on the VPS, so the requested `rg` probes were run with `grep -RInE`.

### Ghost Route Proof

Commands:

```sh
curl -sI https://oceansentinelle.fr/no-such-route | sed -n '1,8p'
curl -sI https://oceansentinelle.fr/ | sed -n '1,8p'
```

Output:

```text
/no-such-route:
HTTP/2 200
content-length: 13991
etag: "69f7d340-36a7"

/:
HTTP/2 200
content-length: 13991
etag: "69f7d340-36a7"
```

Historical conclusion from the earlier incident: `/no-such-route` was a phantom 200 serving the
homepage. Current prod retest on 2026-05-04 shows the route now returns `404`; keep
`scripts/patch_nginx_no_phantom.sh` to enforce and repair this invariant if drift returns.

Current retest:

```text
/no-such-route:
HTTP/2 404
content-length: 162
```

### Navigation Inventory

Command:

```sh
sudo grep -RInE 'os_nav\.css|os_nav\.js|os-topnav|<nav\b|Dashboard|Simulations IA|OSINT v1\.2|Bibliothèque|Infrastructure Overview|Podcast' /var/www/oceansentinelle
```

Summary:

| Route | File served | Nav status | HTTP | Problem | Action |
| --- | --- | --- | --- | --- | --- |
| `/` | `/var/www/oceansentinelle/index.html` | `os_nav_v2` + inline | 200 | double source, inline nav remains | remove inline nav, use `os_nav` only |
| `/projet/` | `/var/www/oceansentinelle/projet/index.html` | `os_nav_v2` only | 200 | current v2 should be replaced/aligned | use canonical `os_nav.css/js` |
| `/dashboard/` | `/var/www/oceansentinelle/dashboard/index.html` | `os_nav_v2` + inline | 200 | double source, inline nav remains | remove inline nav |
| `/dashboard/simulations/` | `/var/www/oceansentinelle/dashboard/simulations/index.html` | `os_nav_v2` only | 200 | layout has no page background | restore page layout |
| `/dashboard/simulations/library/` | `/var/www/oceansentinelle/dashboard/simulations/library/index.html` | `os_nav_v2` + inline | 200 | double source | remove inline nav |
| `/dashboard/transparence/osint/` | `/var/www/oceansentinelle/dashboard/transparence/osint/index.html` | `os_nav_v2` + inline | 200 | double source | remove inline nav |
| `/dashboard/transparence/infrastructure/` | `/var/www/oceansentinelle/dashboard/transparence/infrastructure/index.html` | `os_nav_v2` + inline | 200 | double source | remove inline nav |
| `/podcast/` | `/var/www/oceansentinelle/podcast/index.html` | `os_nav_v2` only | 200 | forbidden term in HTML | rewrite sentence |
| `/simulations/` | redirects to `/dashboard/simulations/` | n/a | 301 | bridge route now explicit | keep redirect |
| `/transparence/` | redirects to `/dashboard/transparence/infrastructure/` | n/a | 301 | bridge route now explicit | keep redirect |

Root cause: `os_nav_v2.js` injects a nav, then hides legacy navs at runtime. This prevents some
visual duplication, but HTML still contains two competing navigation systems.

### `/dashboard/simulations/` White Page Diagnostic

Command:

```sh
sudo head -n 220 /var/www/oceansentinelle/dashboard/simulations/index.html
```

Observed file:

```html
<link rel="stylesheet" href="/assets/os_nav_v2.css" />
<script defer src="/assets/os_nav_v2.js"></script>
...
<body>
  <div id="os-topnav"></div>
  <main style="...;color:#eaf4ff">
```

Cause: the page is a real file, but it is a 905-byte placeholder. It has light text and no page
background stylesheet. If the body defaults to white or a reset wins, content becomes low-contrast.

Corrective action: load the shared site stylesheet and use the canonical nav assets. Add explicit
simulation doctrine:

```text
truth_status="SCENARIO"
shadow_mode=true
alert_allowed=false
decision_ready=false
```

### Forbidden Terms

Command:

```sh
sudo grep -RInE 'API REST|TimescaleDB|MCP|temps réel|real[- ]time|rafraîchissement|5 min' /var/www/oceansentinelle
```

Classification:

| Class | File | Evidence |
| --- | --- | --- |
| canonical page | `/var/www/oceansentinelle/podcast/index.html` | line 31 contains `temps réel` |
| referenced/current nav assets | `os_nav_v2.css/js` | no forbidden term observed |
| legacy assets, publicly servable | `API-DI_F4z2V.js` | contains `API REST`, `TimescaleDB`, `MCP`, `temps réel`, `rafraîchissement 5 min` |
| legacy assets, publicly servable | `Legal-CjFNsjmk.js`, `Dashboard-9M3DEVC5.js`, `Home-BMcYc-eu.js`, `About-DsVNpEbH.js`, `index-CW28djC1*.js`, `semantic-truth-overlay.js` | contain forbidden or equivalent claims |
| backups, publicly servable unless blocked | `*.bak.*` HTML files | contain stale nav and forbidden claims |

Important distinction: not all legacy assets are referenced by current canonical HTML, but nginx can
serve them directly under `/assets/`. They should be quarantined only after manifest and access-log
proof.

### Data/API Contracts

Observed:

```text
/data/BARAG_PROXY.public_status.json -> HTTP/2 200, content-type application/json, cache-control no-store
/api/ -> HTTP/2 302, location /dashboard/
/api/health -> proxied application response to HEAD
```

Must preserve:

```text
/data/*.json -> 200 + no-store
/data/ -> 403
/api -> 301
/api/ -> 302 /dashboard/
/api/* -> proxy
```

## RCA

1. Routing root cause: `try_files $uri $uri/ /index.html` in `location /` turns unknown paths into
   homepage 200 responses.
2. Navigation root cause: pages have both injected navigation and inline navigation. The current
   JavaScript masks old navs instead of removing the second source of truth.
3. Simulation page root cause: the page is a minimal placeholder with no shared page background or
   robust layout CSS.
4. Doctrine root cause: legacy built assets and backup HTML remain publicly servable under webroot
   and still contain old public claims.

## Plan

### Option 1: Unified `os_nav` (recommended)

Use `/assets/os_nav.css` and `/assets/os_nav.js` as the only navigation source. Every canonical HTML
page contains:

```html
<link rel="stylesheet" href="/assets/os_nav.css">
<script defer src="/assets/os_nav.js"></script>
<div id="os-topnav"></div>
```

Then remove all inline `<nav>` blocks. `os_nav.js` must generate exactly:

```text
Accueil /
Le Projet /projet/
Dashboard /dashboard/
Simulations IA /dashboard/simulations/
Bibliothèque /dashboard/simulations/library/
OSINT v1.2 /dashboard/transparence/osint/
Infrastructure Overview /dashboard/transparence/infrastructure/
Podcast /podcast/
```

Why recommended: smallest surface area, less HTML duplication, easier future audits, single active
state logic.

### Option 2: Inline Nav Everywhere

Remove `os_nav` and copy the same inline nav into each canonical page.

Why not recommended: more duplicated HTML, higher risk of drift, harder rollback and future audits.

## Diffs Proposed

This branch prepares:

```text
docs/ops/site_diagnostic.md
docs/ops/runbook_apply_and_verify.md
scripts/audit_public_routes.sh
public/404.html
public/assets/os_nav.css
public/assets/os_nav.js
public/dashboard/simulations/index.html
```

Nginx patch is intentionally runbook-first and not applied in production during this diagnostic step.
