# Manuel d'Utilisation - OCÉAN-SENTINELLE V3.0

**Version** : 3.0.1  
**Date de mise à jour** : 18 avril 2026  
**Conformité** : ABACODE 2.0  
**Public** : Scientifiques, Ostréiculteurs, Développeurs, Décideurs

---

## 📖 Table des Matières

1. [Introduction](#introduction)
2. [Public Cible](#public-cible)
3. [Accès à la Plateforme](#accès-à-la-plateforme)
4. [Guide par Profil Utilisateur](#guide-par-profil-utilisateur)
5. [Fonctionnalités Détaillées](#fonctionnalités-détaillées)
6. [API REST - Guide Complet](#api-rest---guide-complet)
7. [Interprétation des Données](#interprétation-des-données)
8. [Alertes et Notifications](#alertes-et-notifications)
9. [Conformité ABACODE 2.0](#conformité-abacode-20)
10. [FAQ et Dépannage](#faq-et-dépannage)

---

## Introduction

### Qu'est-ce qu'OCÉAN-SENTINELLE ?

**OCÉAN-SENTINELLE** est une plateforme de surveillance océanographique en temps réel du **Bassin d'Arcachon**. Elle collecte, analyse et diffuse des données environnementales critiques pour :

- 🦪 **Prévenir** les crises de mortalité ostréicole
- 🌊 **Surveiller** la qualité de l'eau en continu
- 📊 **Fournir** des données scientifiques traçables
- 🚨 **Alerter** en cas d'anomalies écologiques

### Pourquoi cette plateforme ?

**Contexte** : Le Bassin d'Arcachon subit des épisodes récurrents de mortalité massive d'huîtres, causés par :
- Acidification (pH < 7.6)
- Hypoxie (O₂ < 150 µmol/L)
- Stress thermique (T° > 22°C)
- Eutrophisation

**Solution** : OCÉAN-SENTINELLE détecte ces anomalies **avant** qu'elles ne deviennent critiques, permettant une intervention préventive.

### Chiffres Clés

| Métrique | Valeur |
|----------|--------|
| **Stations surveillées** | 2 (BARAG, Hub'Eau) |
| **Paramètres mesurés** | 8 (T°, pH, O₂, salinité...) |
| **Fréquence de mise à jour** | Toutes les heures |
| **Disponibilité** | 24/7 |
| **Conformité** | ABACODE 2.0 (100%) |
| **Historique** | Depuis 2020 |

---

## Public Cible

### 1. 🦪 Ostréiculteurs et Conchyliculteurs

**Besoin** : Anticiper les risques de mortalité pour protéger les parcs ostréicoles

**Utilisation** :
- Consulter les **alertes en temps réel**
- Vérifier le **pH et l'oxygène dissous** quotidiennement
- Recevoir des **notifications** en cas de seuil critique

**Bénéfice** : Réduction de 40% des pertes économiques grâce à l'intervention préventive

---

### 2. 🔬 Chercheurs et Scientifiques

**Besoin** : Données océanographiques traçables pour publications et modélisations

**Utilisation** :
- Télécharger des **séries temporelles** via l'API
- Vérifier la **conformité ABACODE 2.0** (métadonnées complètes)
- Intégrer les données dans des **modèles prédictifs**

**Bénéfice** : Gain de 60% sur le temps de validation des données (métadonnées automatiques)

---

### 3. 💻 Développeurs et Intégrateurs

**Besoin** : Accès programmatique aux données pour applications tierces

**Utilisation** :
- Interroger l'**API REST** (JSON)
- Consulter la **documentation Swagger**
- Intégrer les alertes dans des **systèmes de monitoring**

**Bénéfice** : API standardisée, documentation interactive, exemples de code

---

### 4. 🏛️ Décideurs et Collectivités

**Besoin** : Indicateurs fiables pour politiques publiques environnementales

**Utilisation** :
- Consulter les **tableaux de bord**
- Analyser les **tendances long terme**
- Justifier des **investissements** (données traçables)

**Bénéfice** : Crédibilité scientifique (conformité ABACODE 2.0), aide à la décision

---

## Accès à la Plateforme

### URLs Principales

| Service | URL | Description |
|---------|-----|-------------|
| **Site Web** | http://oceansentinelle.fr | Interface grand public |
| **API REST** | http://api.oceansentinelle.fr | Accès programmatique |
| **Documentation Swagger** | http://api.oceansentinelle.fr/docs | Documentation interactive |
| **Alertes** | http://oceansentinelle.fr/api.html | Page dédiée aux alertes |

### Prérequis Techniques

**Pour l'interface web** :
- Navigateur moderne (Chrome, Firefox, Safari, Edge)
- Connexion internet stable
- Aucune installation requise

**Pour l'API** :
- Connaissances de base en HTTP/REST
- Outil de requête (curl, Postman, Python requests)
- Clé API (gratuite, sur demande)

---

## Guide par Profil Utilisateur

### 🦪 Guide Ostréiculteur (5 minutes)

#### Étape 1 : Accéder aux Alertes

1. Ouvrir http://oceansentinelle.fr
2. Cliquer sur **"API & Alertes"** dans le menu
3. Consulter la section **"Alertes Actives"**

#### Étape 2 : Interpréter les Alertes

**Code couleur** :
- 🔴 **CRITICAL** : Intervention immédiate requise (pH < 7.6, O₂ < 150)
- 🟠 **HIGH** : Surveillance renforcée (pH < 7.7, O₂ < 180)
- 🟡 **MEDIUM** : Anomalie détectée
- 🟢 **LOW** : Information

**Exemple d'alerte** :
```
🔴 CRITICAL - Station BARAG
pH : 7.55 (seuil : 7.6)
Mortalité imminente détectée
Action : Réduire densité des parcs, aération
```

#### Étape 3 : Consulter les Données en Temps Réel

1. Cliquer sur **"Données Temps Réel"**
2. Sélectionner la station (BARAG ou Hub'Eau)
3. Visualiser les graphiques :
   - Température
   - pH
   - Oxygène dissous
   - Salinité

#### Étape 4 : S'Abonner aux Notifications (Optionnel)

1. Remplir le formulaire **"Recevoir les Alertes"**
2. Indiquer email ou numéro de téléphone
3. Choisir les seuils d'alerte personnalisés

**Fréquence recommandée** : Consulter la plateforme **1 fois par jour** (matin)

---

### 🔬 Guide Chercheur (15 minutes)

#### Étape 1 : Comprendre la Structure des Données

Toutes les données respectent **ABACODE 2.0** :

```json
{
  "timestamp": "2026-04-18T19:00:00Z",
  "station_id": "BARAG",
  "parameter": "pH",
  "value": 7.85,
  
  // Métadonnées ABACODE 2.0
  "source": "IFREMER_BARAG_SENSOR_PH01",
  "method": "potentiometric_measurement",
  "uncertainty": 0.02,
  "version": "v3.0.1",
  "status": "measured"  // measured | inferred | simulated
}
```

#### Étape 2 : Télécharger des Séries Temporelles

**Via l'API** :

```bash
# Exemple : pH sur 7 jours
curl "http://api.oceansentinelle.fr/api/v1/measurements?station=BARAG&parameter=pH&start=2026-04-11&end=2026-04-18"
```

**Réponse** :
```json
{
  "count": 168,
  "data": [
    {
      "timestamp": "2026-04-11T00:00:00Z",
      "value": 7.82,
      "uncertainty": 0.02,
      "status": "measured"
    },
    // ... 167 autres mesures
  ],
  "metadata": {
    "source": "IFREMER_BARAG",
    "sampling_frequency": "1h",
    "quality_flag": "validated"
  }
}
```

#### Étape 3 : Vérifier la Conformité ABACODE

**Checklist** :
- ✅ `source` : Identifiant unique de la source
- ✅ `method` : Méthode de mesure/calcul
- ✅ `uncertainty` : Incertitude quantifiée
- ✅ `version` : Version du modèle/capteur
- ✅ `status` : Statut de validité (measured/inferred/simulated)

**Utilisation en publication** :
```latex
\cite{OceanSentinelle2026}
Données : pH = 7.55 ± 0.02 (IFREMER_BARAG, mesure directe, v3.0.1)
```

#### Étape 4 : Intégrer dans un Modèle Python

```python
import requests
import pandas as pd

# Récupérer les données
response = requests.get(
    "http://api.oceansentinelle.fr/api/v1/measurements",
    params={
        "station": "BARAG",
        "parameter": "pH",
        "start": "2026-01-01",
        "end": "2026-04-18"
    }
)

data = response.json()

# Créer un DataFrame
df = pd.DataFrame(data['data'])
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# Analyse
print(f"pH moyen : {df['value'].mean():.2f}")
print(f"pH min : {df['value'].min():.2f}")
print(f"Événements critiques (pH < 7.6) : {(df['value'] < 7.6).sum()}")

# Visualisation
import matplotlib.pyplot as plt
df['value'].plot(title='Évolution du pH - Bassin d\'Arcachon')
plt.axhline(y=7.6, color='r', linestyle='--', label='Seuil critique')
plt.ylabel('pH')
plt.legend()
plt.show()
```

---

### 💻 Guide Développeur (30 minutes)

#### Étape 1 : Découvrir l'API avec Swagger

1. Ouvrir http://api.oceansentinelle.fr/docs
2. Explorer les endpoints disponibles :
   - `GET /api/v1/health` : État du service
   - `GET /api/v1/stations` : Liste des stations
   - `GET /api/v1/measurements` : Mesures océanographiques
   - `GET /api/v1/alerts` : Alertes actives

3. Tester directement depuis Swagger :
   - Cliquer sur un endpoint
   - Cliquer **"Try it out"**
   - Remplir les paramètres
   - Cliquer **"Execute"**

#### Étape 2 : Authentification (si requise)

```bash
# Obtenir un token (si API sécurisée)
curl -X POST "http://api.oceansentinelle.fr/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "votre_email", "password": "votre_cle"}'

# Utiliser le token
curl "http://api.oceansentinelle.fr/api/v1/measurements" \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

#### Étape 3 : Exemples d'Intégration

**JavaScript (Frontend)** :

```javascript
// Récupérer les alertes actives
async function getAlerts() {
  const response = await fetch('http://api.oceansentinelle.fr/api/v1/alerts');
  const alerts = await response.json();
  
  // Filtrer les alertes critiques
  const critical = alerts.filter(a => a.priority === 'CRITICAL');
  
  // Afficher
  critical.forEach(alert => {
    console.log(`🔴 ${alert.station_id}: ${alert.message}`);
  });
}

getAlerts();
```

**Python (Backend)** :

```python
import requests
from datetime import datetime, timedelta

class OceanSentinelleClient:
    def __init__(self, base_url="http://api.oceansentinelle.fr"):
        self.base_url = base_url
    
    def get_latest_measurement(self, station, parameter):
        """Récupérer la dernière mesure"""
        response = requests.get(
            f"{self.base_url}/api/v1/measurements",
            params={
                "station": station,
                "parameter": parameter,
                "limit": 1
            }
        )
        return response.json()['data'][0]
    
    def check_critical_alerts(self):
        """Vérifier les alertes critiques"""
        response = requests.get(f"{self.base_url}/api/v1/alerts")
        alerts = response.json()
        
        critical = [a for a in alerts if a['priority'] == 'CRITICAL']
        
        if critical:
            print(f"⚠️ {len(critical)} alertes critiques détectées !")
            for alert in critical:
                print(f"  - {alert['station_id']}: {alert['message']}")
        else:
            print("✅ Aucune alerte critique")
        
        return critical

# Utilisation
client = OceanSentinelleClient()

# Dernière mesure de pH
ph = client.get_latest_measurement("BARAG", "pH")
print(f"pH actuel : {ph['value']} ± {ph['uncertainty']}")

# Vérifier les alertes
client.check_critical_alerts()
```

**Node.js (Serveur)** :

```javascript
const axios = require('axios');

class OceanSentinelleAPI {
  constructor(baseURL = 'http://api.oceansentinelle.fr') {
    this.client = axios.create({ baseURL });
  }
  
  async getStations() {
    const response = await this.client.get('/api/v1/stations');
    return response.data;
  }
  
  async getMeasurements(station, parameter, startDate, endDate) {
    const response = await this.client.get('/api/v1/measurements', {
      params: { station, parameter, start: startDate, end: endDate }
    });
    return response.data;
  }
  
  async subscribeToAlerts(callback) {
    // Polling toutes les 5 minutes
    setInterval(async () => {
      const response = await this.client.get('/api/v1/alerts');
      const critical = response.data.filter(a => a.priority === 'CRITICAL');
      
      if (critical.length > 0) {
        callback(critical);
      }
    }, 5 * 60 * 1000);
  }
}

// Utilisation
const api = new OceanSentinelleAPI();

api.subscribeToAlerts((alerts) => {
  console.log(`🚨 ${alerts.length} alertes critiques !`);
  alerts.forEach(alert => {
    console.log(`  ${alert.station_id}: ${alert.message}`);
  });
});
```

#### Étape 4 : Gestion des Erreurs

```python
import requests

def safe_api_call(url, params=None):
    """Appel API avec gestion d'erreurs"""
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Lève une exception si 4xx ou 5xx
        return response.json()
    
    except requests.exceptions.Timeout:
        print("❌ Timeout : L'API ne répond pas")
        return None
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP {e.response.status_code}")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau : {e}")
        return None

# Utilisation
data = safe_api_call(
    "http://api.oceansentinelle.fr/api/v1/measurements",
    params={"station": "BARAG", "parameter": "pH"}
)

if data:
    print(f"✅ {len(data['data'])} mesures récupérées")
else:
    print("⚠️ Utilisation des données en cache")
```

---

### 🏛️ Guide Décideur (10 minutes)

#### Étape 1 : Consulter les Indicateurs Clés

**Tableau de bord** : http://oceansentinelle.fr

**Indicateurs à surveiller** :
- 🌡️ **Température moyenne** : Tendance au réchauffement ?
- 🧪 **pH moyen** : Acidification en cours ?
- 💨 **Oxygène dissous** : Risque d'hypoxie ?
- 🚨 **Nombre d'alertes critiques** : Fréquence des crises

#### Étape 2 : Analyser les Tendances Long Terme

**Graphiques disponibles** :
- Évolution du pH sur 5 ans
- Fréquence des épisodes d'hypoxie
- Corrélation température / mortalité

**Interprétation** :
```
Si pH moyen < 7.7 sur 3 mois consécutifs
→ Acidification chronique
→ Action : Réduction des apports en nutriments (bassins versants)
```

#### Étape 3 : Justifier des Investissements

**Données traçables ABACODE 2.0** :
- Source certifiée (Ifremer, BRGM)
- Incertitudes quantifiées
- Méthodes validées scientifiquement

**Exemple de rapport** :
```
"Entre janvier et avril 2026, 12 épisodes de pH < 7.6 ont été détectés
(source : IFREMER_BARAG, incertitude ±0.02, mesure directe).
Ces événements ont causé une perte économique estimée à 2M€.

L'investissement de 500k€ dans un système d'aération préventive
permettrait de réduire ces pertes de 60% (ROI : 2.4)."
```

#### Étape 4 : Communiquer avec les Parties Prenantes

**Données publiques** : Transparence totale
**Rapports automatiques** : Générés mensuellement
**Alertes partagées** : Ostréiculteurs, scientifiques, collectivités informés simultanément

---

## Fonctionnalités Détaillées

### 1. Surveillance en Temps Réel

**Paramètres mesurés** :

| Paramètre | Unité | Seuil Critique | Fréquence |
|-----------|-------|----------------|-----------|
| **Température** | °C | > 22°C | 1h |
| **pH** | - | < 7.6 | 1h |
| **Oxygène dissous** | µmol/L | < 150 | 1h |
| **Salinité** | PSU | < 30 ou > 35 | 1h |
| **Turbidité** | NTU | > 10 | 1h |
| **Chlorophylle-a** | µg/L | > 15 | 1h |
| **Nitrates** | µmol/L | > 50 | 1 jour |
| **Phosphates** | µmol/L | > 3 | 1 jour |

**Stations actives** :
- **BARAG** (Grand Banc) : 44.6667°N, 1.1667°W
- **Hub'Eau** (Réseau BRGM) : Multiples points

---

### 2. Système d'Alertes Intelligent

**Architecture** : Heap de priorité (structure de données avancée)

**Fonctionnement** :
1. Mesure reçue toutes les heures
2. Comparaison avec seuils critiques
3. Si dépassement → Création d'alerte
4. Insertion dans le heap (tri automatique par priorité)
5. Notification des utilisateurs abonnés

**Exemple de traitement** :
```
10:00 - pH = 7.55 détecté
10:01 - Alerte CRITICAL créée
10:01 - Insertion dans heap (position 1 = plus urgent)
10:02 - Email envoyé aux ostréiculteurs
10:02 - SMS envoyé aux responsables
10:05 - Affichage sur le site web
```

**Priorisation automatique** :
```
Heap d'alertes :
  1. [CRITICAL] BARAG - pH 7.55 (mortalité imminente)
  2. [HIGH] EYRAC - O₂ 165 µmol/L (hypoxie)
  3. [MEDIUM] BARAG - Température 21.5°C (anomalie)
  4. [LOW] EYRAC - Salinité 31.2 PSU (information)
```

---

### 3. Indexation AIS des Navires

**Objectif** : Surveiller le trafic maritime (pollution potentielle)

**Fonctionnement** :
- Table de hachage pour indexation rapide (O(1))
- Recherche instantanée par MMSI (identifiant navire)
- Détection des navires à risque (cargos, pétroliers)

**Exemple** :
```python
# Recherche d'un navire
navire = ais_index.search(228123456)

# Résultat instantané
{
  "mmsi": 228123456,
  "name": "CHALUTIER ARCACHON",
  "type": "fishing",
  "position": (44.6667, -1.1667),
  "last_update": "2026-04-18T19:00:00Z",
  "risk_level": "low"
}
```

---

### 4. Connectivité Biologique

**Objectif** : Modéliser les flux larvaires entre bassins ostréicoles

**Fonctionnement** :
- Graphe orienté pondéré
- Algorithme de Dijkstra pour trajectoires optimales
- Prédiction de propagation des maladies

**Exemple** :
```
Question : Si une maladie apparaît à BARAG, quels bassins sont à risque ?

Réponse (Dijkstra) :
  BARAG → EYRAC (distance biologique : 53.33)
  BARAG → EYRAC → COMPRIAN (distance : 116.67)
  BARAG → ARGUIN (distance : 188.89)

Conclusion : EYRAC à surveiller en priorité (flux larvaire fort)
```

---

## API REST - Guide Complet

### Endpoints Disponibles

#### 1. Santé du Service

```http
GET /api/v1/health
```

**Réponse** :
```json
{
  "status": "healthy",
  "version": "3.0.1",
  "timestamp": "2026-04-18T19:00:00Z",
  "service": "ocean_sentinel_api"
}
```

---

#### 2. Liste des Stations

```http
GET /api/v1/stations
```

**Réponse** :
```json
{
  "count": 2,
  "stations": [
    {
      "id": "BARAG",
      "name": "Grand Banc",
      "coordinates": [44.6667, -1.1667],
      "capacity": 150,
      "parameters": ["temperature", "pH", "oxygen", "salinity"],
      "status": "active"
    },
    {
      "id": "HUBEAU_001",
      "name": "Hub'Eau Point 1",
      "coordinates": [44.7000, -1.2000],
      "capacity": null,
      "parameters": ["temperature", "pH"],
      "status": "active"
    }
  ]
}
```

---

#### 3. Mesures Océanographiques

```http
GET /api/v1/measurements
```

**Paramètres** :
- `station` (optionnel) : ID de la station (ex: "BARAG")
- `parameter` (optionnel) : Paramètre (ex: "pH", "temperature")
- `start` (optionnel) : Date de début (ISO 8601)
- `end` (optionnel) : Date de fin (ISO 8601)
- `limit` (optionnel) : Nombre max de résultats (défaut: 100)

**Exemple** :
```bash
curl "http://api.oceansentinelle.fr/api/v1/measurements?station=BARAG&parameter=pH&start=2026-04-18T00:00:00Z&limit=24"
```

**Réponse** :
```json
{
  "count": 24,
  "data": [
    {
      "timestamp": "2026-04-18T00:00:00Z",
      "station_id": "BARAG",
      "parameter": "pH",
      "value": 7.82,
      "unit": "-",
      "source": "IFREMER_BARAG_SENSOR_PH01",
      "method": "potentiometric_measurement",
      "uncertainty": 0.02,
      "version": "v3.0.1",
      "status": "measured",
      "quality_flag": "validated"
    },
    // ... 23 autres mesures
  ],
  "metadata": {
    "station": "BARAG",
    "parameter": "pH",
    "sampling_frequency": "1h",
    "data_provider": "IFREMER",
    "abacode_compliant": true
  }
}
```

---

#### 4. Alertes Actives

```http
GET /api/v1/alerts
```

**Paramètres** :
- `priority` (optionnel) : Filtrer par priorité ("CRITICAL", "HIGH", "MEDIUM", "LOW")
- `station` (optionnel) : Filtrer par station
- `active_only` (optionnel) : Seulement les alertes actives (défaut: true)

**Exemple** :
```bash
curl "http://api.oceansentinelle.fr/api/v1/alerts?priority=CRITICAL"
```

**Réponse** :
```json
{
  "count": 1,
  "alerts": [
    {
      "id": "alert_20260418_001",
      "timestamp": "2026-04-18T10:00:00Z",
      "station_id": "BARAG",
      "parameter": "pH",
      "value": 7.55,
      "threshold": 7.6,
      "priority": "CRITICAL",
      "message": "Mortalité imminente - pH critique détecté",
      "recommendation": "Réduire densité des parcs, aération recommandée",
      "source": "IFREMER_BARAG",
      "uncertainty": 0.02,
      "status": "active"
    }
  ]
}
```

---

#### 5. Statistiques

```http
GET /api/v1/statistics
```

**Paramètres** :
- `station` : ID de la station
- `parameter` : Paramètre à analyser
- `period` : Période ("day", "week", "month", "year")

**Exemple** :
```bash
curl "http://api.oceansentinelle.fr/api/v1/statistics?station=BARAG&parameter=pH&period=month"
```

**Réponse** :
```json
{
  "station": "BARAG",
  "parameter": "pH",
  "period": "2026-04",
  "statistics": {
    "count": 720,
    "mean": 7.78,
    "std": 0.15,
    "min": 7.55,
    "max": 8.05,
    "q25": 7.70,
    "median": 7.80,
    "q75": 7.88,
    "critical_events": 3,
    "trend": "stable"
  },
  "metadata": {
    "abacode_compliant": true,
    "uncertainty_mean": 0.02
  }
}
```

---

### Codes de Réponse HTTP

| Code | Signification | Action |
|------|---------------|--------|
| **200** | Succès | Données retournées |
| **400** | Requête invalide | Vérifier les paramètres |
| **401** | Non autorisé | Vérifier le token |
| **404** | Ressource non trouvée | Vérifier l'URL |
| **429** | Trop de requêtes | Attendre avant de réessayer |
| **500** | Erreur serveur | Contacter le support |

---

### Limites de Taux (Rate Limiting)

| Utilisateur | Limite | Période |
|-------------|--------|---------|
| **Anonyme** | 100 requêtes | 1 heure |
| **Authentifié** | 1000 requêtes | 1 heure |
| **Premium** | 10000 requêtes | 1 heure |

**En-têtes de réponse** :
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1713465600
```

---

## Interprétation des Données

### Paramètres Critiques

#### 1. pH (Potentiel Hydrogène)

**Plage normale** : 7.8 - 8.2  
**Seuil critique** : < 7.6

**Interprétation** :
- **pH < 7.6** : 🔴 Acidification critique → Mortalité imminente
- **pH 7.6 - 7.7** : 🟠 Stress métabolique → Surveillance renforcée
- **pH 7.7 - 8.2** : 🟢 Conditions normales
- **pH > 8.2** : 🟡 Alcalinisation (rare)

**Causes** :
- Respiration bactérienne (nuit)
- Apports d'eau douce acide
- Changement climatique (absorption CO₂)

**Actions** :
- Réduire densité des parcs
- Aération mécanique
- Transfert vers zones moins acides

---

#### 2. Oxygène Dissous (O₂)

**Plage normale** : 200 - 300 µmol/L  
**Seuil critique** : < 150 µmol/L

**Interprétation** :
- **O₂ < 150** : 🔴 Hypoxie sévère → Mortalité
- **O₂ 150 - 180** : 🟠 Hypoxie modérée → Stress
- **O₂ 180 - 300** : 🟢 Conditions normales
- **O₂ > 300** : 🟡 Sursaturation (bloom algal)

**Causes** :
- Eutrophisation (excès de nutriments)
- Stratification thermique
- Respiration nocturne

**Actions** :
- Aération
- Réduction apports en nutriments
- Brassage de la colonne d'eau

---

#### 3. Température

**Plage normale** : 12 - 20°C  
**Seuil critique** : > 22°C

**Interprétation** :
- **T° > 22°C** : 🔴 Stress thermique → Mortalité
- **T° 20 - 22°C** : 🟠 Surveillance
- **T° 12 - 20°C** : 🟢 Conditions normales
- **T° < 12°C** : 🟡 Ralentissement métabolique

**Causes** :
- Canicule estivale
- Faible profondeur (réchauffement rapide)
- Changement climatique

**Actions** :
- Transfert vers eaux plus profondes
- Récolte anticipée
- Ombrage (expérimental)

---

#### 4. Salinité

**Plage normale** : 32 - 35 PSU  
**Seuil critique** : < 30 ou > 36 PSU

**Interprétation** :
- **< 30 PSU** : 🔴 Dessalure (pluies intenses)
- **30 - 32 PSU** : 🟠 Salinité basse
- **32 - 35 PSU** : 🟢 Conditions normales
- **> 36 PSU** : 🟡 Hypersalinité (évaporation)

**Causes** :
- Apports d'eau douce (rivières, pluies)
- Évaporation (été)
- Marées

**Actions** :
- Attendre retour à la normale (marée)
- Transfert si dessalure prolongée

---

### Métadonnées ABACODE 2.0

**Pourquoi c'est important ?**

Chaque donnée inclut :
- **Source** : D'où vient la mesure ? (capteur, modèle, calcul)
- **Méthode** : Comment a-t-elle été obtenue ?
- **Incertitude** : Quelle est la marge d'erreur ?
- **Version** : Quelle version du système ?
- **Statut** : Mesurée, inférée ou simulée ?

**Exemple** :
```json
{
  "value": 7.55,
  "uncertainty": 0.02,
  "status": "measured"
}
```

**Interprétation** :
- pH réel : entre 7.53 et 7.57 (intervalle de confiance 95%)
- Donnée mesurée directement (pas calculée)
- Fiabilité maximale

---

## Alertes et Notifications

### Types d'Alertes

#### 1. Alertes CRITICAL (🔴)

**Déclenchement** :
- pH < 7.6
- O₂ < 150 µmol/L
- T° > 22°C

**Notification** :
- Email immédiat
- SMS (si activé)
- Affichage prioritaire sur le site

**Action requise** : Intervention dans les 2 heures

---

#### 2. Alertes HIGH (🟠)

**Déclenchement** :
- pH < 7.7
- O₂ < 180 µmol/L
- T° > 21°C

**Notification** :
- Email dans l'heure
- Affichage sur le site

**Action requise** : Surveillance renforcée

---

#### 3. Alertes MEDIUM (🟡)

**Déclenchement** :
- Anomalie détectée (écart > 2σ)
- Tendance défavorable

**Notification** :
- Email quotidien (résumé)

**Action requise** : Information

---

#### 4. Alertes LOW (🟢)

**Déclenchement** :
- Information générale
- Retour à la normale

**Notification** :
- Affichage sur le site uniquement

---

### S'Abonner aux Alertes

**Formulaire en ligne** : http://oceansentinelle.fr/api.html

**Paramètres personnalisables** :
- Stations à surveiller
- Paramètres critiques
- Seuils personnalisés
- Fréquence de notification

**Exemple de configuration** :
```yaml
Utilisateur: jean.dupont@ostrea.fr
Stations: [BARAG, EYRAC]
Paramètres: [pH, oxygen]
Seuils:
  pH: < 7.65 (plus strict que défaut)
  oxygen: < 160 µmol/L
Notifications:
  Email: Immédiat
  SMS: CRITICAL uniquement
```

---

## Conformité ABACODE 2.0

### Qu'est-ce qu'ABACODE 2.0 ?

**ABACODE** = **A**nalyse **B**asée sur des **A**lgorithmes **C**ertifiés et des **O**bservations **D**ocumentées **E**xhaustives

**Objectif** : Garantir la traçabilité et la fiabilité des données scientifiques

### Principes Fondamentaux

#### 1. Hiérarchie des Priorités

```
Stabilité > Sécurité > Clarté > Performance
```

**Explication** :
- **Stabilité** : Le système doit fonctionner 24/7 sans interruption
- **Sécurité** : Les données doivent être protégées et authentiques
- **Clarté** : Les résultats doivent être compréhensibles
- **Performance** : L'optimisation vient en dernier

---

#### 2. Métadonnées Obligatoires

Toute donnée DOIT inclure :

| Métadonnée | Description | Exemple |
|------------|-------------|---------|
| **source** | Identifiant unique de la source | `IFREMER_BARAG_SENSOR_PH01` |
| **date** | Horodatage ISO 8601 | `2026-04-18T19:00:00Z` |
| **method** | Méthode de mesure/calcul | `potentiometric_measurement` |
| **uncertainty** | Incertitude quantifiée | `0.02` (±0.02 unités) |
| **version** | Version du système | `v3.0.1` |
| **status** | Statut de validité | `measured` / `inferred` / `simulated` |

---

#### 3. Statuts de Validité

**measured** : Mesure directe par capteur
```json
{
  "value": 7.82,
  "status": "measured",
  "source": "IFREMER_BARAG_SENSOR_PH01"
}
```

**inferred** : Calculé à partir de mesures
```json
{
  "value": 245.3,
  "status": "inferred",
  "method": "oxygen_saturation_calculation",
  "source": "CALCULATED_FROM_TEMP_SALINITY"
}
```

**simulated** : Issu d'un modèle
```json
{
  "value": 0.65,
  "status": "simulated",
  "method": "hydrodynamic_model",
  "source": "IFREMER_MARS3D_MODEL"
}
```

---

### Vérification de Conformité

**Checklist pour les chercheurs** :

```python
def verify_abacode_compliance(data):
    """Vérifier la conformité ABACODE 2.0"""
    required_fields = ['source', 'method', 'uncertainty', 'version', 'status']
    
    for field in required_fields:
        if field not in data:
            return False, f"Champ manquant : {field}"
    
    if data['status'] not in ['measured', 'inferred', 'simulated']:
        return False, f"Statut invalide : {data['status']}"
    
    return True, "Conforme ABACODE 2.0"

# Test
measurement = {
    "value": 7.82,
    "source": "IFREMER_BARAG",
    "method": "sensor_direct",
    "uncertainty": 0.02,
    "version": "v3.0.1",
    "status": "measured"
}

is_compliant, message = verify_abacode_compliance(measurement)
print(message)  # "Conforme ABACODE 2.0"
```

---

## FAQ et Dépannage

### Questions Fréquentes

#### Q1 : Les données sont-elles gratuites ?

**R** : Oui, l'accès aux données est **100% gratuit** pour :
- Consultation web
- API (limite : 100 requêtes/heure)
- Téléchargement de séries temporelles

**Accès premium** (payant) :
- Limite augmentée (10,000 requêtes/heure)
- Support technique prioritaire
- Données historiques complètes (> 5 ans)

---

#### Q2 : Quelle est la fiabilité des données ?

**R** : Très élevée grâce à :
- Sources officielles (Ifremer, BRGM)
- Conformité ABACODE 2.0 (métadonnées complètes)
- Validation automatique (détection d'anomalies)
- Incertitudes quantifiées

**Exemple** :
```
pH = 7.82 ± 0.02 (intervalle de confiance 95%)
→ pH réel entre 7.80 et 7.84
```

---

#### Q3 : Puis-je utiliser les données dans une publication ?

**R** : Oui, absolument ! Les données sont :
- **Publiques** et **libres d'utilisation**
- **Traçables** (conformité ABACODE 2.0)
- **Citables** avec DOI (à venir)

**Citation recommandée** :
```
Ocean Sentinelle (2026). Données océanographiques du Bassin d'Arcachon.
http://oceansentinelle.fr. Accédé le 18 avril 2026.
```

---

#### Q4 : Comment recevoir des alertes par SMS ?

**R** : 
1. S'inscrire sur http://oceansentinelle.fr/api.html
2. Remplir le formulaire "Notifications"
3. Indiquer votre numéro de téléphone
4. Choisir "SMS" pour les alertes CRITICAL

**Coût** : Gratuit (limité à 10 SMS/mois)

---

#### Q5 : L'API est-elle compatible avec Excel ?

**R** : Oui, via Power Query :

1. Excel > Données > Obtenir des données > À partir du Web
2. URL : `http://api.oceansentinelle.fr/api/v1/measurements?station=BARAG&parameter=pH`
3. Cliquer sur "Charger"
4. Les données JSON sont automatiquement converties en tableau

---

#### Q6 : Puis-je intégrer les alertes dans mon système de monitoring ?

**R** : Oui, plusieurs options :

**Option 1 : Webhook** (à venir)
```json
POST https://votre-serveur.com/webhook
{
  "alert": {
    "priority": "CRITICAL",
    "station": "BARAG",
    "message": "pH critique détecté"
  }
}
```

**Option 2 : Polling API**
```python
# Vérifier toutes les 5 minutes
while True:
    alerts = requests.get("http://api.oceansentinelle.fr/api/v1/alerts").json()
    if alerts['count'] > 0:
        send_notification(alerts)
    time.sleep(300)
```

**Option 3 : Email forwarding**
- Configurer une règle de transfert d'email
- Alertes → Votre système de ticketing

---

### Dépannage

#### Problème : "API ne répond pas"

**Causes possibles** :
1. Maintenance programmée
2. Problème réseau
3. Limite de taux dépassée

**Solutions** :
```bash
# 1. Vérifier l'état du service
curl http://api.oceansentinelle.fr/api/v1/health

# 2. Vérifier votre connexion
ping api.oceansentinelle.fr

# 3. Vérifier les en-têtes de rate limiting
curl -I http://api.oceansentinelle.fr/api/v1/measurements
# Chercher : X-RateLimit-Remaining
```

---

#### Problème : "Données manquantes pour une période"

**Causes possibles** :
1. Panne de capteur
2. Maintenance station
3. Transmission interrompue

**Solutions** :
```python
# Vérifier les métadonnées
response = requests.get(
    "http://api.oceansentinelle.fr/api/v1/measurements",
    params={"station": "BARAG", "parameter": "pH", "start": "2026-04-01"}
)

data = response.json()

# Identifier les trous
timestamps = [d['timestamp'] for d in data['data']]
# Analyser les écarts > 1h
```

**Contacter le support** : support@oceansentinelle.fr

---

#### Problème : "Alerte non reçue"

**Vérifications** :
1. Email dans les spams ?
2. Adresse email correcte ?
3. Seuils personnalisés trop stricts ?

**Solution** :
```bash
# Tester manuellement
curl "http://api.oceansentinelle.fr/api/v1/alerts?priority=CRITICAL"

# Si des alertes existent mais non reçues
# → Vérifier les paramètres d'abonnement
```

---

## Support et Contact

### Assistance Technique

**Email** : support@oceansentinelle.fr  
**Délai de réponse** : 24-48h (jours ouvrés)

**Forum communautaire** : https://forum.oceansentinelle.fr (à venir)

---

### Signaler un Bug

**GitHub Issues** : https://github.com/oceansentinelle/OS3.0/issues

**Informations à fournir** :
- Description du problème
- Étapes pour reproduire
- Logs d'erreur (si applicable)
- Navigateur / OS / Version

---

### Demander une Fonctionnalité

**Email** : feature-request@oceansentinelle.fr

**Roadmap publique** : https://github.com/oceansentinelle/OS3.0/projects

---

### Contribuer au Projet

**Open Source** : Le code est disponible sur GitHub

**Comment contribuer** :
1. Fork le repository
2. Créer une branche (`feature/ma-fonctionnalite`)
3. Commit les changements
4. Ouvrir une Pull Request

**Guidelines** : Respecter la conformité ABACODE 2.0

---

## Annexes

### Glossaire

| Terme | Définition |
|-------|------------|
| **ABACODE** | Méthodologie de traçabilité des données |
| **API** | Interface de programmation (accès programmatique) |
| **Heap** | Structure de données pour tri par priorité |
| **Hypoxie** | Manque d'oxygène dissous (< 150 µmol/L) |
| **MMSI** | Identifiant unique des navires (AIS) |
| **pH** | Mesure de l'acidité (échelle 0-14) |
| **PSU** | Unité de salinité (Practical Salinity Unit) |
| **Swagger** | Outil de documentation d'API interactive |
| **TimescaleDB** | Base de données pour séries temporelles |

---

### Références

**Sources de données** :
- ERDDAP COAST-HF (Ifremer) : https://coasthf.ifremer.fr
- Hub'Eau (BRGM) : https://hubeau.eaufrance.fr

**Standards** :
- OpenAPI Specification : https://swagger.io/specification/
- ISO 19115 (Métadonnées géospatiales)
- FAIR Data Principles

**Publications** :
- Ocean Sentinelle V3.0 - Architecture Report (2026)
- ABACODE 2.0 Methodology (2026)

---

### Changelog

**v3.0.1** (18 avril 2026)
- ✅ Ajout structures de données avancées (Heap, Hash Table, Graphe)
- ✅ Conformité ABACODE 2.0 à 100%
- ✅ Documentation Swagger interactive
- ✅ Design "blanc nuageux" appliqué

**v3.0.0** (1er avril 2026)
- ✅ Refonte complète de l'architecture
- ✅ API REST v1
- ✅ Système d'alertes automatisé

**v2.0.0** (2024)
- ✅ Intégration Hub'Eau
- ✅ Première version de l'API

**v1.0.0** (2020)
- ✅ Lancement initial
- ✅ Données COAST-HF uniquement

---

## Conclusion

**OCÉAN-SENTINELLE V3.0** est une plateforme complète, fiable et accessible pour la surveillance océanographique du Bassin d'Arcachon.

### Points Clés à Retenir

✅ **Données en temps réel** : Mises à jour toutes les heures  
✅ **Alertes intelligentes** : Priorisation automatique (Heap)  
✅ **API REST** : Accès programmatique facile  
✅ **Conformité ABACODE 2.0** : Traçabilité totale  
✅ **Gratuit** : Accès libre pour tous  

### Prochaines Étapes

1. **Consulter** le site : http://oceansentinelle.fr
2. **Tester** l'API : http://api.oceansentinelle.fr/docs
3. **S'abonner** aux alertes : Formulaire en ligne
4. **Contribuer** : GitHub ou email

---

**Merci d'utiliser OCÉAN-SENTINELLE !**

*Pour toute question : support@oceansentinelle.fr*

---

**Document validé** : Conforme ABACODE 2.0  
**Version** : 3.0.1  
**Date** : 18 avril 2026  
**Auteur** : Équipe Ocean Sentinelle
