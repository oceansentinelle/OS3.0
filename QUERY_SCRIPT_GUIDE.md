# 🐍 Guide du Script de Requête Python - Ocean Sentinel

## 📦 Installation

### 1. Installer Python (si nécessaire)

**Windows:**
```powershell
# Télécharger depuis python.org ou utiliser winget
winget install Python.Python.3.12
```

**Linux (VPS):**
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

### 2. Installer les Dépendances

```bash
# Depuis le répertoire du projet
pip install -r requirements.txt

# Ou installation manuelle
pip install psycopg2-binary python-dotenv
```

---

## 🚀 Utilisation

### Configuration

Le script utilise automatiquement le fichier `.env` pour se connecter.

**Fichier `.env` (déjà configuré) :**
```env
POSTGRES_USER=oceansentinel
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_DB=oceansentinelle
POSTGRES_PORT=6543
```

Le script cherche automatiquement le `.env` dans le répertoire parent.

---

## 📋 Exemples d'Utilisation

### 1. Requête Simple

```bash
# Depuis Windows
python scripts\query.py "SELECT * FROM barag.sensor_data LIMIT 5"

# Depuis Linux
python3 scripts/query.py "SELECT * FROM barag.sensor_data LIMIT 5"
```

**Sortie (JSON) :**
```json
[
  {
    "time": "2026-04-16T13:54:48.449861+00:00",
    "station_id": "BARAG",
    "temperature_air": 22.5,
    "temperature_water": 18.3,
    "salinity": 35.2,
    "ph": 8.1
  }
]
```

### 2. Format Tableau

```bash
python scripts\query.py "SELECT * FROM barag.sensor_data LIMIT 3" --format table
```

**Sortie :**
```
time                          | station_id | temperature_air | temperature_water | salinity | ph  
-------------------------------------------------------------------------------------------------
2026-04-16T13:54:48.449861+00 | BARAG      | 22.5            | 18.3              | 35.2     | 8.1
2026-04-16T12:54:48.449861+00 | BARAG      | 22.3            | 18.2              | 35.1     | 8.0

(2 ligne(s))
```

### 3. Format CSV

```bash
python scripts\query.py "SELECT * FROM barag.sensor_data LIMIT 5" --format csv > data.csv
```

### 4. Requête depuis un Fichier

```bash
# Créer un fichier SQL
echo "SELECT COUNT(*) as total FROM barag.sensor_data;" > query.sql

# Exécuter
python scripts\query.py --file query.sql
```

### 5. Sauvegarder dans un Fichier

```bash
python scripts\query.py "SELECT * FROM metadata.stations" --output stations.json
```

### 6. Mode Interactif

```bash
python scripts\query.py --interactive
```

**Exemple de session interactive :**
```
🌊 Ocean Sentinel - Mode Interactif TimescaleDB
============================================================
Tapez vos requêtes SQL (terminez par ';' et Entrée)
Commandes spéciales:
  \q ou exit  - Quitter
  \d          - Lister les tables
  \dt         - Lister les tables avec détails
  \c          - Afficher la configuration de connexion
============================================================

oceansentinel> SELECT COUNT(*) FROM barag.sensor_data;
count
-----
2    

(1 ligne(s))

oceansentinel> \d
schemaname | tablename      
--------------------------
analytics  | hourly_aggregates
barag      | sensor_data    
metadata   | stations       

(3 ligne(s))

oceansentinel> \q
Au revoir! 👋
```

---

## 🔧 Options Avancées

### Connexion Personnalisée

```bash
# Spécifier l'hôte et le port
python scripts\query.py "SELECT 1" --host VOTRE_IP_VPS --port 6543 --user oceansentinel --password votre_mdp

# Utiliser un fichier .env différent
python scripts\query.py "SELECT 1" --env-file /chemin/vers/.env
```

### Requêtes Complexes

```bash
# Statistiques sur 24h
python scripts\query.py "
SELECT 
    DATE_TRUNC('hour', time) as hour,
    AVG(temperature_air) as avg_temp_air,
    AVG(temperature_water) as avg_temp_water,
    COUNT(*) as samples
FROM barag.sensor_data 
WHERE time > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC
" --format table
```

### Agrégats Continus

```bash
# Voir les données agrégées par heure
python scripts\query.py "
SELECT * FROM analytics.hourly_aggregates 
WHERE bucket > NOW() - INTERVAL '7 days'
ORDER BY bucket DESC
LIMIT 10
" --format table
```

---

## 📊 Requêtes Utiles Prédéfinies

### Statistiques Générales

```bash
# Nombre total d'enregistrements
python scripts\query.py "SELECT COUNT(*) as total FROM barag.sensor_data"

# Plage de dates
python scripts\query.py "
SELECT 
    MIN(time) as first_record,
    MAX(time) as last_record,
    COUNT(*) as total_records
FROM barag.sensor_data
"

# Données par station
python scripts\query.py "
SELECT 
    station_id,
    COUNT(*) as records,
    MIN(time) as first,
    MAX(time) as last
FROM barag.sensor_data
GROUP BY station_id
" --format table
```

### Analyses Météo/Océano

```bash
# Moyennes sur 24h
python scripts\query.py "
SELECT 
    AVG(temperature_air) as avg_temp_air,
    AVG(temperature_water) as avg_temp_water,
    AVG(salinity) as avg_salinity,
    AVG(ph) as avg_ph,
    AVG(wind_speed) as avg_wind_speed
FROM barag.sensor_data 
WHERE time > NOW() - INTERVAL '24 hours'
"

# Min/Max températures par jour
python scripts\query.py "
SELECT 
    DATE(time) as date,
    MIN(temperature_air) as min_temp,
    MAX(temperature_air) as max_temp,
    AVG(temperature_air) as avg_temp
FROM barag.sensor_data 
GROUP BY DATE(time) 
ORDER BY date DESC 
LIMIT 7
" --format table
```

### Monitoring TimescaleDB

```bash
# Taille de la base
python scripts\query.py "
SELECT pg_size_pretty(pg_database_size('oceansentinelle')) as db_size
"

# Statistiques des chunks
python scripts\query.py "
SELECT 
    is_compressed,
    COUNT(*) as chunk_count
FROM timescaledb_information.chunks
GROUP BY is_compressed
"

# Jobs TimescaleDB
python scripts\query.py "
SELECT 
    job_id,
    application_name,
    schedule_interval,
    next_start
FROM timescaledb_information.jobs
" --format table
```

---

## 🔐 Sécurité

### Bonnes Pratiques

1. **Ne jamais mettre le mot de passe dans la ligne de commande**
   ```bash
   # ❌ MAUVAIS
   python scripts\query.py "SELECT 1" --password mon_mdp
   
   # ✅ BON (utiliser .env)
   python scripts\query.py "SELECT 1"
   ```

2. **Protéger le fichier .env**
   ```bash
   # Linux/VPS
   chmod 600 .env
   
   # Windows (PowerShell en admin)
   icacls .env /inheritance:r /grant:r "$env:USERNAME:(R)"
   ```

3. **Utiliser des requêtes paramétrées** (pour éviter l'injection SQL)
   Le script utilise automatiquement `psycopg2` qui protège contre l'injection SQL.

---

## 🐛 Dépannage

### Erreur: Module 'psycopg2' not found

```bash
pip install psycopg2-binary
```

### Erreur: Connexion refusée

```bash
# Vérifier que le pare-feu autorise le port 6543
# Vérifier l'IP et le port dans .env
# Tester la connexion
telnet VOTRE_IP_VPS 6543
```

### Erreur: Mot de passe incorrect

```bash
# Vérifier le mot de passe dans .env
cat .env | grep POSTGRES_PASSWORD

# Ou sur le VPS
ssh root@VOTRE_IP_VPS "cat ~/oceansentinel/.env | grep POSTGRES_PASSWORD"
```

### Erreur: Permission denied sur .env

```bash
# Windows
icacls .env

# Linux
chmod 600 .env
```

---

## 🔄 Intégration avec d'Autres Outils

### Utiliser avec Jupyter Notebook

```python
import subprocess
import json

# Exécuter une requête
result = subprocess.run(
    ['python', 'scripts/query.py', 'SELECT * FROM barag.sensor_data LIMIT 5'],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
print(data)
```

### Utiliser avec Pandas

```python
import pandas as pd
import psycopg2
import os

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Connexion
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 6543)),
    database=os.getenv('DB_NAME', 'oceansentinelle'),
    user=os.getenv('DB_USER', 'oceansentinel'),
    password=os.getenv('DB_PASSWORD')
)

# Requête vers DataFrame
df = pd.read_sql_query("SELECT * FROM barag.sensor_data LIMIT 100", conn)
print(df.head())

conn.close()
```

---

## 📚 Référence Complète des Options

```
usage: query.py [-h] [-f FILE] [-i] [-o OUTPUT] [--format {json,table,csv}]
                [--no-pretty] [--host HOST] [--port PORT] [--user USER]
                [--password PASSWORD] [--database DATABASE] [--env-file ENV_FILE]
                [query]

Options:
  query                 Requête SQL à exécuter
  -f, --file FILE       Fichier SQL contenant la requête
  -i, --interactive     Mode interactif
  -o, --output OUTPUT   Fichier de sortie (par défaut: stdout)
  --format {json,table,csv}
                        Format de sortie (défaut: json)
  --no-pretty           Désactiver le formatage JSON
  --host HOST           Hôte de la base de données
  --port PORT           Port de la base de données
  --user USER           Utilisateur de la base de données
  --password PASSWORD   Mot de passe (non recommandé, utilisez .env)
  --database DATABASE   Nom de la base de données
  --env-file ENV_FILE   Chemin vers le fichier .env
```

---

**🌊 Script de Requête Ocean Sentinel - Prêt à l'Emploi !**
