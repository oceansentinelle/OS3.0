#!/usr/bin/env sh
set -eu

PUBLIC_DIR="${PUBLIC_DIR:-public}"
TMP_DIR="${TMPDIR:-/tmp}/os_asset_audit_$$"
mkdir -p "$TMP_DIR"
trap 'rm -rf "$TMP_DIR"' EXIT

HTML_LIST="$TMP_DIR/html.txt"
REFERENCED="$TMP_DIR/referenced.txt"
PRESENT="$TMP_DIR/present.txt"

find "$PUBLIC_DIR" -type f -name '*.html' | sort > "$HTML_LIST"

sed -nE 's/.*(href|src)="([^"]+)".*/\2/p' $(cat "$HTML_LIST") \
    | sed -E 's/[?#].*$//' \
    | awk '
        /^\// { print substr($0, 2); next }
        /^https?:/ { next }
        { print }
      ' \
    | grep -E '^(assets/|styles\.css)' \
    | sort -u > "$REFERENCED"

find "$PUBLIC_DIR" -type f \( -name '*.css' -o -name '*.js' -o -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.webp' -o -name '*.svg' \) \
    | sed "s#^$PUBLIC_DIR/##" \
    | sort -u > "$PRESENT"

echo "== Referenced assets =="
cat "$REFERENCED"
echo
echo "== Present assets =="
cat "$PRESENT"
echo
echo "== Orphan assets =="
comm -23 "$PRESENT" "$REFERENCED" || true

echo
echo "Proof command: orphans = present - referenced via comm -23"
