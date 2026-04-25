# 🚀 ROADMAP INTÉGRATION API RÉELLES

## 📊 ÉTAT ACTUEL

| Source | Status | Données | Priorité |
|--------|--------|---------|----------|
| **Backend Ocean Sentinel** | ⏳ À connecter | TEMP, PSAL, DOX2, pH | 🔴 CRITIQUE |
| **NOAA WaveWatch 3** | ⏳ À connecter | Houle, Vent marin | 🟡 HAUTE |
| **Météo-France** | ⏳ À connecter | Temp air, Humidité, Pression | 🟡 HAUTE |
| **COAST-HF Ifremer** | ⏳ À connecter | Données in-situ BARAG | 🟢 MOYENNE |
| **Hub'Eau** | ⏳ À connecter | Qualité eau EYRAC | 🟢 MOYENNE |
| **Copernicus CMEMS** | ⏳ À connecter | Données satellitaires | 🔵 BASSE |

---

## 🎯 ÉTAPE 1 : BACKEND OCEAN SENTINEL (PRIORITÉ CRITIQUE)

### **Objectif**
Connecter le frontend React au backend FastAPI existant pour récupérer les données océanographiques réelles.

### **Actions**

#### 1.1 Vérifier l'API Backend
```bash
# SSH vers le VPS
ssh root@76.13.43.3

# Vérifier que l'API tourne
curl http://localhost:8000/api/v1/health

# Tester un endpoint
curl http://localhost:8000/api/v1/station/BARAG_PROXY/latest
```

#### 1.2 Configurer le Proxy Nginx
```nginx
# /etc/nginx/sites-available/oceansentinelle

# Ajouter dans le bloc server {}
location /api/ {
    proxy_pass http://localhost:8000/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_cache_bypass $http_upgrade;
    
    # CORS headers
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
}
```

#### 1.3 Modifier `src/lib/api.ts`
```typescript
// Remplacer les données mockées par de vraies requêtes
export async function fetchStationData(stationId: string): Promise<StationData> {
  const response = await fetch(`/api/v1/station/${stationId}/latest`)
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  
  return await response.json()
}
```

#### 1.4 Tester
```bash
# Rebuild et redéployer
npm run build
scp -r dist/* root@76.13.43.3:/var/www/oceansentinelle/

# Tester dans le navigateur
# https://oceansentinelle.fr/dashboard
```

### **Critères de Succès**
- ✅ Les vraies données BARAG et EYRAC s'affichent
- ✅ Les alertes critiques se déclenchent automatiquement
- ✅ Les badges de vérité (●/◐/○) sont corrects
- ✅ Pas d'erreur CORS

---

## 🌊 ÉTAPE 2 : NOAA WAVEWATCH 3 (HOULE ET VENT)

### **Objectif**
Récupérer les données de houle et vent marin depuis NOAA pour le widget météo.

### **API Disponibles**

#### Option A : NOAA NOMADS (Recommandé)
```bash
# Endpoint GRIB2
https://nomads.ncep.noaa.gov/cgi-bin/filter_wave_multi.pl

# Paramètres
?file=multi_1.glo_30m.t00z.f000.grib2
&lev_surface=on
&var_HTSGW=on  # Hauteur vagues
&var_PERPW=on  # Période
&var_DIRPW=on  # Direction
&subregion=
&leftlon=-2
&rightlon=-1
&toplat=45
&bottomlat=44
```

#### Option B : NOAA CO-OPS (Stations côtières)
```bash
# Station la plus proche : Arcachon (si disponible)
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter

# Paramètres
?station=STATION_ID
&product=predictions
&datum=MLLW
&time_zone=gmt
&units=metric
&format=json
```

### **Actions**

#### 2.1 Créer un Proxy Backend
```python
# backend/app/routers/meteo.py

from fastapi import APIRouter
import httpx

router = APIRouter(prefix="/meteo", tags=["meteo"])

@router.get("/marine")
async def get_meteo_marine():
    async with httpx.AsyncClient() as client:
        # Requête NOAA
        response = await client.get(
            "https://nomads.ncep.noaa.gov/...",
            params={...}
        )
        
        # Parser GRIB2 ou JSON
        data = parse_noaa_response(response.content)
        
        return {
            "wave_height": data.HTSGW,
            "wave_period": data.PERPW,
            "wind_speed": data.WIND,
            ...
        }
```

#### 2.2 Modifier le Frontend
```typescript
// src/lib/meteo-service.ts

export async function fetchMeteoMarine(): Promise<MeteoMarineData> {
  const response = await fetch('/api/v1/meteo/marine')
  return await response.json()
}
```

### **Critères de Succès**
- ✅ Houle et vent affichés en temps réel
- ✅ Mise à jour toutes les 6 heures (cycle NOAA)
- ✅ Fallback sur données mockées si erreur

---

## 🌡️ ÉTAPE 3 : MÉTÉO-FRANCE (ATMOSPHÈRE)

### **Objectif**
Récupérer température air, humidité, pression depuis Météo-France.

### **API Météo-France**

#### Inscription
1. Créer un compte sur https://portail-api.meteofrance.fr/
2. Souscrire à l'offre "Données Publiques Observations"
3. Récupérer la clé API

#### Endpoint
```bash
# Observations infrahoraires (6 minutes)
GET https://public-api.meteofrance.fr/public/DPObs/v1/station/infrahoraire-6m

# Headers
apikey: VOTRE_CLE_API

# Paramètres
?id-station=33122001  # Cap Ferret
```

### **Actions**

#### 3.1 Stocker la Clé API
```bash
# Sur le VPS
echo "METEO_FRANCE_API_KEY=votre_cle_ici" >> /opt/oceansentinel/backend/.env

# Recharger le backend
systemctl restart oceansentinel-api
```

#### 3.2 Créer l'Endpoint Backend
```python
# backend/app/routers/meteo.py

@router.get("/atmosphere")
async def get_meteo_atmosphere():
    api_key = os.getenv("METEO_FRANCE_API_KEY")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://public-api.meteofrance.fr/public/DPObs/v1/station/infrahoraire-6m",
            headers={"apikey": api_key},
            params={"id-station": "33122001"}
        )
        
        data = response.json()[0]  # Dernière observation
        
        return {
            "air_temp": data.t,
            "humidity": data.u,
            "pressure": data.pres,
            "wind_speed": data.ff * 3.6,  # m/s → km/h
            ...
        }
```

### **Critères de Succès**
- ✅ Température, humidité, pression affichées
- ✅ Mise à jour toutes les 6 minutes
- ✅ Gestion des erreurs API

---

## 🛰️ ÉTAPE 4 : COAST-HF IFREMER (DONNÉES IN-SITU)

### **Objectif**
Récupérer les données haute fréquence de la station BARAG.

### **API COAST-HF**

```bash
# Endpoint (à vérifier avec Ifremer)
https://www.coast-hf.fr/data/barag/latest

# Format : JSON ou NetCDF
```

### **Actions**

#### 4.1 Contacter Ifremer
- Email : coast-hf@ifremer.fr
- Demander accès API BARAG
- Récupérer documentation

#### 4.2 Intégrer au Backend
```python
@router.get("/station/barag/coasthf")
async def get_coasthf_barag():
    # Requête COAST-HF
    response = await client.get("https://www.coast-hf.fr/data/barag/latest")
    
    # Transformer en format SACS
    return transform_coasthf_to_sacs(response.json())
```

---

## 🌍 ÉTAPE 5 : HUB'EAU (QUALITÉ DES EAUX)

### **Objectif**
Récupérer les données de qualité de l'eau pour EYRAC.

### **API Hub'Eau**

```bash
# Endpoint public (pas de clé requise)
GET https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis

# Paramètres
?code_commune=33009  # Arcachon
&size=1000
&sort=desc
```

### **Actions**

```python
@router.get("/station/eyrac/hubeau")
async def get_hubeau_eyrac():
    response = await client.get(
        "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis",
        params={"code_commune": "33009", "size": 100}
    )
    
    return transform_hubeau_to_sacs(response.json())
```

---

## 📅 PLANNING RECOMMANDÉ

| Semaine | Tâche | Livrable |
|---------|-------|----------|
| **S1** | Backend Ocean Sentinel | Dashboard avec vraies données |
| **S2** | NOAA WaveWatch 3 | Widget météo houle/vent |
| **S3** | Météo-France | Widget météo complet |
| **S4** | COAST-HF + Hub'Eau | Sources multiples validées |
| **S5** | Tests & Optimisation | Performance + Cache |
| **S6** | Documentation | Guide API complet |

---

## 🔒 SÉCURITÉ & BONNES PRATIQUES

### Variables d'Environnement
```bash
# /opt/oceansentinel/backend/.env
METEO_FRANCE_API_KEY=xxx
COPERNICUS_USERNAME=xxx
COPERNICUS_PASSWORD=xxx
NOAA_API_KEY=  # Pas nécessaire (public)
```

### Rate Limiting
```python
# backend/app/middleware/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/meteo/marine")
@limiter.limit("10/minute")  # Max 10 requêtes/min
async def get_meteo_marine():
    ...
```

### Cache Redis
```python
# backend/app/cache.py

import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_get(key: str):
    data = redis_client.get(key)
    return json.loads(data) if data else None

def cache_set(key: str, value: dict, ttl: int = 300):
    redis_client.setex(key, ttl, json.dumps(value))
```

---

## 📊 MÉTRIQUES DE SUCCÈS

| Métrique | Objectif | Actuel |
|----------|----------|--------|
| **Latence API** | < 500ms | ⏳ |
| **Disponibilité** | > 99.5% | ⏳ |
| **Fraîcheur données** | < 5 min | ⏳ |
| **Taux d'erreur** | < 1% | ⏳ |
| **Cache hit rate** | > 80% | ⏳ |

---

## 🆘 SUPPORT & CONTACTS

| Service | Contact | Documentation |
|---------|---------|---------------|
| **NOAA** | https://www.ncei.noaa.gov/support | https://polar.ncep.noaa.gov/waves/ |
| **Météo-France** | portail-api@meteo.fr | https://portail-api.meteofrance.fr/web/ |
| **Ifremer COAST-HF** | coast-hf@ifremer.fr | https://www.coast-hf.fr/ |
| **Hub'Eau** | contact@hubeau.fr | https://hubeau.eaufrance.fr/ |
| **Copernicus** | servicedesk.cmems@mercator-ocean.eu | https://marine.copernicus.eu/ |

---

**Prochaine action recommandée** : Commencer par l'Étape 1 (Backend Ocean Sentinel) car c'est la source de données la plus critique et déjà disponible sur le VPS.
