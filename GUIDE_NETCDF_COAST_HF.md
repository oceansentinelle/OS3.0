# 🌊 Guide d'Utilisation des Fichiers NetCDF COAST-HF

**Ocean Sentinel V3.0 - Agent Data Engineer**  
**Infrastructure de Recherche ILICO - Réseau COAST-HF**

---

## 📋 Table des Matières

1. [Obtenir les Données COAST-HF](#obtenir-les-données-coast-hf)
2. [Structure des Fichiers NetCDF](#structure-des-fichiers-netcdf)
3. [Inspection des Fichiers](#inspection-des-fichiers)
4. [Ingestion avec Ocean Sentinel](#ingestion-avec-ocean-sentinel)
5. [Exemples Pratiques](#exemples-pratiques)
6. [Dépannage](#dépannage)

---

## 🔍 OBTENIR LES DONNÉES COAST-HF

### Sources Officielles

#### 1. Portail COAST-HF
**URL:** https://www.coast-hf.fr/data

**Accès:**
- Données publiques (temps réel et historique)
- Inscription gratuite requise
- Format: NetCDF CF-compliant

**Stations Bassin d'Arcachon:**
- **BARAG** (Bouée Arcachon Gascogne) - Station principale
- **ARCACHON_EYRAC** - Station côtière

#### 2. SEANOE (SEA scieNtific Open data Edition)
**URL:** https://www.seanoe.org/

**Recherche:**
```
Mots-clés: "COAST-HF" + "Arcachon" + "BARAG"
Filtres: Format NetCDF, Licence CC-BY
```

**Exemple de DOI:**
```
DOI: 10.17882/xxxxx (à remplacer par le DOI réel)
```

#### 3. Copernicus Marine Service (Données Complémentaires)
**URL:** https://marine.copernicus.eu/

**Produits utiles:**
- IBI (Iberia-Biscay-Ireland) - Modèles océaniques
- Observations in-situ (complément COAST-HF)

---

## 📦 STRUCTURE DES FICHIERS NETCDF COAST-HF

### Format Standard

Les fichiers NetCDF COAST-HF suivent la convention **CF (Climate and Forecast)**.

### Dimensions Typiques

```python
dimensions:
    time = UNLIMITED ;  # Dimension temporelle (principale)
    depth = 1 ;         # Profondeur (surface pour BARAG)
    latitude = 1 ;      # Position fixe de la bouée
    longitude = 1 ;     # Position fixe de la bouée
```

### Variables Principales

| Variable NetCDF | Nom Standard | Unité | Description |
|-----------------|--------------|-------|-------------|
| `TIME` | time | seconds since 1970-01-01 | Timestamp UTC |
| `LATITUDE` | latitude | degrees_north | 44.6°N (BARAG) |
| `LONGITUDE` | longitude | degrees_east | -1.2°W (BARAG) |
| `TEMP` | sea_water_temperature | °C | Température eau |
| `PSAL` | sea_water_practical_salinity | PSU | Salinité |
| `DOX2` | dissolved_oxygen | µmol/kg | Oxygène dissous |
| `PH_TOTAL` | sea_water_ph_reported_on_total_scale | pH | pH (échelle totale) |
| `ATMS` | air_pressure_at_sea_level | hPa | Pression atmosphérique |
| `WDIR` | wind_from_direction | degrees | Direction vent |
| `WSPD` | wind_speed | m/s | Vitesse vent |

### Attributs Globaux

```python
:title = "COAST-HF BARAG Time Series" ;
:institution = "CNRS - EPOC - Université de Bordeaux" ;
:source = "moored surface buoy" ;
:Conventions = "CF-1.6" ;
:station_id = "BARAG" ;
:geospatial_lat_min = 44.6 ;
:geospatial_lon_min = -1.2 ;
:time_coverage_start = "2024-01-01T00:00:00Z" ;
:time_coverage_end = "2024-12-31T23:59:59Z" ;
:license = "CC-BY 4.0" ;
```

---

## 🔬 INSPECTION DES FICHIERS

### Méthode 1: ncdump (Ligne de Commande)

```bash
# Installation (Ubuntu/Debian)
sudo apt install netcdf-bin

# Afficher la structure complète
ncdump -h fichier_barag.nc

# Afficher les 10 premières valeurs de température
ncdump -v TEMP fichier_barag.nc | head -20

# Extraire les métadonnées globales
ncdump -h fichier_barag.nc | grep ":" | head -20
```

### Méthode 2: Python (xarray)

```python
import xarray as xr

# Ouvrir le fichier
ds = xr.open_dataset('fichier_barag.nc')

# Afficher la structure
print(ds)

# Lister les variables
print(ds.data_vars)

# Afficher les attributs globaux
print(ds.attrs)

# Voir les dimensions
print(ds.dims)

# Statistiques sur une variable
print(ds['TEMP'].describe())

# Plage temporelle
print(f"Début: {ds.time.min().values}")
print(f"Fin: {ds.time.max().values}")
print(f"Nombre de points: {len(ds.time)}")
```

### Méthode 3: Script d'Inspection Automatique

```python
#!/usr/bin/env python3
"""
Script d'inspection rapide pour fichiers NetCDF COAST-HF
"""
import xarray as xr
import sys

def inspect_netcdf(filepath):
    """Inspecte un fichier NetCDF et affiche les informations clés."""
    
    print(f"📄 Inspection: {filepath}")
    print("=" * 70)
    
    ds = xr.open_dataset(filepath)
    
    # Métadonnées globales
    print("\n🏷️  MÉTADONNÉES GLOBALES:")
    for key in ['title', 'institution', 'station_id', 'Conventions', 'license']:
        if key in ds.attrs:
            print(f"  • {key}: {ds.attrs[key]}")
    
    # Dimensions
    print("\n📐 DIMENSIONS:")
    for dim, size in ds.dims.items():
        print(f"  • {dim}: {size}")
    
    # Variables
    print("\n📊 VARIABLES:")
    for var in ds.data_vars:
        var_data = ds[var]
        print(f"  • {var}")
        print(f"    - Nom long: {var_data.attrs.get('long_name', 'N/A')}")
        print(f"    - Unité: {var_data.attrs.get('units', 'N/A')}")
        print(f"    - Shape: {var_data.shape}")
        if var_data.size > 0:
            print(f"    - Min/Max: {float(var_data.min()):.2f} / {float(var_data.max()):.2f}")
    
    # Plage temporelle
    if 'time' in ds.dims:
        print("\n⏰ PLAGE TEMPORELLE:")
        print(f"  • Début: {ds.time.min().values}")
        print(f"  • Fin: {ds.time.max().values}")
        print(f"  • Points: {len(ds.time)}")
        
        # Fréquence d'échantillonnage
        if len(ds.time) > 1:
            dt = (ds.time[1] - ds.time[0]).values
            print(f"  • Intervalle: {dt}")
    
    # Taille du fichier
    import os
    size_mb = os.path.getsize(filepath) / 1024 / 1024
    print(f"\n💾 TAILLE: {size_mb:.2f} Mo")
    
    ds.close()
    print("\n" + "=" * 70)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inspect_netcdf.py fichier.nc")
        sys.exit(1)
    
    inspect_netcdf(sys.argv[1])
```

**Utilisation:**
```bash
python inspect_netcdf.py BARAG_2024_01.nc
```

---

## 🚀 INGESTION AVEC OCEAN SENTINEL

### Préparation

#### 1. Placer le Fichier NetCDF

```bash
# Sur votre PC Windows
mkdir -p data
# Copier le fichier téléchargé dans data/

# Sur le VPS
mkdir -p ~/oceansentinel/data
scp fichier_barag.nc root@VOTRE_IP_VPS:~/oceansentinel/data/
```

#### 2. Vérifier la Configuration

```bash
# Vérifier que le conteneur d'ingestion a accès au répertoire
docker compose -f docker-compose-v3.yml config | grep -A 5 "ingestion"
```

### Ingestion Simple

```bash
# Méthode 1: Via Docker Compose
docker compose -f docker-compose-v3.yml exec ingestion \
    python /app/ingestion_stream.py \
    /data/BARAG_2024_01.nc \
    --format netcdf

# Méthode 2: Directement sur le VPS (sans Docker)
cd ~/oceansentinel
python3 scripts/ingestion_stream.py \
    data/BARAG_2024_01.nc \
    --format netcdf \
    --chunk-size-netcdf 1000
```

### Ingestion avec Options Avancées

```bash
# Ajuster la taille des chunks (si fichier très volumineux)
docker compose -f docker-compose-v3.yml exec ingestion \
    python /app/ingestion_stream.py \
    /data/BARAG_2024_FULL.nc \
    --format netcdf \
    --chunk-size-netcdf 500 \
    --memory-limit 200

# Ingestion en arrière-plan avec logs
docker compose -f docker-compose-v3.yml exec -d ingestion \
    python /app/ingestion_stream.py /data/BARAG_2024_01.nc \
    > logs/ingestion_barag_2024_01.log 2>&1

# Suivre les logs en temps réel
tail -f logs/ingestion_barag_2024_01.log
```

### Vérification Post-Ingestion

```bash
# Compter les lignes insérées
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
    "SELECT COUNT(*) FROM barag.sensor_data WHERE data_source LIKE '%BARAG_2024_01%';"

# Voir les premières lignes
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
    "SELECT time, temperature_water, salinity, ph 
     FROM barag.sensor_data 
     WHERE data_source LIKE '%BARAG_2024_01%' 
     ORDER BY time 
     LIMIT 10;"

# Statistiques
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
    "SELECT 
        MIN(time) as first_record,
        MAX(time) as last_record,
        COUNT(*) as total_records,
        AVG(temperature_water) as avg_temp,
        AVG(salinity) as avg_salinity
     FROM barag.sensor_data 
     WHERE data_source LIKE '%BARAG_2024_01%';"
```

---

## 💡 EXEMPLES PRATIQUES

### Exemple 1: Télécharger et Ingérer Données COAST-HF

```bash
#!/bin/bash
# Script complet de téléchargement et ingestion

# Variables
STATION="BARAG"
YEAR="2024"
MONTH="01"
DATA_DIR="./data"
COAST_HF_URL="https://www.coast-hf.fr/data/download"  # URL exemple

# Créer le répertoire
mkdir -p $DATA_DIR

# Télécharger (adapter l'URL selon le portail COAST-HF)
echo "📥 Téléchargement des données ${STATION} ${YEAR}-${MONTH}..."
wget -O "${DATA_DIR}/${STATION}_${YEAR}_${MONTH}.nc" \
    "${COAST_HF_URL}/${STATION}/${YEAR}/${MONTH}/data.nc"

# Vérifier le téléchargement
if [ -f "${DATA_DIR}/${STATION}_${YEAR}_${MONTH}.nc" ]; then
    echo "✓ Fichier téléchargé: $(du -h ${DATA_DIR}/${STATION}_${YEAR}_${MONTH}.nc | cut -f1)"
    
    # Inspection rapide
    echo "🔍 Inspection du fichier..."
    ncdump -h "${DATA_DIR}/${STATION}_${YEAR}_${MONTH}.nc" | head -30
    
    # Ingestion
    echo "🚀 Ingestion dans TimescaleDB..."
    python3 scripts/ingestion_stream.py \
        "${DATA_DIR}/${STATION}_${YEAR}_${MONTH}.nc" \
        --format netcdf \
        --chunk-size-netcdf 1000
    
    echo "✅ Ingestion terminée!"
else
    echo "❌ Erreur de téléchargement"
    exit 1
fi
```

### Exemple 2: Ingestion Multiple (Année Complète)

```bash
#!/bin/bash
# Ingestion de tous les mois d'une année

STATION="BARAG"
YEAR="2024"

for MONTH in {01..12}; do
    FILE="${STATION}_${YEAR}_${MONTH}.nc"
    
    if [ -f "data/${FILE}" ]; then
        echo "📊 Ingestion ${FILE}..."
        
        python3 scripts/ingestion_stream.py \
            "data/${FILE}" \
            --format netcdf \
            --chunk-size-netcdf 1000
        
        # Pause entre chaque fichier
        sleep 5
    else
        echo "⚠️  Fichier manquant: ${FILE}"
    fi
done

echo "✅ Ingestion annuelle terminée!"
```

### Exemple 3: Script Python Personnalisé

```python
#!/usr/bin/env python3
"""
Script d'ingestion personnalisé pour fichiers NetCDF COAST-HF
avec mapping spécifique des variables
"""
import xarray as xr
import psycopg2
from datetime import datetime
import os

# Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '6543')),
    'database': 'oceansentinelle',
    'user': 'oceansentinel_writer',
    'password': os.getenv('DB_PASSWORD')
}

# Mapping variables NetCDF -> Base de données
VARIABLE_MAPPING = {
    'TEMP': 'temperature_water',
    'PSAL': 'salinity',
    'PH_TOTAL': 'ph',
    'DOX2': 'dissolved_oxygen',
    'ATMS': 'pressure',
    'WSPD': 'wind_speed',
    'WDIR': 'wind_direction'
}

def ingest_coast_hf_netcdf(filepath, station_id='BARAG'):
    """Ingère un fichier NetCDF COAST-HF dans TimescaleDB."""
    
    print(f"📂 Ouverture: {filepath}")
    ds = xr.open_dataset(filepath)
    
    # Connexion DB
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    total_inserted = 0
    
    # Itération sur les pas de temps
    for i, time_val in enumerate(ds.time.values):
        
        # Conversion timestamp
        time_dt = pd.Timestamp(time_val).to_pydatetime()
        
        # Extraction des valeurs
        record = {
            'time': time_dt,
            'station_id': station_id,
            'data_source': f'COAST-HF:{os.path.basename(filepath)}'
        }
        
        # Mapping des variables
        for nc_var, db_col in VARIABLE_MAPPING.items():
            if nc_var in ds:
                value = float(ds[nc_var].isel(time=i).values)
                if not np.isnan(value):
                    record[db_col] = value
        
        # Insertion
        columns = ', '.join(record.keys())
        placeholders = ', '.join(['%s'] * len(record))
        values = tuple(record.values())
        
        query = f"""
            INSERT INTO barag.sensor_data ({columns})
            VALUES ({placeholders})
            ON CONFLICT (time, station_id) DO NOTHING
        """
        
        cursor.execute(query, values)
        total_inserted += 1
        
        # Commit par batch de 1000
        if total_inserted % 1000 == 0:
            conn.commit()
            print(f"  ✓ {total_inserted} lignes insérées...")
    
    # Commit final
    conn.commit()
    cursor.close()
    conn.close()
    ds.close()
    
    print(f"✅ Total: {total_inserted} lignes insérées")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ingest_coast_hf.py fichier.nc [station_id]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    station_id = sys.argv[2] if len(sys.argv) > 2 else 'BARAG'
    
    ingest_coast_hf_netcdf(filepath, station_id)
```

---

## 🔧 DÉPANNAGE

### Problème 1: Variables Manquantes

**Symptôme:**
```
KeyError: 'TEMP' not found in dataset
```

**Solution:**
```python
# Vérifier les noms de variables
import xarray as xr
ds = xr.open_dataset('fichier.nc')
print(list(ds.data_vars))

# Adapter le mapping dans ingestion_stream.py
# Ligne ~150, modifier le dictionnaire de mapping
```

### Problème 2: Erreur de Mémoire

**Symptôme:**
```
MemoryError: Consommation mémoire excessive: 280 Mo
```

**Solution:**
```bash
# Réduire la taille des chunks
python scripts/ingestion_stream.py fichier.nc \
    --chunk-size-netcdf 500  # Au lieu de 1000
    --memory-limit 200       # Limite plus stricte
```

### Problème 3: Fichier Corrompu

**Symptôme:**
```
OSError: [Errno -51] NetCDF: Unknown file format
```

**Solution:**
```bash
# Vérifier l'intégrité
ncdump -h fichier.nc

# Réparer avec NCO (NetCDF Operators)
sudo apt install nco
ncks -O fichier.nc fichier_repare.nc
```

### Problème 4: Timezone Incorrecte

**Symptôme:**
Les timestamps sont décalés de plusieurs heures.

**Solution:**
```python
# Les données COAST-HF sont en UTC
# Vérifier l'attribut 'units' de la variable TIME
ds = xr.open_dataset('fichier.nc')
print(ds.time.attrs['units'])
# Devrait être: "seconds since 1970-01-01 00:00:00 UTC"

# Si nécessaire, forcer UTC dans ingestion_stream.py
time_dt = pd.Timestamp(time_val, tz='UTC').to_pydatetime()
```

---

## 📚 Ressources Complémentaires

### Documentation Officielle

- **COAST-HF:** https://www.coast-hf.fr/
- **NetCDF CF Conventions:** http://cfconventions.org/
- **xarray:** https://docs.xarray.dev/
- **SEANOE:** https://www.seanoe.org/

### Outils Recommandés

```bash
# Installation complète des outils NetCDF
sudo apt install -y \
    netcdf-bin \      # ncdump, ncgen
    nco \             # NCO (NetCDF Operators)
    cdo \             # CDO (Climate Data Operators)
    python3-netcdf4   # Bindings Python
```

### Commandes Utiles

```bash
# Convertir NetCDF en CSV
ncdump -v TEMP,PSAL,PH_TOTAL fichier.nc > data.csv

# Extraire une période spécifique
ncks -d time,0,1000 fichier.nc periode.nc

# Fusionner plusieurs fichiers
ncrcat fichier_01.nc fichier_02.nc fichier_03.nc -o annee_complete.nc

# Compresser un fichier NetCDF
ncks -4 -L 9 fichier.nc fichier_compresse.nc
```

---

## ✅ Checklist d'Ingestion

Avant d'ingérer un fichier NetCDF COAST-HF:

- [ ] Fichier téléchargé et vérifié (taille > 0)
- [ ] Inspection avec `ncdump -h` ou `xarray`
- [ ] Variables principales présentes (TEMP, PSAL, TIME)
- [ ] Plage temporelle cohérente
- [ ] Attribut `station_id` identifié
- [ ] Espace disque suffisant sur le VPS
- [ ] TimescaleDB accessible et opérationnel
- [ ] Backup récent de la base de données
- [ ] Logs d'ingestion activés

---

**🌊 Vous êtes maintenant prêt à ingérer des données NetCDF COAST-HF dans Ocean Sentinel V3.0 !**

Pour toute question, consultez la documentation COAST-HF ou contactez l'équipe technique ILICO.
