# Ocean Sentinelle Web Hardening Report

Date: 2026-05-04
Branch: `fix/nav-canonicalize-and-route-hardening`

## Findings

The workspace webroot is `public/`, not a full mirror of `/var/www/oceansentinelle`. The local
forensic scan found three pre-existing HTML files: `index.html`, `about.html`, and `api.html`.
There was no pre-existing `public/assets/` directory, no `dashboard/` subtree, and no local nginx
site file matching the broad production fallback. The production-only symptoms must therefore be
validated after deploy against the real webroot.

### Canonical HTML Inventory

| Route | File | CSS | JS |
| --- | --- | --- | --- |
| `/` | `public/index.html` | `/styles.css`, `/assets/os_nav.css` | `/assets/os_nav.js` |
| `/projet/` | `public/projet/index.html` | `/styles.css`, `/assets/os_nav.css` | `/assets/os_nav.js` |
| `/dashboard/` | `public/dashboard/index.html` | `/styles.css`, `/assets/os_nav.css` | `/assets/os_nav.js` |
| `/dashboard/simulations/` | `public/dashboard/simulations/index.html` | `/styles.css`, `/assets/os_nav.css` | `/assets/os_nav.js` |
| `/dashboard/simulations/library/` | `public/dashboard/simulations/library/index.html` | `/styles.css`, `/assets/os_nav.css` | `/assets/os_nav.js` |
| `/dashboard/transparence/osint/` | `public/dashboard/transparence/osint/index.html` | `/styles.css`, `/assets/os_nav.css` | `/assets/os_nav.js` |
| `/dashboard/transparence/infrastructure/` | `public/dashboard/transparence/infrastructure/index.html` | `/styles.css`, `/assets/os_nav.css` | `/assets/os_nav.js` |
| `/podcast/` | `public/podcast/index.html` | `/styles.css`, `/assets/os_nav.css` | `/assets/os_nav.js` |

### Route Graph

```text
/                                           -> public/index.html                                      -> styles.css, assets/os_nav.css, assets/os_nav.js
/projet/                                    -> public/projet/index.html                               -> styles.css, assets/os_nav.css, assets/os_nav.js
/dashboard/                                 -> public/dashboard/index.html                            -> styles.css, assets/os_nav.css, assets/os_nav.js
/dashboard/simulations/                     -> public/dashboard/simulations/index.html                -> styles.css, assets/os_nav.css, assets/os_nav.js
/dashboard/simulations/library/             -> public/dashboard/simulations/library/index.html        -> styles.css, assets/os_nav.css, assets/os_nav.js
/dashboard/transparence/osint/              -> public/dashboard/transparence/osint/index.html         -> styles.css, assets/os_nav.css, assets/os_nav.js
/dashboard/transparence/infrastructure/     -> public/dashboard/transparence/infrastructure/index.html -> styles.css, assets/os_nav.css, assets/os_nav.js
/podcast/                                   -> public/podcast/index.html                              -> styles.css, assets/os_nav.css, assets/os_nav.js
```

### Legacy Assets

No legacy asset existed under `public/assets/` before this change. The only assets now present are:

```text
assets/os_nav.css
assets/os_nav.js
styles.css
```

Proof command: `sh scripts/audit_assets_references.sh`, which computes `orphans = present - referenced`.

### Cause Notes

The double-navigation class of bug comes from mixing inline `<nav>` blocks with injected navigation.
The local files had inline navigation; all canonical pages now contain no inline `<nav>` and load one
shared injection script.

The simulations blank-page symptom could not be reproduced from the local snapshot because that page
did not exist. The hardening fix creates the canonical simulations page on the shared stylesheet and
uses explicit high-contrast tokens for text, panels, notices, and badges.

## Changes

Suggested commit split:

1. `fix(web): canonicalize public routes and shared nav`
2. `fix(web): add route and asset audits`
3. `docs(web): add nginx hardening patch and rollout proof`

Files touched:

```text
public/index.html
public/about.html
public/api.html
public/styles.css
public/assets/os_nav.css
public/assets/os_nav.js
public/projet/index.html
public/dashboard/index.html
public/dashboard/simulations/index.html
public/dashboard/simulations/library/index.html
public/dashboard/transparence/osint/index.html
public/dashboard/transparence/infrastructure/index.html
public/podcast/index.html
public/404.html
scripts/audit_public_routes.sh
scripts/audit_assets_references.sh
docs/web-hardening/nginx-route-hardening.diff
docs/web-hardening/legacy-quarantine-2026-05-04.md
docs/web-hardening/report.md
```

## Patch nginx

Patch file: `docs/web-hardening/nginx-route-hardening.diff`

Validation commands:

```sh
sudo cp /etc/nginx/sites-available/oceansentinelle /etc/nginx/sites-available/oceansentinelle.bak-20260504
sudo patch /etc/nginx/sites-available/oceansentinelle < docs/web-hardening/nginx-route-hardening.diff
sudo nginx -t
sudo systemctl reload nginx
BASE_URL=https://oceansentinelle.fr sh scripts/audit_public_routes.sh
```

Rollback:

```sh
sudo cp /etc/nginx/sites-available/oceansentinelle.bak-20260504 /etc/nginx/sites-available/oceansentinelle
sudo nginx -t
sudo systemctl reload nginx
```

## Tests/Proofs

Executed in this Codex workspace with PowerShell equivalents because `sh`/`bash` is not installed
locally. The committed `.sh` scripts are intended for CI/Linux/VPS execution.

Actual local static proof:

```text
== Referenced assets ==
assets/os_nav.css
assets/os_nav.js
styles.css

== Present assets ==
assets/os_nav.css
assets/os_nav.js
styles.css

== Orphan assets ==

Proof command: orphans = present - referenced via comm -23
```

Actual local nav and forbidden-string proof:

```text
0 forbidden-string matches in public/
all public HTML: css=1 js=1 inline_nav=0
```

Actual local HTTP proof with a temporary static server:

```text
OK / 200
OK /projet/ 200
OK /dashboard/ 200
OK /dashboard/simulations/ 200
OK /dashboard/simulations/library/ 200
OK /dashboard/transparence/osint/ 200
OK /dashboard/transparence/infrastructure/ 200
OK /podcast/ 200
OK /__missing_ocean_sentinel_<timestamp>__/ 404
```

Expected deployed route proof after nginx patch:

```text
OK / 200
OK /projet/ 200
OK /dashboard/ 200
OK /dashboard/simulations/ 200
OK /dashboard/simulations/library/ 200
OK /dashboard/transparence/osint/ 200
OK /dashboard/transparence/infrastructure/ 200
OK /podcast/ 200
OK /__missing_ocean_sentinel_<timestamp>__/ 404
OK no forbidden strings in canonical HTML or referenced nav assets
OK <each canonical HTML> nav-assets=1 inline-nav=0
```

## Remaining risks

The production webroot may contain additional HTML and legacy assets absent from this workspace.
Before deployment, compare the production file list with this branch and run the two audit scripts
against a staging copy of `/var/www/oceansentinelle`.

Recent nginx access logs were not available in the repo. Any production quarantine should inspect
access logs before moving extra assets.

The nginx patch is deliberately not applied here. It must be validated with `nginx -t` on the host
that owns the active site configuration.
