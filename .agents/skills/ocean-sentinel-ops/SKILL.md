---
name: ocean-sentinel-ops
description: Utilise cette compétence pour vérifier l'état du VPS Hostinger, lire les logs du conteneur d'ingestion, interroger l'API REST de production, vérifier les alertes SACS, ou exécuter des requêtes SQL de lecture sur la base TimescaleDB de production.
version: 2.0.0
author: Ocean Sentinel Team
tags:
  - vps
  - monitoring
  - timescaledb
  - production
  - oceanography
  - api
  - grafana
  - sacs
---

# Ocean Sentinel Ops - Compétence d'Administration VPS

Cette compétence permet de surveiller et d'interagir avec l'infrastructure Ocean Sentinel V3.0 déployée sur le VPS Hostinger en production.

## 🎯 Cas d'Usage

Utilise cette compétence lorsque l'utilisateur demande de :
- Vérifier l'état des conteneurs Docker sur le VPS
- Consulter les logs d'ingestion ou de backup
- Interroger la base de données TimescaleDB pour connaître le nombre de données
- Vérifier la dernière date d'ingestion
- Surveiller l'utilisation mémoire et CPU
- Valider que le système fonctionne correctement

## 📋 Scripts Disponibles

### 1. `monitor.py` - Monitoring Complet VPS (NOUVEAU)

**Utilisation :**
```bash
python scripts/monitor.py [--vps-ip IP] [--api-port PORT] [--station-id ID] [--json]
```

**Options :**
- `--vps-ip` : Adresse IP du VPS (défaut: 76.13.43.3)
- `--api-port` : Port de l'API (défaut: 8000)
- `--station-id` : ID de la station (défaut: VPS_PROD)
- `--json` : Sortie en JSON uniquement

**Exemples :**
```bash
# Monitoring complet avec affichage formaté
python scripts/monitor.py

# Monitoring avec IP personnalisée
python scripts/monitor.py --vps-ip 76.13.43.3

# Sortie JSON pour parsing
python scripts/monitor.py --json
```

**Ce que le script fait :**
- Interroge l'API REST (`GET /health`)
- Vérifie les alertes SACS (`GET /api/v1/alerts/sacs`)
- Récupère la dernière mesure (`GET /api/v1/station/{id}/latest`)
- Génère un rapport complet de santé
- Retourne un code de sortie (0 = healthy, 1 = unhealthy)

**Rapport généré :**
```json
{
  "timestamp": "2026-04-17T02:45:00",
  "overall_status": "healthy",
  "api": {
    "status": "healthy",
    "reachable": true
  },
  "database": {
    "status": "connected",
    "total_records": 3
  },
  "alerts": {
    "checked": true,
    "total": 0,
    "critical": 0,
    "warning": 0
  },
  "latest_measurement": {
    "found": true,
    "time": "2026-04-16T23:56:56+00:00",
    "station_id": "VPS_PROD",
    "temperature": 24.8,
    "salinity": 35.0,
    "quality_flag": 1
  }
}
```

---

### 2. `check_logs.sh` - Consultation des Logs

**Utilisation :**
```bash
./scripts/check_logs.sh [service]
```

**Services disponibles :**
- `ingestion` : Logs du service d'ingestion (par défaut)
- `timescaledb` : Logs de la base de données
- `backup` : Logs des backups automatiques
- `all` : Statut de tous les conteneurs

**Exemples :**
```bash
# Voir les logs d'ingestion (50 dernières lignes)
./scripts/check_logs.sh ingestion

# Voir les logs de backup
./scripts/check_logs.sh backup

# Voir le statut de tous les conteneurs
./scripts/check_logs.sh all
```

**Ce que le script fait :**
- Se connecte au VPS via SSH (76.13.43.3)
- Récupère les logs du conteneur demandé
- Affiche les 50 dernières lignes
- Filtre les informations importantes (erreurs, warnings, succès)

---

### 3. `query_prod_db.py` - Requêtes Base de Données

**Utilisation :**
```bash
python scripts/query_prod_db.py [query_type]
```

**Types de requêtes disponibles :**
- `count` : Nombre total d'enregistrements (par défaut)
- `today` : Nombre d'enregistrements du jour
- `last` : 5 dernières données insérées
- `stats` : Statistiques complètes (période, stations, qualité)
- `health` : Vérification de santé de la base

**Exemples :**
```bash
# Compter le nombre total d'enregistrements
python scripts/query_prod_db.py count

# Vérifier les données du jour
python scripts/query_prod_db.py today

# Voir les 5 dernières données
python scripts/query_prod_db.py last

# Statistiques complètes
python scripts/query_prod_db.py stats
```

**Ce que le script fait :**
- Se connecte à TimescaleDB sur le VPS (port 6543)
- Exécute une requête SQL en lecture seule
- Retourne le résultat en JSON formaté
- Gère les erreurs de connexion proprement

---

## 🔐 Configuration Requise

### Variables d'Environnement

Crée un fichier `.env.vps` à la racine du projet avec :

```env
VPS_HOST=76.13.43.3
VPS_USER=root
VPS_SSH_PORT=22

DB_HOST=76.13.43.3
DB_PORT=6543
DB_NAME=oceansentinelle
DB_USER=oceansentinel
DB_PASSWORD=OceanSentinel2026SecurePassword!
```

**Note :** Ce fichier est déjà dans `.gitignore` pour la sécurité.

### Prérequis Système

- **SSH :** Accès SSH configuré au VPS (clé ou mot de passe)
- **Python 3.11+** : Pour le script de requêtes DB
- **psycopg2** : `pip install psycopg2-binary python-dotenv`

---

## 📊 Instructions pour l'Agent

### Quand l'utilisateur demande un monitoring complet :

1. **Utilise le nouveau script `monitor.py`** pour obtenir un rapport complet
2. **Exécute la commande** :
   ```bash
   cd .agents/skills/ocean-sentinel-ops
   python scripts/monitor.py --json
   ```
3. **Parse le JSON retourné** et présente les informations de manière lisible
4. **Interprète les résultats** :
   - Si `overall_status` = "healthy" : Système opérationnel ✅
   - Si `overall_status` = "unhealthy" : Problème détecté ❌
   - Si `alerts.total` > 0 : Alertes SACS actives ⚠️
   - Si `database.total_records` = 0 : Aucune donnée ingérée
   - Si `latest_measurement.found` = false : Pas de données récentes

### Quand l'utilisateur demande de vérifier l'état de santé du VPS :

1. **Exécute le script de monitoring** :
   ```bash
   cd .agents/skills/ocean-sentinel-ops
   python scripts/monitor.py
   ```
2. **Résume les informations importantes** :
   - Statut API (reachable/unreachable)
   - Statut base de données (connected/disconnected)
   - Nombre total d'enregistrements
   - Alertes SACS actives
   - Dernière mesure disponible

### Quand l'utilisateur demande de vérifier les alertes SACS :

1. **Exécute le monitoring** avec focus sur les alertes
2. **Analyse la section `alerts`** du rapport JSON
3. **Signale les alertes critiques** :
   - 🔴 CRITICAL : pH < 7.8 ou O₂ < 150 µmol/kg
   - ⚠️ WARNING : pH < 7.9 ou O₂ < 175 µmol/kg
4. **Recommande des actions** si des alertes sont détectées

### Quand l'utilisateur demande de vérifier les logs :

1. **Identifie le service concerné** (ingestion, backup, timescaledb)
2. **Exécute le script approprié** :
   ```bash
   cd .agents/skills/ocean-sentinel-ops
   ./scripts/check_logs.sh [service]
   ```
3. **Analyse les logs** pour détecter :
   - ✅ Messages de succès (connexion DB, ingestion réussie)
   - ⚠️ Warnings (mémoire élevée, timeout)
   - ❌ Erreurs (échec connexion, permission denied)
4. **Résume les informations importantes** à l'utilisateur

### Quand l'utilisateur demande des statistiques de données :

1. **Identifie le type de requête** (count, today, last, stats)
2. **Exécute le script Python** :
   ```bash
   cd .agents/skills/ocean-sentinel-ops
   python scripts/query_prod_db.py [query_type]
   ```
3. **Parse le JSON retourné** et présente les résultats de manière lisible
4. **Interprète les données** :
   - Si count = 0 : Aucune donnée ingérée
   - Si today > 0 : Ingestion active aujourd'hui
   - Si last_data < 24h : Système opérationnel
   - Si last_data > 24h : Possible problème d'ingestion

### Quand l'utilisateur demande un rapport complet :

1. **Exécute les deux scripts** :
   ```bash
   ./scripts/check_logs.sh all
   python scripts/query_prod_db.py stats
   ```
2. **Combine les informations** :
   - État des conteneurs (running/stopped)
   - Utilisation mémoire/CPU
   - Nombre de données en base
   - Dernière ingestion
   - Erreurs récentes dans les logs
3. **Génère un rapport structuré** avec recommandations si nécessaire

---

## 🛡️ Sécurité

**Mode Lecture Seule :**
- Les scripts n'effectuent **AUCUNE modification** sur le VPS
- Les requêtes SQL sont en **SELECT uniquement**
- Aucune suppression, insertion ou mise à jour possible
- Connexions SSH en lecture seule (pas de commandes destructives)

**Gestion des Credentials :**
- Utilise des variables d'environnement (`.env.vps`)
- Jamais de mots de passe en dur dans les scripts
- Fichier `.env.vps` dans `.gitignore`

---

## 📈 Exemples de Requêtes Utilisateur

**L'utilisateur peut demander :**

> "Vérifie si de nouvelles données ont été ingérées sur le VPS aujourd'hui"

**Action de l'agent :**
```bash
python scripts/query_prod_db.py today
```

---

> "Montre-moi les derniers logs du service d'ingestion"

**Action de l'agent :**
```bash
./scripts/check_logs.sh ingestion
```

---

> "Combien de données avons-nous en base de production ?"

**Action de l'agent :**
```bash
python scripts/query_prod_db.py count
```

---

> "Donne-moi un rapport complet du système Ocean Sentinel"

**Action de l'agent :**
```bash
./scripts/check_logs.sh all
python scripts/query_prod_db.py stats
```

---

## 🔧 Dépannage

### Erreur de connexion SSH

**Symptôme :** `Permission denied` ou `Connection refused`

**Solution :**
1. Vérifier que `VPS_HOST` et `VPS_USER` sont corrects dans `.env.vps`
2. Tester la connexion manuellement : `ssh root@76.13.43.3`
3. Vérifier que la clé SSH est configurée

### Erreur de connexion DB

**Symptôme :** `could not connect to server` ou `password authentication failed`

**Solution :**
1. Vérifier que le port 6543 est accessible
2. Tester : `telnet 76.13.43.3 6543`
3. Vérifier les credentials dans `.env.vps`
4. S'assurer que le conteneur TimescaleDB est running

### Script non exécutable

**Symptôme :** `Permission denied` sur Linux/Mac

**Solution :**
```bash
chmod +x .agents/skills/ocean-sentinel-ops/scripts/*.sh
```

---

## 📝 Notes Importantes

- **Toujours vérifier** que les conteneurs sont running avant d'interroger la DB
- **Les logs sont limités** aux 50 dernières lignes pour éviter la surcharge
- **Les requêtes DB ont un timeout** de 10 secondes
- **En cas d'erreur**, toujours vérifier d'abord la connectivité réseau

---

## 🎯 Résumé pour l'Agent

**Cette compétence te permet de :**
1. ✅ Surveiller l'état du VPS en production
2. ✅ Consulter les logs des services Docker
3. ✅ Interroger la base TimescaleDB en lecture seule
4. ✅ Générer des rapports de santé du système
5. ✅ Détecter les problèmes d'ingestion ou de base de données

**Utilise cette compétence dès que l'utilisateur mentionne :**
- VPS, production, Hostinger
- Logs, monitoring, surveillance
- TimescaleDB, base de données
- Ingestion, données, enregistrements
- Statut, santé, rapport

---

**Version :** 1.0.0  
**Dernière mise à jour :** 2026-04-17  
**Auteur :** Ocean Sentinel Team
