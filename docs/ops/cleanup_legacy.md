# Legacy Cleanup Runbook

## Scope

Phase 1 removes legacy public pages and stale backups from the static webroot while keeping a minimal rollback path.

Canonical public routes:

- `/`
- `/projet/`
- `/dashboard/`
- `/dashboard/transparence/infrastructure/`
- `/data/*.json`

Legacy routes:

- `/about`
- `/about.html`
- `/api.html`
- `/data-status`
- `/data-status/`

## Nginx Guardrails

The active vhost must keep these targeted legacy responses:

```nginx
location = /about { return 410; }
location = /about.html { return 410; }
location = /api.html { return 410; }
location = /data-status { return 410; }
location ^~ /data-status/ { return 410; }
```

The API and data routes must keep their current behavior:

```nginx
location = /api { return 301 /api/; }
location = /api/ { return 302 /dashboard/; }

location /data/ {
    alias /opt/oceansentinel/current/site_data/;
    add_header Cache-Control "no-store" always;
    default_type application/json;
}
```

## Backup

```bash
set -euo pipefail
TS=$(date -u +%Y%m%dT%H%M%SZ)
STASH="/root/oceansentinelle-cleanup-$TS"
mkdir -p "$STASH"

cp -a /var/www/oceansentinelle/api.html "$STASH/" 2>/dev/null || true
cp -a /var/www/oceansentinelle/data-status "$STASH/" 2>/dev/null || true

find /var/www/oceansentinelle -type f -name '*.bak*' -print0 \
  | tar --null -czf "$STASH/webroot-bak-files.tgz" --files-from -
```

## Delete

```bash
set -euo pipefail

rm -f /var/www/oceansentinelle/api.html
rm -rf /var/www/oceansentinelle/data-status
find /var/www/oceansentinelle -type f -name '*.bak*' -delete
```

## Nginx Test And Reload

```bash
nginx -t
systemctl reload nginx
```

## Smoke Tests

```bash
curl -I https://oceansentinelle.fr/about
curl -I https://oceansentinelle.fr/about.html
curl -I https://oceansentinelle.fr/api
curl -I https://oceansentinelle.fr/api/
curl -I https://oceansentinelle.fr/api.html
curl -I https://oceansentinelle.fr/data/
curl -I https://oceansentinelle.fr/data/BARAG_PROXY.public_status.json
curl -I https://oceansentinelle.fr/dashboard/
curl -I https://oceansentinelle.fr/dashboard/transparence/infrastructure/
```

Expected results:

- `/about` -> `410`
- `/about.html` -> `410`
- `/api` -> `301` to `/api/`
- `/api/` -> `302` to `/dashboard/`
- `/api.html` -> `410`
- `/data/` -> `403`
- existing `/data/*.json` -> `200`
- `/dashboard/` -> `200`
- `/dashboard/transparence/infrastructure/` -> `200`

## Content Checks

```bash
find /var/www/oceansentinelle -type f -name '*.html' -print0 \
  | xargs -0 grep -InE 'temps réel|real[- ]time|API REST|TimescaleDB|MCP' && exit 1 || true

find /var/www/oceansentinelle -type f -name '*.html' -print0 \
  | xargs -0 grep -InE 'about\.html|/about\b|href="/api"' && exit 1 || true
```

Success criteria:

- `0` forbidden wording occurrences in active HTML.
- `0` links to `/about`, `about.html`, or `href="/api"` in active HTML.
- Legacy routes return `410`.
- Data JSON remains available with `Cache-Control: no-store`.

## Rollback

```bash
set -euo pipefail
STASH="/root/oceansentinelle-cleanup-YYYYMMDDTHHMMSSZ"

cp -a "$STASH/api.html" /var/www/oceansentinelle/api.html 2>/dev/null || true
cp -a "$STASH/data-status" /var/www/oceansentinelle/data-status 2>/dev/null || true
tar -xzf "$STASH/webroot-bak-files.tgz" -C /

nginx -t
systemctl reload nginx
```
