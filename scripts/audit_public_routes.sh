#!/usr/bin/env sh
set -eu

BASE_URL="${BASE_URL:-http://localhost}"
PUBLIC_DIR="${PUBLIC_DIR:-public}"
CANONICAL_ROUTES="/ /projet/ /dashboard/ /dashboard/simulations/ /dashboard/simulations/library/ /dashboard/transparence/osint/ /dashboard/transparence/infrastructure/ /podcast/"
CANONICAL_HTML="
$PUBLIC_DIR/index.html
$PUBLIC_DIR/projet/index.html
$PUBLIC_DIR/dashboard/index.html
$PUBLIC_DIR/dashboard/simulations/index.html
$PUBLIC_DIR/dashboard/simulations/library/index.html
$PUBLIC_DIR/dashboard/transparence/osint/index.html
$PUBLIC_DIR/dashboard/transparence/infrastructure/index.html
$PUBLIC_DIR/podcast/index.html
"
FORBIDDEN='API REST|TimescaleDB|MCP|temps réel|real[- ]time|rafraîchissement|5 min'

echo "== Route status audit =="
for route in $CANONICAL_ROUTES; do
    status="$(curl -sI "$BASE_URL$route" | awk 'NR==1 {print $2}')"
    case "$status" in
        200|301|302) echo "OK $route $status" ;;
        *) echo "FAIL $route expected 200/301/302 got ${status:-none}"; exit 1 ;;
    esac
done

random_route="/__missing_ocean_sentinel_$(date +%s)__/"
missing_status="$(curl -sI "$BASE_URL$random_route" | awk 'NR==1 {print $2}')"
if [ "$missing_status" != "404" ]; then
    echo "FAIL $random_route expected 404 got ${missing_status:-none}"
    exit 1
fi
echo "OK $random_route 404"

echo "== Data/API contract audit =="
data_dir_status="$(curl -sI "$BASE_URL/data/" | awk 'NR==1 {print $2}')"
if [ "$data_dir_status" != "403" ]; then
    echo "FAIL /data/ expected 403 got ${data_dir_status:-none}"
    exit 1
fi
echo "OK /data/ 403"

data_json="${DATA_JSON:-/data/BARAG_PROXY.public_status.json}"
data_json_headers="$(curl -sI "$BASE_URL$data_json")"
data_json_status="$(printf '%s\n' "$data_json_headers" | awk 'NR==1 {print $2}')"
if [ "$data_json_status" != "200" ]; then
    echo "FAIL $data_json expected 200 got ${data_json_status:-none}"
    exit 1
fi
printf '%s\n' "$data_json_headers" | grep -Eiq '^cache-control:.*no-store' || {
    echo "FAIL $data_json missing Cache-Control: no-store"
    exit 1
}
echo "OK $data_json 200 no-store"

api_status="$(curl -sI "$BASE_URL/api" | awk 'NR==1 {print $2}')"
if [ "$api_status" != "301" ]; then
    echo "FAIL /api expected 301 got ${api_status:-none}"
    exit 1
fi
echo "OK /api 301"

api_slash_headers="$(curl -sI "$BASE_URL/api/")"
api_slash_status="$(printf '%s\n' "$api_slash_headers" | awk 'NR==1 {print $2}')"
if [ "$api_slash_status" != "302" ]; then
    echo "FAIL /api/ expected 302 got ${api_slash_status:-none}"
    exit 1
fi
printf '%s\n' "$api_slash_headers" | grep -Eiq '^location: .*/dashboard/' || {
    echo "FAIL /api/ missing redirect to /dashboard/"
    exit 1
}
echo "OK /api/ 302 /dashboard/"

echo "== Doctrine string audit =="
if grep -EIn "$FORBIDDEN" $CANONICAL_HTML "$PUBLIC_DIR/assets/os_nav.css" "$PUBLIC_DIR/assets/os_nav.js"; then
    echo "FAIL forbidden public string found"
    exit 1
fi
echo "OK no forbidden strings in canonical HTML or referenced nav assets"

echo "== Unique nav injection audit =="
for file in $CANONICAL_HTML; do
    css_count="$(grep -c '/assets/os_nav.css' "$file" || true)"
    js_count="$(grep -c '/assets/os_nav.js' "$file" || true)"
    mount_count="$(grep -c 'id="os-topnav"' "$file" || true)"
    inline_nav_count="$(grep -ci '<nav' "$file" || true)"
    if [ "$css_count" != "1" ] || [ "$js_count" != "1" ] || [ "$mount_count" != "1" ] || [ "$inline_nav_count" != "0" ]; then
        echo "FAIL $file css=$css_count js=$js_count mount=$mount_count inline_nav=$inline_nav_count"
        exit 1
    fi
    echo "OK $file nav-assets=1 mount=1 inline-nav=0"
done

echo "audit_public_routes.sh passed"
