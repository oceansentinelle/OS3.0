#!/usr/bin/env sh
set -eu

SITE="${SITE:-/etc/nginx/sites-available/oceansentinelle}"
WEBROOT="${WEBROOT:-/var/www/oceansentinelle}"
STAMP="${STAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
BACKUP="$SITE.bak-$STAMP"

echo "== Backup nginx site =="
sudo cp -a "$SITE" "$BACKUP"
echo "$BACKUP"

echo "== Ensure themed 404 exists =="
sudo tee "$WEBROOT/404.html" >/dev/null <<'HTML'
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page introuvable - Ocean Sentinelle</title>
  <link rel="stylesheet" href="/assets/os_nav.css">
  <script defer src="/assets/os_nav.js"></script>
  <style>body{margin:0;background:#071B2E;color:#EAF4FF;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}main{max-width:960px;margin:0 auto;padding:36px 20px}.panel{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:10px;padding:24px}a{color:#7ED7FF}.muted{color:#C7D8E8}</style>
</head>
<body data-route="/404.html">
  <div id="os-topnav"></div>
  <main>
    <section class="panel">
      <p class="muted">404 controlee</p>
      <h1>Page introuvable</h1>
      <p>Cette route n'est pas publiee dans le canon public Ocean Sentinelle.</p>
      <p><a href="/">Retour accueil</a></p>
    </section>
  </main>
</body>
</html>
HTML

echo "== Patch nginx safely =="
tmp_py="$(mktemp)"
cat > "$tmp_py" <<'PY'
from pathlib import Path
import re
import sys

site = Path(sys.argv[1])
s = site.read_text(encoding="utf-8", errors="replace")

if "error_page 404 /404.html;" not in s:
    s = s.replace("    index index.html;\n", "    index index.html;\n\n    error_page 404 /404.html;\n    location = /404.html {\n        internal;\n    }\n", 1)

for line in [
    "    location = /simulations { return 301 /dashboard/simulations/; }",
    "    location = /simulations/ { return 301 /dashboard/simulations/; }",
    "    location = /transparence { return 301 /dashboard/transparence/infrastructure/; }",
    "    location = /transparence/ { return 301 /dashboard/transparence/infrastructure/; }",
]:
    if line.strip() not in s:
        marker = "    location = /podcast { return 301 /podcast/; }\n"
        if marker in s:
            s = s.replace(marker, marker + line + "\n", 1)

pattern = re.compile(r'\nlocation\s+/\s*\{\s*try_files\s+\$uri\s+\$uri/\s+[^;]+;\s*((?:\s*add_header[^\n]+\n|\s*)*)\}', re.S)
replacement = "\nlocation / {\n        try_files $uri $uri/ =404;\n        add_header Cache-Control \"no-cache, no-store, must-revalidate\";\n        add_header Pragma \"no-cache\";\n        add_header Expires \"0\";\n    }"
if pattern.search(s):
    s = pattern.sub(replacement, s, count=1)
else:
    raise SystemExit("Could not find location / block; refusing to patch")

if "/index.html" in re.search(r'location\s+/\s*\{.*?\}', s, re.S).group(0):
    raise SystemExit("location / still contains /index.html; refusing to write")

site.write_text(s, encoding="utf-8")
PY

if ! sudo python3 "$tmp_py" "$SITE"; then
  rm -f "$tmp_py"
  sudo cp -a "$BACKUP" "$SITE"
  echo "Patch failed; restored $BACKUP"
  exit 1
fi
rm -f "$tmp_py"

echo "== Validate nginx =="
if ! sudo nginx -t; then
  sudo cp -a "$BACKUP" "$SITE"
  sudo nginx -t || true
  echo "nginx -t failed; restored $BACKUP"
  exit 1
fi

sudo systemctl reload nginx

echo "== Verify HTTP contracts =="
BASE_URL="${BASE_URL:-https://oceansentinelle.fr}"
missing="$(curl -skI "$BASE_URL/no-such-route" | awk 'NR==1 {print $2}')"
data_dir="$(curl -skI "$BASE_URL/data/" | awk 'NR==1 {print $2}')"
api="$(curl -skI "$BASE_URL/api" | awk 'NR==1 {print $2}')"
api_slash="$(curl -skI "$BASE_URL/api/" | awk 'NR==1 {print $2}')"

if [ "$missing" != "404" ] || [ "$data_dir" != "403" ] || [ "$api" != "301" ] || [ "$api_slash" != "302" ]; then
  sudo cp -a "$BACKUP" "$SITE"
  sudo nginx -t && sudo systemctl reload nginx
  echo "HTTP verification failed; rolled back $BACKUP"
  echo "missing=$missing data_dir=$data_dir api=$api api_slash=$api_slash"
  exit 1
fi

echo "patch_nginx_no_phantom.sh passed"

