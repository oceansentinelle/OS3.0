# Ocean Sentinelle Apply, Verify, Rollback Runbook

Target: `oceansentinelle.fr`
Webroot: `/var/www/oceansentinelle`
Vhost: `/etc/nginx/sites-available/oceansentinelle`

## Preflight

```sh
set -eu
date -u
sudo nginx -t
sudo test -d /var/www/oceansentinelle
sudo test -f /etc/nginx/sites-available/oceansentinelle
```

Do not print `.env`, tokens, private keys, or full unrelated configs.

## Backup

```sh
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
sudo cp /etc/nginx/sites-available/oceansentinelle "/etc/nginx/sites-available/oceansentinelle.bak-$STAMP"
sudo tar -C /var/www -czf "/var/backups/oceansentinelle-webroot-$STAMP.tar.gz" oceansentinelle
```

## Apply Webroot

Deploy the PR artifact so files land under `/var/www/oceansentinelle`.

Expected files:

```text
/var/www/oceansentinelle/404.html
/var/www/oceansentinelle/assets/os_nav.css
/var/www/oceansentinelle/assets/os_nav.js
/var/www/oceansentinelle/dashboard/simulations/index.html
```

Canonical HTML pages should include only one nav mount and no inline nav.

Idempotent nav patch option on the VPS:

```sh
cd /path/to/deployed/repo-or-scripts
WEBROOT=/var/www/oceansentinelle sh scripts/patch_webroot_nav.sh
```

## Apply Nginx Patch

Idempotent nginx patch option on the VPS:

```sh
cd /path/to/deployed/repo-or-scripts
SITE=/etc/nginx/sites-available/oceansentinelle WEBROOT=/var/www/oceansentinelle sh scripts/patch_nginx_no_phantom.sh
```

Minimal patch intent:

```diff
@@
     root /var/www/oceansentinelle;
     index index.html;
+
+    error_page 404 /404.html;
+    location = /404.html {
+        internal;
+    }
@@
     location = /podcast { return 301 /podcast/; }
+
+    location = /projet { return 301 /projet/; }
+    location = /simulations { return 301 /simulations/; }
+    location = /transparence { return 301 /transparence/; }
@@
 location / {
-        try_files $uri $uri/ /index.html;
+        try_files $uri $uri/ /404.html =404;
         add_header Cache-Control "no-cache, no-store, must-revalidate";
```

Preserve exactly:

```text
location /data/ { alias /opt/oceansentinel/current/site_data/; add_header Cache-Control "no-store" always; }
location = /api { return 301 /api/; }
location = /api/ { return 302 /dashboard/; }
location /api/ { proxy_pass http://localhost:8000/api/; }
```

Validate before reload:

```sh
sudo nginx -t
sudo systemctl reload nginx
```

## Verify

Run from a machine with `curl`, `grep`, and POSIX shell:

```sh
BASE_URL=https://oceansentinelle.fr PUBLIC_DIR=/var/www/oceansentinelle sh scripts/audit_public_routes.sh
```

Manual spot checks:

```sh
curl -sI https://oceansentinelle.fr/no-such-route | sed -n '1,8p'
curl -sI https://oceansentinelle.fr/data/ | sed -n '1,8p'
curl -sI https://oceansentinelle.fr/data/BARAG_PROXY.public_status.json | sed -n '1,12p'
curl -sI https://oceansentinelle.fr/api | sed -n '1,8p'
curl -sI https://oceansentinelle.fr/api/ | sed -n '1,8p'
```

Expected:

```text
/no-such-route -> 404
/data/ -> 403
/data/BARAG_PROXY.public_status.json -> 200 + Cache-Control: no-store
/api -> 301
/api/ -> 302 Location: /dashboard/
```

## Legacy Quarantine

Build proof first:

```sh
sudo grep -RhoE '/assets/[^" ]+' /var/www/oceansentinelle/*.html /var/www/oceansentinelle/dashboard /var/www/oceansentinelle/podcast /var/www/oceansentinelle/projet /var/www/oceansentinelle/simulations /var/www/oceansentinelle/transparence 2>/dev/null | sort -u > /tmp/os-assets-referenced.txt
sudo tail -n 5000 /var/log/nginx/access.log | awk '{print $7}' | grep '^/assets/' | sort -u > /tmp/os-assets-accessed.txt
sudo find /var/www/oceansentinelle/assets -maxdepth 1 -type f -printf '/assets/%f\n' | sort -u > /tmp/os-assets-present.txt
comm -23 /tmp/os-assets-present.txt /tmp/os-assets-referenced.txt > /tmp/os-assets-unreferenced.txt
```

Only quarantine files that are absent from canonical HTML references and absent from recent access logs:

```sh
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
sudo mkdir -p /var/www/oceansentinelle/assets/_quarantine
sudo tar -C /var/www/oceansentinelle -czf "/var/www/oceansentinelle/assets/_quarantine/legacy-assets-$STAMP.tar.gz" $(sed 's#^/##' /tmp/os-assets-unreferenced.txt)
```

Idempotent script option:

```sh
WEBROOT=/var/www/oceansentinelle sh scripts/quarantine_legacy_assets.sh
```

## Rollback

Nginx:

```sh
sudo cp /etc/nginx/sites-available/oceansentinelle.bak-<STAMP> /etc/nginx/sites-available/oceansentinelle
sudo nginx -t
sudo systemctl reload nginx
```

Webroot:

```sh
sudo tar -C /var/www -xzf /var/backups/oceansentinelle-webroot-<STAMP>.tar.gz
sudo nginx -t
sudo systemctl reload nginx
```
