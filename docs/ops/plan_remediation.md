# Ocean Sentinelle Remediation Plan

Date: 2026-05-04
Branch: `fix/site-coherence-nav-routing`

## Decision

Use `os_nav` as the single canonical navigation system.

`os_nav_v2` is currently the production path, but it is also the source of drift because it coexists
with inline navigation and an older `os_nav` pair. The remediation must converge the public HTML to:

```html
<link rel="stylesheet" href="/assets/os_nav.css">
<script defer src="/assets/os_nav.js"></script>
<div id="os-topnav"></div>
```

Then remove inline `<nav>`/template headers from canonical pages.

## PR1: Nav Unique

Goal: one global nav everywhere.

Actions:

```text
1. Install canonical /assets/os_nav.css and /assets/os_nav.js.
2. Replace /assets/os_nav_v2.css/js references with /assets/os_nav.css/js.
3. Fix bad mount strings such as id=\"os-topnav\".
4. Ensure exactly one <div id="os-topnav"></div> per canonical HTML.
5. Remove legacy inline nav/header blocks from canonical pages.
```

Eight tabs, exact order:

```text
Accueil /
Le Projet /projet/
Dashboard /dashboard/
Simulations IA /dashboard/simulations/
Bibliothèque /dashboard/simulations/library/
OSINT v1.2 /dashboard/transparence/osint/
Transparence /dashboard/transparence/infrastructure/
Podcast /podcast/
```

Script: `scripts/patch_webroot_nav.sh`

Rollback: restore `/var/backups/oceansentinelle-webroot-<STAMP>.tar.gz`.

## PR2: Routing Hardening

Goal: unknown routes return 404 instead of homepage 200.

Current production already shows:

```text
location / { try_files $uri $uri/ =404; }
/no-such-route -> 404
```

Keep the script idempotent so it can repair drift if `/index.html` fallback returns.

Script: `scripts/patch_nginx_no_phantom.sh`

Preserve:

```text
/data/ alias + no-store
/api -> 301 /api/
/api/ -> 302 /dashboard/
/api/* -> proxy http://localhost:8000/api/
static assets -> try_files $uri =404
```

## PR3: Theme Stabilization

Goal: no blank page on simulation routes.

Actions:

```text
1. Ensure canonical simulation pages have a dark background and readable text.
2. Display truth_status="SCENARIO", shadow_mode=true, alert_allowed=false, decision_ready=false.
3. Do not suggest or render operational alerts on scenario pages.
```

Current `/dashboard/simulations/` has a minimal dark style patch; the repo version should replace it
with the shared theme when deployed.

## PR4: Legacy Cleanup

Goal: no public claims from legacy assets.

Categories:

```text
1. Referenced by canonical HTML: must be corrected or deployment must fail.
2. Not referenced but URL-served: quarantine or return 410 for precise paths.
3. Dead after manifest + access log proof: delete in a later cleanup only.
```

Current forbidden files observed in prod:

```text
/assets/API-DI_F4z2V.js
/assets/About-DsVNpEbH.js
/assets/Dashboard-9M3DEVC5.js
/assets/Home-BMcYc-eu.js
/assets/Legal-CjFNsjmk.js
/assets/index-CW28djC1*.js
/assets/semantic-truth-overlay.js
/podcast/index.html
/podcast/index.html.bak.*
```

Script: `scripts/quarantine_legacy_assets.sh`

## PR5: Verification/CI

Goal: prevent regression.

Script: `scripts/audit_public_routes.sh`

Acceptance:

```text
/no-such-route -> 404
all canonical routes -> expected status
/data/ -> 403
/data/*.json -> 200 + no-store
/api -> 301
/api/ -> 302 /dashboard/
one #os-topnav per canonical HTML
zero inline nav in canonical HTML
zero forbidden terms in canonical HTML and referenced nav assets
```

