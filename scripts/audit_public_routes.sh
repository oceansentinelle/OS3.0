#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-https://oceansentinelle.fr}"
WEBROOT="${WEBROOT:-}"
UNKNOWN_ROUTE="${UNKNOWN_ROUTE:-/no-such-ocean-route}"

canonical_routes=(
  "/"
  "/projet/"
  "/dashboard/"
  "/dashboard/simulations/"
  "/dashboard/simulations/library/"
  "/dashboard/transparence/osint/"
  "/dashboard/transparence/infrastructure/"
  "/podcast/"
  "/data/BARAG_PROXY.public_status.json"
  "/api"
  "/api/"
)

for path in "${canonical_routes[@]}"; do
  printf '== %s\n' "$path"
  curl -sI "${BASE_URL}${path}" | sed -n '1,12p'
done

printf '== %s\n' "$UNKNOWN_ROUTE"
unknown_headers="$(curl -sI "${BASE_URL}${UNKNOWN_ROUTE}")"
printf '%s\n' "$unknown_headers" | sed -n '1,12p'
if printf '%s\n' "$unknown_headers" | grep -qE '^HTTP/[0-9.]+ 200'; then
  echo "FAIL: unknown route returned HTTP 200"
  exit 1
fi

root_etag="$(curl -sI "${BASE_URL}/" | awk 'tolower($1)=="etag:" {print $2}' | tr -d '\r')"
unknown_etag="$(printf '%s\n' "$unknown_headers" | awk 'tolower($1)=="etag:" {print $2}' | tr -d '\r')"
if [ -n "$root_etag" ] && [ "$root_etag" = "$unknown_etag" ]; then
  echo "FAIL: unknown route shares homepage ETag"
  exit 1
fi

if [ -n "$WEBROOT" ] && [ -d "$WEBROOT" ]; then
  echo "== local content checks"
  find "$WEBROOT" -type f \( -name '*.html' -o -name '*.js' -o -name '*.css' \) -print0 \
    | xargs -0 grep -InE 'API REST|TimescaleDB|MCP|temps réel|real[- ]time|rafraîchissement|5 min' \
    && { echo "FAIL: forbidden public terms found"; exit 1; } || true
fi

echo "OK: public route audit completed"
