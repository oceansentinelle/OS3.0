# 🚀 Déploiement Frontend Ocean Sentinelle V3.1

## 📋 Prérequis VPS

- Node.js 18+ (pour Tailwind CLI)
- Nginx configuré
- Accès SSH root@76.13.43.3

---

## 🔧 Installation Tailwind CLI (VPS)

```bash
# Connexion VPS
ssh root@76.13.43.3

# Installation Node.js 20 LTS (si absent)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Vérification
node --version  # v20.x.x
npm --version   # 10.x.x

# Installation Tailwind CSS CLI (global)
npm install -g tailwindcss

# Vérification
tailwindcss --help
```

---

## 📦 Déploiement Fichiers

### Depuis Windows (Local)

```powershell
# Copier fichiers sources
scp -r C:\Users\ktprt\Documents\OSwindsurf\public\* root@76.13.43.3:/opt/oceansentinel/frontend/

# Vérifier transfert
ssh root@76.13.43.3 "ls -lah /opt/oceansentinel/frontend/"
```

---

## 🎨 Compilation Tailwind CSS (VPS)

```bash
# Connexion VPS
ssh root@76.13.43.3

# Aller dans dossier frontend
cd /opt/oceansentinel/frontend

# Compiler Tailwind (production - minifié + purgé)
tailwindcss -i ./assets/css/input.css -o ./assets/css/main.css --minify

# Vérifier fichier généré
ls -lh assets/css/main.css
# Devrait faire ~10-50 KB (purgé)

# Permissions correctes
chown -R www-data:www-data /opt/oceansentinel/frontend/
chmod -R 755 /opt/oceansentinel/frontend/
```

---

## 🔄 Rechargement Nginx

```bash
# Tester configuration
nginx -t

# Recharger Nginx (sans downtime)
systemctl reload nginx

# Vérifier status
systemctl status nginx
```

---

## ✅ Validation Déploiement

```bash
# Tester localement sur VPS
curl -I https://oceansentinelle.fr

# Vérifier CSS chargé
curl https://oceansentinelle.fr/assets/css/main.css | head -20

# Vérifier favicon
curl -I https://oceansentinelle.fr/assets/images/favicon.svg
```

### Depuis navigateur

1. Ouvrir https://oceansentinelle.fr
2. Inspecter (F12) → Network → Vérifier `main.css` (200 OK)
3. Vérifier responsive (Ctrl+Shift+M)
4. Tester accessibilité (Lighthouse)

---

## 🔁 Workflow Mise à Jour

```bash
# 1. Modifier fichiers HTML localement
# 2. Déployer
scp C:\Users\ktprt\Documents\OSwindsurf\public\*.html root@76.13.43.3:/opt/oceansentinel/frontend/

# 3. Si modification CSS
scp C:\Users\ktprt\Documents\OSwindsurf\public\assets\css\input.css root@76.13.43.3:/opt/oceansentinel/frontend/assets/css/

# 4. Recompiler Tailwind sur VPS
ssh root@76.13.43.3 "cd /opt/oceansentinel/frontend && tailwindcss -i ./assets/css/input.css -o ./assets/css/main.css --minify"

# 5. Pas besoin de recharger Nginx (fichiers statiques)
```

---

## 📊 Optimisations Production

### Cache Nginx (optionnel)

```nginx
# /etc/nginx/sites-available/oceansentinelle.fr
location ~* \.(css|js|svg|png|jpg|jpeg|gif|ico)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Compression Gzip

```nginx
gzip on;
gzip_types text/css application/javascript image/svg+xml;
gzip_min_length 1000;
```

---

## 🐛 Dépannage

### CSS non chargé
```bash
# Vérifier fichier existe
ls -lh /opt/oceansentinel/frontend/assets/css/main.css

# Vérifier permissions
ls -l /opt/oceansentinel/frontend/assets/css/

# Recompiler
cd /opt/oceansentinel/frontend
tailwindcss -i ./assets/css/input.css -o ./assets/css/main.css --minify
```

### Tailwind CLI non trouvé
```bash
# Réinstaller
npm install -g tailwindcss

# Vérifier PATH
which tailwindcss
```

---

## 📝 Notes Sécurité

- ✅ Aucun CDN externe (conformité M-23-22)
- ✅ Tout auto-hébergé sur VPS
- ✅ HTTPS obligatoire (Let's Encrypt)
- ✅ Headers sécurité Nginx activés
- ✅ Permissions restrictives (www-data)
