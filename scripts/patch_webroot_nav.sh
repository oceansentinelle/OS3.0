#!/usr/bin/env sh
set -eu

WEBROOT="${WEBROOT:-/var/www/oceansentinelle}"
STAMP="${STAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups}"
BACKUP="$BACKUP_DIR/oceansentinelle-webroot-before-nav-$STAMP.tar.gz"

CANONICAL_HTML="
$WEBROOT/index.html
$WEBROOT/projet/index.html
$WEBROOT/dashboard/index.html
$WEBROOT/dashboard/simulations/index.html
$WEBROOT/dashboard/simulations/library/index.html
$WEBROOT/dashboard/transparence/osint/index.html
$WEBROOT/dashboard/transparence/infrastructure/index.html
$WEBROOT/podcast/index.html
$WEBROOT/simulations/index.html
$WEBROOT/transparence/index.html
"

echo "== Backup webroot =="
sudo mkdir -p "$BACKUP_DIR"
sudo tar -C "$(dirname "$WEBROOT")" -czf "$BACKUP" "$(basename "$WEBROOT")"
echo "$BACKUP"

echo "== Install canonical os_nav assets =="
sudo mkdir -p "$WEBROOT/assets"
sudo tee "$WEBROOT/assets/os_nav.css" >/dev/null <<'CSS'
#os-topnav{position:sticky;top:0;z-index:1000;border-bottom:1px solid rgba(141,200,216,.32);background:rgba(5,16,25,.94);backdrop-filter:blur(14px)}
.os-topnav__inner{width:min(1120px,calc(100% - 24px));min-height:68px;margin:0 auto;display:flex;align-items:center;gap:18px}
.os-topnav__brand{flex:0 0 auto;color:#f6fbff;text-decoration:none;font-weight:900;white-space:nowrap}
.os-topnav__links{display:flex;align-items:center;gap:6px;min-width:0;margin-left:auto;overflow-x:auto;scrollbar-width:thin}
.os-topnav__link{flex:0 0 auto;min-height:38px;display:inline-flex;align-items:center;justify-content:center;border:1px solid transparent;border-radius:8px;padding:8px 11px;color:#c7d8e8;text-decoration:none;font-size:.92rem;font-weight:800;white-space:nowrap}
.os-topnav__link:hover{color:#fff;border-color:rgba(141,200,216,.34);background:rgba(255,255,255,.07)}
.os-topnav__link[aria-current="page"]{color:#051019;background:#7fd3c6;border-color:#7fd3c6}
@media(max-width:760px){.os-topnav__inner{min-height:76px;align-items:flex-start;flex-direction:column;justify-content:center;gap:8px;padding:10px 0}.os-topnav__links{width:100%;margin-left:0;padding-bottom:4px}}
CSS

sudo tee "$WEBROOT/assets/os_nav.js" >/dev/null <<'JS'
(function(){
  const links=[
    ["Accueil","/"],
    ["Le Projet","/projet/"],
    ["Dashboard","/dashboard/"],
    ["Simulations IA","/dashboard/simulations/"],
    ["Bibliothèque","/dashboard/simulations/library/"],
    ["OSINT v1.2","/dashboard/transparence/osint/"],
    ["Transparence","/dashboard/transparence/infrastructure/"],
    ["Podcast","/podcast/"]
  ];
  function normalizedPath(){
    const declared=document.body&&document.body.getAttribute("data-route");
    const path=declared||window.location.pathname||"/";
    if(path===""||path==="/index.html") return "/";
    return path.endsWith("/")?path:`${path}/`;
  }
  function buildNav(){
    const mounts=document.querySelectorAll("#os-topnav");
    mounts.forEach((node,index)=>{ if(index>0) node.remove(); });
    let header=document.getElementById("os-topnav");
    if(!header){ header=document.createElement("header"); header.id="os-topnav"; document.body.prepend(header); }
    header.className="os-topnav";
    const current=normalizedPath();
    const inner=document.createElement("div");
    inner.className="os-topnav__inner";
    const brand=document.createElement("a");
    brand.className="os-topnav__brand";
    brand.href="/";
    brand.textContent="Ocean Sentinelle";
    const nav=document.createElement("nav");
    nav.className="os-topnav__links";
    nav.setAttribute("aria-label","Navigation principale");
    links.forEach(([label,href])=>{
      const item=document.createElement("a");
      item.className="os-topnav__link";
      item.href=href;
      item.textContent=label;
      if(href===current) item.setAttribute("aria-current","page");
      nav.appendChild(item);
    });
    inner.appendChild(brand);
    inner.appendChild(nav);
    header.replaceChildren(inner);
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",buildNav); else buildNav();
})();
JS

echo "== Patch canonical HTML =="
tmp_py="$(mktemp)"
cat > "$tmp_py" <<'PY'
import re
from pathlib import Path
import sys

files = [Path(p) for p in sys.argv[1:]]

nav_link_css = '<link rel="stylesheet" href="/assets/os_nav.css">'
nav_script = '<script defer src="/assets/os_nav.js"></script>'
mount = '<div id="os-topnav"></div>'

def remove_legacy_nav(html: str) -> str:
    # Remove compact header/nav blocks used by dashboard subpages.
    html = re.sub(r'\n\s*<header[^>]*>\s*<nav\b.*?</nav>\s*</header>\s*', '\n', html, flags=re.I|re.S)
    # Remove multiline header blocks containing nav links.
    html = re.sub(r'\n\s*<header[^>]*>.*?<nav\b.*?</nav>.*?</header>\s*', '\n', html, flags=re.I|re.S)
    # Remove standalone nav blocks containing canonical labels.
    def repl_nav(m):
        text = m.group(0)
        labels = ["Dashboard", "Simulations IA", "OSINT v1.2", "Bibliothèque", "Infrastructure Overview", "Podcast", "Accueil", "Le Projet"]
        return "\n" if sum(label in text for label in labels) >= 2 else text
    html = re.sub(r'\n\s*<nav\b.*?</nav>\s*', repl_nav, html, flags=re.I|re.S)
    return html

for path in files:
    if not path.exists():
        continue
    html = path.read_text(encoding="utf-8", errors="replace")
    html = html.replace('id=\\"os-topnav\\"', 'id="os-topnav"')
    html = re.sub(r'<link[^>]+href="/assets/os_nav(?:_v2)?\.css"[^>]*>\s*', '', html, flags=re.I)
    html = re.sub(r'<script[^>]+src="/assets/os_nav(?:_v2)?\.js"[^>]*>\s*</script>\s*', '', html, flags=re.I)
    html = re.sub(r'\s*<div\s+id="os-topnav"\s*>\s*</div>\s*', '\n', html, flags=re.I)
    html = remove_legacy_nav(html)

    if "</head>" in html:
        html = html.replace("</head>", f"  {nav_link_css}\n  {nav_script}\n</head>", 1)
    if "<body" in html:
        html = re.sub(r'(<body\b[^>]*>)', r'\1\n  ' + mount, html, count=1, flags=re.I)
    path.write_text(html, encoding="utf-8")
PY

sudo python3 "$tmp_py" $CANONICAL_HTML
rm -f "$tmp_py"

echo "== Fix simulation doctrine/theme =="
SIM="$WEBROOT/dashboard/simulations/index.html"
if [ -f "$SIM" ] && ! sudo grep -q 'truth_status="SCENARIO"' "$SIM"; then
  sudo python3 - "$SIM" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8", errors="replace")
needle="</h1>"
insert='''</h1>
    <p><strong>truth_status="SCENARIO"</strong> · <strong>shadow_mode=true</strong> · <strong>alert_allowed=false</strong> · <strong>decision_ready=false</strong></p>'''
s=s.replace(needle, insert, 1)
p.write_text(s, encoding="utf-8")
PY
fi

echo "== Permissions =="
sudo chown -R root:root "$WEBROOT"
sudo find "$WEBROOT" -type d -exec chmod 0755 {} \;
sudo find "$WEBROOT" -type f -name '*.html' -exec chmod 0644 {} \;
sudo chmod 0644 "$WEBROOT/assets/os_nav.css" "$WEBROOT/assets/os_nav.js"

echo "== Verify nav shape =="
failed=0
for f in $CANONICAL_HTML; do
  [ -f "$f" ] || continue
  css=$(sudo grep -c '/assets/os_nav.css' "$f" || true)
  js=$(sudo grep -c '/assets/os_nav.js' "$f" || true)
  mount_count=$(sudo grep -c 'id="os-topnav"' "$f" || true)
  broken=$(sudo grep -c 'id=\\"os-topnav\\"' "$f" || true)
  inline=$(sudo grep -ci '<nav\b' "$f" || true)
  echo "$f css=$css js=$js mount=$mount_count broken=$broken inline_nav=$inline"
  [ "$css" = 1 ] && [ "$js" = 1 ] && [ "$mount_count" = 1 ] && [ "$broken" = 0 ] && [ "$inline" = 0 ] || failed=1
done

if [ "$failed" != 0 ]; then
  echo "FAIL nav verification. Restore with: sudo tar -C $(dirname "$WEBROOT") -xzf $BACKUP"
  exit 1
fi

echo "patch_webroot_nav.sh passed"

