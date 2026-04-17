# 🌊 Ocean Sentinel Ops - Agent Skill

Compétence d'administration pour surveiller et interroger l'infrastructure Ocean Sentinel V3.0 déployée sur VPS Hostinger.

## 🎯 Objectif

Permettre à l'agent IA local de :
- Vérifier l'état des conteneurs Docker sur le VPS
- Consulter les logs d'ingestion et de backup
- Interroger la base TimescaleDB en lecture seule
- Générer des rapports de santé du système

## 📁 Structure

```
ocean-sentinel-ops/
├── SKILL.md                    # Documentation de la compétence (frontmatter YAML)
├── README.md                   # Ce fichier
└── scripts/
    ├── check_logs.sh           # Consultation des logs VPS via SSH
    └── query_prod_db.py        # Requêtes SQL en lecture seule
```

## 🚀 Installation

### 1. Créer le fichier de configuration

```bash
# Copier le template
cp .env.vps.example .env.vps

# Éditer avec vos credentials
nano .env.vps
```

### 2. Installer les dépendances Python

```bash
pip install psycopg2-binary python-dotenv requests
```

### 3. Rendre les scripts exécutables (Linux/Mac)

```bash
chmod +x .agents/skills/ocean-sentinel-ops/scripts/*.sh
```

## 📖 Utilisation

### Via l'Agent IA

L'agent détectera automatiquement cette compétence. Vous pouvez demander :

> "Vérifie si de nouvelles données ont été ingérées sur le VPS aujourd'hui"

> "Montre-moi les derniers logs du service d'ingestion"

> "Combien de données avons-nous en base de production ?"

> "Donne-moi un rapport complet du système Ocean Sentinel"

### Utilisation Manuelle

**Consulter les logs :**
```bash
cd .agents/skills/ocean-sentinel-ops
./scripts/check_logs.sh ingestion
./scripts/check_logs.sh backup
./scripts/check_logs.sh all
```

**Interroger la base de données :**
```bash
cd .agents/skills/ocean-sentinel-ops
python scripts/query_prod_db.py count
python scripts/query_prod_db.py today
python scripts/query_prod_db.py last
python scripts/query_prod_db.py stats
python scripts/query_prod_db.py health
```

## 🔐 Sécurité

- **Mode lecture seule** : Aucune modification possible sur le VPS
- **Requêtes SQL SELECT uniquement** : Pas d'INSERT/UPDATE/DELETE
- **Credentials dans .env.vps** : Fichier dans .gitignore
- **Timeout de connexion** : 10 secondes max

## 📊 Exemples de Sortie

### Requête Count

```json
{
  "success": true,
  "query": "count",
  "data": {
    "total_records": 3
  },
  "timestamp": "2026-04-17T02:00:00"
}
```

### Requête Stats

```json
{
  "success": true,
  "query": "stats",
  "data": {
    "total_records": 3,
    "first_record": "2026-04-16T22:56:56+00:00",
    "last_record": "2026-04-16T23:56:56+00:00",
    "stations_count": 1,
    "today_records": 3,
    "quality_distribution": [
      {"flag": 1, "count": 3}
    ]
  },
  "timestamp": "2026-04-17T02:00:00"
}
```

## 🛠️ Dépannage

### Erreur de connexion SSH

```bash
# Tester manuellement
ssh root@76.13.43.3

# Vérifier les credentials dans .env.vps
cat .env.vps
```

### Erreur de connexion DB

```bash
# Tester le port
telnet 76.13.43.3 6543

# Vérifier que TimescaleDB est running
ssh root@76.13.43.3 "docker ps | grep timescaledb"
```

## 📝 Notes

- Les logs sont limités aux 50 dernières lignes
- Les requêtes DB ont un timeout de 10 secondes
- En cas d'erreur, vérifier d'abord la connectivité réseau

## 🔄 Mises à Jour

**Version 1.0.0** (2026-04-17)
- Création initiale de la compétence
- Scripts check_logs.sh et query_prod_db.py
- Support des requêtes count, today, last, stats, health

---

**Auteur :** Ocean Sentinel Team  
**Licence :** MIT  
**Contact :** contact@ocean-sentinel.fr
