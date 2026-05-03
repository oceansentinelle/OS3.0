#!/usr/bin/env python3
"""Check that canonical public HTML pages use the shared os_nav component."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED_LABELS = [
    "Accueil",
    "Le Projet",
    "Dashboard",
    "Simulations IA",
    "Bibliothèque",
    "OSINT v1.2",
    "Infrastructure Overview",
    "Podcast",
]

CANONICAL_HTML = [
    "public/index.html",
    "public/projet/index.html",
    "public/podcast/index.html",
    "public/simulations/index.html",
    "public/transparence/index.html",
    "public/404.html",
    "dashboard/index.html",
    "dashboard/simulations/index.html",
    "dashboard/simulations/library/index.html",
    "dashboard/transparence/osint/index.html",
    "dashboard/transparence/infrastructure/index.html",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    nav_js = root / "public" / "assets" / "os_nav.js"
    nav_css = root / "public" / "assets" / "os_nav.css"
    if not nav_js.exists():
        fail("public/assets/os_nav.js missing")
    if not nav_css.exists():
        fail("public/assets/os_nav.css missing")

    js = nav_js.read_text(encoding="utf-8", errors="ignore")
    labels = re.findall(r'label:\s*"([^"]+)"', js)
    if labels != EXPECTED_LABELS:
        fail(f"nav labels/order mismatch: {labels}")

    for rel in CANONICAL_HTML:
        path = root / rel
        if not path.exists():
            fail(f"{rel} missing")
        html = path.read_text(encoding="utf-8", errors="ignore")
        if "/assets/os_nav.css" not in html:
            fail(f"{rel} missing os_nav.css")
        if "/assets/os_nav.js" not in html:
            fail(f"{rel} missing os_nav.js")
        if 'id="os-topnav"' not in html:
            fail(f"{rel} missing #os-topnav")
        if "data-os-nav" in html or "/assets/nav.js" in html:
            fail(f"{rel} still uses legacy nav")
        if re.search(r"<nav\b", html, re.IGNORECASE):
            fail(f"{rel} contains inline <nav>")

    print("OK: shared os_nav is consistent across canonical pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
