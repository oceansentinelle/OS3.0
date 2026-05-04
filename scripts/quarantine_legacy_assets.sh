#!/usr/bin/env sh
set -eu

WEBROOT="${WEBROOT:-/var/www/oceansentinelle}"
STAMP="${STAMP:-$(date -u +%Y%m%d)}"
QDIR="$WEBROOT/_quarantine/$STAMP"
REPORT="$QDIR/report.txt"
FORBIDDEN='API REST|TimescaleDB|MCP|temps réel|real[- ]time|rafraîchissement|5 min'

CANONICAL_GLOBS="$WEBROOT/*.html $WEBROOT/dashboard $WEBROOT/podcast $WEBROOT/projet $WEBROOT/simulations $WEBROOT/transparence"

sudo mkdir -p "$QDIR"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "== Build manifests =="
sudo grep -RhoE '/assets/[^" ]+' $CANONICAL_GLOBS 2>/dev/null | sed 's/[?#].*$//' | sort -u > "$tmp/referenced.txt" || true
sudo tail -n 5000 /var/log/nginx/access.log 2>/dev/null | awk '{print $7}' | grep '^/assets/' | sed 's/[?#].*$//' | sort -u > "$tmp/accessed.txt" || true
sudo find "$WEBROOT/assets" -maxdepth 1 -type f -printf '/assets/%f\n' | sort -u > "$tmp/present.txt"
sudo grep -RIlE "$FORBIDDEN" "$WEBROOT" | sed "s#^$WEBROOT##" | sort -u > "$tmp/forbidden.txt" || true

{
  echo "Quarantine report $STAMP"
  echo
  echo "Referenced assets:"
  cat "$tmp/referenced.txt"
  echo
  echo "Recently accessed assets:"
  cat "$tmp/accessed.txt"
  echo
  echo "Forbidden files:"
  cat "$tmp/forbidden.txt"
  echo
  echo "Actions:"
} | sudo tee "$REPORT" >/dev/null

failed=0
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  case "$rel" in
    /assets/*)
      if grep -qx "$rel" "$tmp/referenced.txt"; then
        echo "KEEP referenced forbidden asset: $rel" | sudo tee -a "$REPORT" >/dev/null
        failed=1
      elif grep -qx "$rel" "$tmp/accessed.txt"; then
        echo "KEEP recently accessed forbidden asset: $rel" | sudo tee -a "$REPORT" >/dev/null
        failed=1
      else
        dest="$QDIR${rel}"
        sudo mkdir -p "$(dirname "$dest")"
        sudo mv "$WEBROOT$rel" "$dest"
        echo "MOVED $rel -> $dest" | sudo tee -a "$REPORT" >/dev/null
      fi
      ;;
    *.bak*|*/index.html.bak*)
      dest="$QDIR$rel"
      sudo mkdir -p "$(dirname "$dest")"
      sudo mv "$WEBROOT$rel" "$dest"
      echo "MOVED backup $rel -> $dest" | sudo tee -a "$REPORT" >/dev/null
      ;;
    *)
      echo "REQUIRES MANUAL PATCH canonical forbidden file: $rel" | sudo tee -a "$REPORT" >/dev/null
      failed=1
      ;;
  esac
done < "$tmp/forbidden.txt"

echo "Report: $REPORT"
if [ "$failed" != 0 ]; then
  echo "Some forbidden files are referenced, recently accessed, or canonical. Patch them before delete."
  exit 2
fi

echo "quarantine_legacy_assets.sh passed"

