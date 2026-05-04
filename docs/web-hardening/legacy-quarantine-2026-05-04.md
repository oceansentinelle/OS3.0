# Legacy Asset Quarantine - 2026-05-04

No legacy asset was moved in this workspace because no pre-existing `/assets/` or `public/assets/`
legacy file was present before the nav consolidation.

Proof used:

```sh
find public -type f
sh scripts/audit_assets_references.sh
```

Current referenced assets:

```text
assets/os_nav.css
assets/os_nav.js
styles.css
```

Current orphan result:

```text
none
```

Rollback model if production contains extra legacy files:

```sh
mkdir -p /var/www/oceansentinelle/assets/_quarantine/2026-05-04
mv /var/www/oceansentinelle/assets/<legacy-file> /var/www/oceansentinelle/assets/_quarantine/2026-05-04/
nginx -t && systemctl reload nginx
```

Only move files after confirming they are absent from canonical HTML references and recent access logs.
