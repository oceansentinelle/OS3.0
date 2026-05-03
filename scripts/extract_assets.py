#!/usr/bin/env python3
"""Build a public asset manifest from HTML href/src references."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name not in {"href", "src"} or not value:
                continue
            parsed = urlparse(value)
            if parsed.scheme or parsed.netloc:
                continue
            if parsed.path.startswith("/assets/") or parsed.path.startswith("assets/"):
                self.refs.add(parsed.path if parsed.path.startswith("/") else f"/{parsed.path}")


def html_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for base in (root, root / "public", root / "dashboard"):
        if base.exists():
            candidates.extend(base.rglob("*.html"))
    return sorted(set(candidates))


def asset_files(root: Path) -> dict[str, str]:
    assets_dir = root / "assets"
    if not assets_dir.exists() and (root / "public" / "assets").exists():
        assets_dir = root / "public" / "assets"
    found: dict[str, str] = {}
    if assets_dir.exists():
        for path in assets_dir.rglob("*"):
            if path.is_file():
                public_path = "/assets/" + path.relative_to(assets_dir).as_posix()
                found[public_path] = str(path)
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root or deployed webroot")
    parser.add_argument("--output", default="-", help="Output JSON path, or '-' for stdout")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    assets = asset_files(root)
    refs: dict[str, list[str]] = {}
    for html in html_files(root):
        parser_obj = AssetParser()
        parser_obj.feed(html.read_text(encoding="utf-8", errors="ignore"))
        for ref in sorted(parser_obj.refs):
            refs.setdefault(ref, []).append(str(html))

    manifest = {
        "root": str(root),
        "referenced_assets": {ref: refs[ref] for ref in sorted(refs)},
        "orphan_assets": {ref: assets[ref] for ref in sorted(set(assets) - set(refs))},
        "missing_assets": {ref: refs[ref] for ref in sorted(set(refs) - set(assets))},
    }

    payload = json.dumps(manifest, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(payload)
    else:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    return 0 if not manifest["missing_assets"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
