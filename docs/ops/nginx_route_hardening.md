# Nginx route hardening runbook

This runbook is a proposed production patch. It must be applied only after the static files in this branch are deployed and `scripts/audit_public_routes.sh` passes for canonical routes.

## Goal

- Stop unknown routes from falling back to the homepage.
- Preserve `/data/` JSON alias and current `/api` behavior.
- Keep legacy routes as explicit `410 Gone`.

## Minimal patch intent

```nginx
error_page 404 /404.html;

location = /404.html {
    internal;
}

location / {
    try_files $uri $uri/ =404;
}
```

Preserve existing blocks for:

- `location /data/`
- `location = /api`
- `location = /api/`
- `location /api/`
- `location = /about`
- `location = /about.html`
- `location = /api.html`
- `location = /data-status`
- `location ^~ /data-status/`

## Production commands

```bash
set -euo pipefail
CFG="/etc/nginx/sites-available/oceansentinelle"
BK="${CFG}.bak.$(date -u +%Y%m%dT%H%M%SZ)"

sudo cp -a "$CFG" "$BK"
sudo nginx -T 2>/dev/null | grep -nE 'server_name oceansentinelle\.fr|root /var/www/oceansentinelle|try_files|location /data/|location /api/|error_page|return 410'

# Edit only the fallback location:
#   location / { try_files $uri $uri/ =404; ... }
# Add:
#   error_page 404 /404.html;
#   location = /404.html { internal; }

sudo nginx -t
sudo systemctl reload nginx
```

## Verification

```bash
curl -sI https://oceansentinelle.fr/no-such-ocean-route | sed -n '1,8p'
curl -sI https://oceansentinelle.fr/ | sed -n '1,8p'
curl -sI https://oceansentinelle.fr/data/BARAG_PROXY.public_status.json | sed -n '1,12p'
curl -sI https://oceansentinelle.fr/api | sed -n '1,8p'
curl -sI https://oceansentinelle.fr/api/ | sed -n '1,8p'
```

Expected:

- unknown route: `404`
- `/`: `200`
- `/data/BARAG_PROXY.public_status.json`: `200` with `Cache-Control: no-store`
- `/api`: `301`
- `/api/`: `302`

## Rollback

```bash
sudo cp -a "$BK" "$CFG"
sudo nginx -t
sudo systemctl reload nginx
```
