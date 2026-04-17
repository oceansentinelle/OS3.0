# 🌊 Ocean Sentinel V3.0 - Architecture Multi-Agents

**Système de Surveillance Écologique du Bassin d'Arcachon**  
**Infrastructure de Recherche ILICO - Réseau COAST-HF**

---

## 📋 Vue d'Ensemble

Ocean Sentinel V3.0 est un **système multi-agents (MAS)** de surveillance océanographique en temps réel, conçu pour le monitoring du Bassin d'Arcachon et l'intégration au réseau national COAST-HF.

### Caractéristiques Principales

- ✅ **Ingestion streaming** optimisée (max 256 Mo RAM)
- ✅ **Machine Learning** (LSTM + Isolation Forest)
- ✅ **Formules UNESCO** (PSS-78, Garcia & Gordon)
- ✅ **Alertes automatiques** (hypoxie, acidification)
- ✅ **Conformité SACS** (Superviseur Autonome de Conformité Scientifique)
- ✅ **Infrastructure Docker** complète

---

## 🏗️ Architecture

### Services Docker

```
┌─────────────────────────────────────────────────────────────┐
│                    Ocean Sentinel V3.0                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ TimescaleDB  │  │  Ingestion   │  │  ML Pipeline │    │
│  │  (Postgres)  │◄─┤  (Streaming) │  │  (LSTM+IF)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         ▲                                     │            │
│         │                                     │            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   API REST   │  │  Prometheus  │  │   Grafana    │    │
│  │   (FastAPI)  │  │ (Monitoring) │  │ (Dashboard)  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         ▲                                                  │
│         │                                                  │
│  ┌──────────────┐                                         │
│  │    NGINX     │                                         │
│  │ (Rev. Proxy) │                                         │
│  └──────────────┘                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Agents Spécialisés

1. **Agent Data Engineer** (`scripts/ingestion_stream.py`)
   - Ingestion NetCDF, GRIB2, CSV
   - Lecture par morceaux (chunked)
   - Limite stricte: 256 Mo RAM

2. **Agent IA & Scientifique** (`scripts/ml_pipeline.py`)
   - Prédiction LSTM (séries temporelles)
   - Détection d'anomalies (Isolation Forest)
   - Formules UNESCO (PSS-78, Garcia & Gordon)

3. **Agent DevOps** (`scripts/harden_vps.sh`)
   - Durcissement VPS (UFW, Fail2Ban)
   - Configuration sécurisée
   - Monitoring système

4. **Agent SACS** (`.windsurf/skills/project-context.md`)
   - Règles de conformité
   - Traçabilité des données
   - Génération d'alertes

---

## 🚀 Déploiement

### Prérequis

- **VPS:** Ubuntu 22.04+ (8 Go RAM / 4 vCPU recommandé)
- **Docker:** 24.0+
- **Docker Compose:** 2.20+

### Installation Rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-org/oceansentinel-v3.git
cd oceansentinel-v3

# 2. Configuration
cp .env.example .env
nano .env  # Configurer POSTGRES_PASSWORD

# 3. Durcissement VPS (optionnel mais recommandé)
sudo bash scripts/harden_vps.sh

# 4. Lancement
docker compose -f docker-compose-v3.yml up -d

# 5. Vérification
docker compose ps
docker compose logs -f
```

### Configuration .env

```env
# Base de données
POSTGRES_USER=oceansentinel
POSTGRES_PASSWORD=VOTRE_MOT_DE_PASSE_FORT
POSTGRES_DB=oceansentinelle
POSTGRES_PORT=6543

# API
API_PORT=8000

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=VOTRE_MOT_DE_PASSE_GRAFANA

# Alertes
ALERT_PH_MIN=7.8
ALERT_O2_MIN=150
```

---

## 📊 Utilisation

### Ingestion de Données

```bash
# Ingérer un fichier NetCDF
docker exec oceansentinel_ingestion python /app/ingestion_stream.py \
    /data/BARAG_2026-04-16.nc --format netcdf

# Ingérer un CSV SEANOE
docker exec oceansentinel_ingestion python /app/ingestion_stream.py \
    /data/seanoe_data.csv --format csv --chunk-size-csv 5000

# Ingérer un GRIB2 (Météo-France)
docker exec oceansentinel_ingestion python /app/ingestion_stream.py \
    /data/meteo_france.grb2 --format grib2
```

### Pipeline ML

```bash
# Prédiction LSTM
docker exec oceansentinel_ml python /app/ml_pipeline.py \
    --mode predict --start-date 2026-03-16 --end-date 2026-04-16

# Détection d'anomalies
docker exec oceansentinel_ml python /app/ml_pipeline.py \
    --mode detect --start-date 2026-03-16 --end-date 2026-04-16

# Pipeline complet
docker exec oceansentinel_ml python /app/ml_pipeline.py \
    --mode full
```

### Requêtes SQL

```bash
# Dernières données
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
    "SELECT * FROM barag.sensor_data ORDER BY time DESC LIMIT 10;"

# Statistiques 24h
docker exec oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c \
    "SELECT AVG(temperature_water), AVG(ph), AVG(dissolved_oxygen) 
     FROM barag.sensor_data 
     WHERE time > NOW() - INTERVAL '24 hours';"
```

---

## 🔬 Formules Scientifiques

### Salinité Pratique (PSS-78)

Implémentation conforme à la norme UNESCO 1981:

```python
from scripts.ml_pipeline import OceanographicFormulas

formulas = OceanographicFormulas()

salinity = formulas.practical_salinity_pss78(
    conductivity_ratio=1.0023,
    temperature=18.5,
    pressure=0.5
)
# Résultat: 35.2 PSU
```

### Oxygène Dissous (Garcia & Gordon, 1992)

```python
o2_saturation = formulas.dissolved_oxygen_garcia_gordon(
    temperature=18.5,
    salinity=35.2,
    pressure=0.5
)
# Résultat: ~250 µmol/kg
```

---

## 🚨 Système d'Alertes

### Seuils Configurés

| Paramètre | Seuil Critique | Action |
|-----------|----------------|--------|
| pH | < 7.8 | Rapport immédiat |
| O₂ dissous | < 150 µmol/kg | Rapport immédiat (hypoxie) |
| Température | > 25°C | Surveillance renforcée |

### Exemple de Rapport d'Alerte

```markdown
# 🚨 ALERTE ÉCOLOGIQUE OCEAN SENTINEL

**Niveau:** CRITIQUE
**Date:** 2026-04-16 14:30:00 UTC
**Station:** BARAG
**Paramètre:** pH = 7.75 ± 0.01

## Analyse
- Tendance: Baisse continue (-0.15 pH/jour)
- Prédiction 6h: pH = 7.70 ± 0.05
- Anomalie détectée: OUI

## Actions Recommandées
1. Vérifier calibrage capteur
2. Analyser données météo
3. Prélèvement eau pour analyse labo
```

---

## 📐 Conformité SACS

### Règles Principales

- **SACS-001:** Métadonnées obligatoires pour toute donnée
- **SACS-002:** Interdiction des assertions non fondées
- **SACS-003:** Traçabilité des transformations
- **SACS-101:** Protocole d'alerte automatisé
- **SACS-201:** Acknowledgment ILICO obligatoire

### Exemple de Donnée Conforme

```json
{
  "value": 8.1,
  "unit": "pH",
  "time": "2026-04-16T14:30:00+00:00",
  "station_id": "BARAG",
  "source": "SeaBird SBE 37-SMP CTD",
  "uncertainty": 0.01,
  "status": "MEASURED",
  "quality_flag": 0,
  "data_source": "COAST-HF:BARAG:2026-04-16"
}
```

---

## 🔐 Sécurité

### Durcissement VPS

Le script `harden_vps.sh` configure:

- ✅ Pare-feu UFW (ports 22, 6543, 8000, 3000, 9090, 80, 443)
- ✅ Fail2Ban (protection SSH, PostgreSQL)
- ✅ SSH durci (clés uniquement, port personnalisé)
- ✅ Kernel durci (sysctl)
- ✅ Mises à jour automatiques

### Ports Exposés

| Service | Port | Description |
|---------|------|-------------|
| SSH | 22 | Accès serveur (à changer) |
| TimescaleDB | 6543 | Base de données |
| API | 8000 | API REST |
| Grafana | 3000 | Dashboards |
| Prometheus | 9090 | Monitoring |
| HTTP | 80 | Web (redirect HTTPS) |
| HTTPS | 443 | Web sécurisé |

---

## 📊 Monitoring

### Grafana Dashboards

Accès: `http://VOTRE_IP_VPS:3000`

Dashboards disponibles:
- **Ocean Sentinel Overview** - Vue d'ensemble
- **BARAG Station** - Données en temps réel
- **ML Pipeline** - Performances modèles
- **System Health** - Monitoring infrastructure

### Prometheus Metrics

Accès: `http://VOTRE_IP_VPS:9090`

Métriques collectées:
- Débit d'ingestion (lignes/s)
- Utilisation mémoire (services)
- Latence API (P50, P95, P99)
- Taux d'anomalies détectées

---

## 🧪 Tests

### Tests Unitaires

```bash
# Tests ingestion
pytest tests/test_ingestion_stream.py

# Tests ML pipeline
pytest tests/test_ml_pipeline.py

# Tests formules UNESCO
pytest tests/test_oceanographic_formulas.py
```

### Tests d'Intégration

```bash
# Test complet du pipeline
bash tests/integration/test_full_pipeline.sh
```

---

## 📚 Documentation

### Fichiers Principaux

- **`project-context.md`** - Constitution SACS (règles de gouvernance)
- **`DEPLOYMENT.md`** - Guide de déploiement détaillé
- **`API_REFERENCE.md`** - Documentation API REST
- **`ML_MODELS.md`** - Documentation modèles ML

### Références Scientifiques

1. **PSS-78:** UNESCO (1981). *Practical Salinity Scale 1978*. Technical Papers in Marine Science No. 37.

2. **Garcia & Gordon (1992):** *Oxygen solubility in seawater: Better fitting equations*. Limnology and Oceanography, 37(6), 1307-1312.

3. **COAST-HF:** https://www.coast-hf.fr/

4. **ILICO:** https://www.ir-ilico.fr/

---

## 🤝 Contribution

### Workflow

1. Fork le dépôt
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

### Standards de Code

- **Langage:** Python 3.11+
- **Style:** PEP 8
- **Docstrings:** Format Google
- **Tests:** pytest (couverture > 80%)
- **Commentaires:** En français

---

## 📄 Licence

### Code Source
MIT License - Copyright (c) 2026 Ocean Sentinel Team

### Données Océanographiques
CC-BY 4.0 - Infrastructure de Recherche ILICO / COAST-HF

### Modèles ML
CC-BY-NC 4.0 - Usage non commercial uniquement

---

## 🏛️ Acknowledgment

Ce projet est développé dans le cadre de l'**Infrastructure de Recherche ILICO** (Littoral et Côtier), financée par le Ministère de l'Enseignement Supérieur et de la Recherche, et opérée par le réseau **COAST-HF** (Coastal Ocean Observing System - High Frequency).

**Station:** BARAG - Bassin d'Arcachon

---

## 📞 Contact

**Responsable Scientifique:** [À compléter]  
**Responsable Technique:** [À compléter]  
**Email:** oceansentinel@ilico.fr  
**Website:** https://www.coast-hf.fr/

---

**Version:** 3.0.0  
**Date:** 2026-04-16  
**Statut:** Production Ready
