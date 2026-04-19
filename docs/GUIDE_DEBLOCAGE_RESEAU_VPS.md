# Guide de Déblocage Réseau VPS Hostinger

## 🚨 Problème Actuel

**Symptôme** : Ports 80/8080 en timeout depuis l'extérieur  
**Cause** : Cloud Firewall Hostinger bloque le trafic HTTP/HTTPS  
**Impact** : Webhooks Stripe impossibles, site inaccessible  
**Priorité** : CRITIQUE (Stabilité > Sécurité)

---

## 📋 Diagnostic Actuel

### Tests Effectués
```bash
# ✅ SSH fonctionne (port 22)
Test-NetConnection -ComputerName 76.13.43.3 -Port 22
# Résultat: TcpTestSucceeded : True

# ❌ HTTP en timeout (port 80)
Test-NetConnection -ComputerName 76.13.43.3 -Port 80
# Résultat: TcpTestSucceeded : False (Timeout)

# ❌ HTTPS en timeout (port 443)
Test-NetConnection -ComputerName 76.13.43.3 -Port 443
# Résultat: TcpTestSucceeded : False (Timeout)
```

### Architecture du Filtrage Hostinger

```
Internet → [Cloud Firewall Hostinger] → [VPS UFW] → [Nginx] → [Application]
            ↑ BLOQUE ICI                ↑ Jamais atteint
```

**Ordre de traitement** :
1. **Cloud Firewall** (hPanel) - Filtrage AVANT le VPS
2. **UFW** (VPS local) - Filtrage AU NIVEAU du VPS
3. **Nginx** - Reverse proxy applicatif

---

## 🔧 Solution : Configuration hPanel

### Étape 1 : Accéder au Cloud Firewall

1. **Connexion au hPanel**
   - URL : https://hpanel.hostinger.com
   - Identifiants : Votre compte Hostinger

2. **Navigation**
   ```
   hPanel
   └── VPS
       └── Sélectionner votre VPS (76.13.43.3)
           └── Paramètres
               └── Firewall (ou "Cloud Firewall")
   ```

3. **Interface Firewall**
   - Vous devriez voir une liste de règles existantes
   - Probablement uniquement SSH (port 22) est autorisé

### Étape 2 : Ajouter les Règles HTTP/HTTPS

#### Règle 1 : HTTP (Port 80)

```
┌─────────────────────────────────────────────────────────┐
│ Ajouter une règle de pare-feu                          │
├─────────────────────────────────────────────────────────┤
│ Action:      [Accept ▼]                                │
│ Protocol:    [TCP ▼]                                   │
│ Port:        [80]                                       │
│ Source:      [0.0.0.0/0]  (Tout le monde)             │
│ Description: [HTTP Traffic]                            │
│                                                         │
│              [Annuler]  [Ajouter la règle]            │
└─────────────────────────────────────────────────────────┘
```

**Paramètres exacts** :
- **Action** : `Accept`
- **Protocol** : `TCP`
- **Port** : `80`
- **Source** : `0.0.0.0/0` (ou "Any" selon l'interface)
- **Description** : `HTTP Traffic`

#### Règle 2 : HTTPS (Port 443)

```
┌─────────────────────────────────────────────────────────┐
│ Ajouter une règle de pare-feu                          │
├─────────────────────────────────────────────────────────┤
│ Action:      [Accept ▼]                                │
│ Protocol:    [TCP ▼]                                   │
│ Port:        [443]                                      │
│ Source:      [0.0.0.0/0]  (Tout le monde)             │
│ Description: [HTTPS Traffic]                           │
│                                                         │
│              [Annuler]  [Ajouter la règle]            │
└─────────────────────────────────────────────────────────┘
```

**Paramètres exacts** :
- **Action** : `Accept`
- **Protocol** : `TCP`
- **Port** : `443`
- **Source** : `0.0.0.0/0`
- **Description** : `HTTPS Traffic`

### Étape 3 : Appliquer les Modifications

1. **Sauvegarder** : Cliquer sur "Appliquer" ou "Sauvegarder les modifications"
2. **Délai de propagation** : 30 secondes à 2 minutes
3. **Pas de redémarrage nécessaire** : Les règles sont appliquées à chaud

---

## ✅ Vérification Post-Configuration

### Test 1 : Depuis Windows (PowerShell)

```powershell
# Test HTTP (port 80)
Test-NetConnection -ComputerName 76.13.43.3 -Port 80

# Résultat attendu:
# TcpTestSucceeded : True
# ✅ Si True → Firewall débloqué
# ❌ Si False → Attendre 2 min et réessayer

# Test HTTPS (port 443)
Test-NetConnection -ComputerName 76.13.43.3 -Port 443

# Résultat attendu:
# TcpTestSucceeded : True
```

### Test 2 : Depuis le VPS (SSH)

```bash
# Connexion SSH
ssh root@76.13.43.3

# Vérifier UFW (firewall local)
ufw status verbose

# Résultat attendu:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere

# Si les règles 80/443 sont absentes, les ajouter:
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload

# Vérifier que Nginx écoute
netstat -tlnp | grep -E ':(80|443)'

# Résultat attendu:
# tcp  0  0 0.0.0.0:80    0.0.0.0:*  LISTEN  1234/nginx
# tcp  0  0 0.0.0.0:443   0.0.0.0:*  LISTEN  1234/nginx
```

### Test 3 : Depuis l'Extérieur (curl)

```bash
# Test HTTP depuis votre machine locale
curl -I http://76.13.43.3

# Résultat attendu (si Nginx configuré):
# HTTP/1.1 200 OK
# Server: nginx/1.24.0
# ...

# OU (si redirection HTTPS):
# HTTP/1.1 301 Moved Permanently
# Location: https://76.13.43.3/

# Test HTTPS (si certificat SSL configuré)
curl -I https://76.13.43.3

# Résultat attendu:
# HTTP/2 200
# server: nginx/1.24.0
```

### Test 4 : Validation avec tcpdump

```bash
# Sur le VPS, capturer le trafic HTTP
tcpdump -i eth0 port 80 -n

# Depuis votre machine, faire une requête:
curl http://76.13.43.3

# Résultat attendu dans tcpdump:
# 12:34:56.789 IP VOTRE_IP.12345 > 76.13.43.3.80: Flags [S], seq 123456
# 12:34:56.790 IP 76.13.43.3.80 > VOTRE_IP.12345: Flags [S.], seq 789012

# ✅ Si vous voyez des paquets → Firewall OK
# ❌ Si aucun paquet → Firewall toujours bloqué
```

---

## 🔒 Sécurisation Post-Déblocage

### 1. Limiter les Sources (Optionnel)

Si vous voulez restreindre l'accès à certaines IPs :

```
# Au lieu de 0.0.0.0/0, utiliser:
Source: VOTRE_IP/32  (Une seule IP)
Source: 1.2.3.0/24   (Plage d'IPs)
```

**⚠️ Attention** : Pour les webhooks Stripe, vous DEVEZ autoriser les IPs Stripe :
- Liste officielle : https://stripe.com/docs/ips

### 2. Activer fail2ban (Protection Brute Force)

```bash
# Installation
apt update
apt install fail2ban -y

# Configuration pour Nginx
cat > /etc/fail2ban/jail.local << 'EOF'
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 3600

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 3600
EOF

# Démarrer fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Vérifier le statut
fail2ban-client status
```

### 3. Configurer Rate Limiting dans Nginx

```nginx
# /etc/nginx/nginx.conf
http {
    # Limiter à 10 requêtes/seconde par IP
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    # Limiter les connexions simultanées
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    
    server {
        listen 80;
        
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            limit_conn conn_limit 10;
            
            proxy_pass http://backend:8000;
        }
    }
}
```

---

## 🐛 Dépannage

### Problème 1 : Règles ajoutées mais toujours en timeout

**Causes possibles** :
1. Délai de propagation (attendre 2-5 minutes)
2. Cache DNS (vider le cache : `ipconfig /flushdns`)
3. Règles dans le mauvais ordre (vérifier la priorité)

**Solution** :
```bash
# Vérifier l'ordre des règles dans hPanel
# Les règles "Accept" doivent être AVANT les règles "Deny"

# Exemple d'ordre correct:
1. Accept TCP 22 (SSH)
2. Accept TCP 80 (HTTP)
3. Accept TCP 443 (HTTPS)
4. Deny All (si règle par défaut)
```

### Problème 2 : Port ouvert mais Nginx ne répond pas

**Diagnostic** :
```bash
# Vérifier si Nginx est démarré
systemctl status nginx

# Si arrêté, démarrer:
systemctl start nginx

# Vérifier les logs d'erreur
tail -f /var/log/nginx/error.log

# Tester la configuration
nginx -t
```

### Problème 3 : Certificat SSL invalide

**Solution temporaire** :
```bash
# Tester sans vérification SSL
curl -k https://76.13.43.3

# Générer un certificat Let's Encrypt
apt install certbot python3-certbot-nginx -y
certbot --nginx -d oceansentinel.fr -d www.oceansentinel.fr
```

---

## 📊 Checklist de Validation Complète

```markdown
## Firewall Hostinger
- [ ] Connexion au hPanel réussie
- [ ] Règle HTTP (80) ajoutée : Accept, TCP, 0.0.0.0/0
- [ ] Règle HTTPS (443) ajoutée : Accept, TCP, 0.0.0.0/0
- [ ] Modifications sauvegardées
- [ ] Attente 2 minutes (propagation)

## Tests de Connectivité
- [ ] Test-NetConnection port 80 → True
- [ ] Test-NetConnection port 443 → True
- [ ] curl http://76.13.43.3 → Réponse HTTP
- [ ] tcpdump capture des paquets entrants

## Configuration VPS
- [ ] UFW autorise 80/tcp
- [ ] UFW autorise 443/tcp
- [ ] Nginx écoute sur 0.0.0.0:80
- [ ] Nginx écoute sur 0.0.0.0:443
- [ ] nginx -t → Configuration OK

## Sécurité
- [ ] fail2ban installé et actif
- [ ] Rate limiting Nginx configuré
- [ ] Logs d'accès activés
- [ ] Certificat SSL valide (Let's Encrypt)

## Tests Stripe
- [ ] Webhook endpoint accessible publiquement
- [ ] Stripe CLI peut envoyer des événements de test
- [ ] Signature Stripe validée correctement
```

---

## 🚀 Prochaines Étapes (Après Déblocage)

### 1. Tester l'Endpoint Webhook Stripe

```bash
# Installer Stripe CLI
# https://stripe.com/docs/stripe-cli

# Se connecter
stripe login

# Tester l'envoi d'événement
stripe trigger payment_intent.succeeded \
  --webhook-endpoint https://76.13.43.3/api/webhooks/stripe

# Vérifier les logs
docker-compose logs -f api
```

### 2. Configurer le Webhook dans Stripe Dashboard

```
1. Aller sur https://dashboard.stripe.com/webhooks
2. Cliquer "Add endpoint"
3. URL: https://oceansentinel.fr/api/webhooks/stripe
4. Événements à écouter:
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.payment_succeeded
   - invoice.payment_failed
5. Copier le "Signing secret" (whsec_...)
6. Ajouter dans .env: STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Implémenter le Worker Asynchrone

Une fois le réseau validé, nous créerons :
- Worker de traitement des événements Stripe
- Dead Letter Queue pour les échecs
- Dashboard de monitoring
- Système de retry automatique

---

## 📞 Support Hostinger

Si vous rencontrez des difficultés avec le hPanel :

**Support Hostinger** :
- Chat en direct : https://www.hostinger.fr/contact
- Email : support@hostinger.com
- Téléphone : +33 1 76 54 48 85
- Documentation : https://support.hostinger.com/fr/

**Question à poser** :
> "Je ne parviens pas à accéder aux ports 80 et 443 de mon VPS (IP: 76.13.43.3) 
> depuis l'extérieur. Le port 22 (SSH) fonctionne. Comment configurer le Cloud 
> Firewall pour autoriser le trafic HTTP/HTTPS ?"

---

**Document créé le** : 19 avril 2026  
**Version** : 1.0  
**Priorité** : CRITIQUE
