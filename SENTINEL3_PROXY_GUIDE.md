# 🛰️ Ocean Sentinel V3.0 - Guide Proxy Sentinel-3

## Vue d'Ensemble

Ce guide explique comment utiliser les données satellitaires **Copernicus Sentinel-3** comme proxy pour les mesures in-situ BARAG, conformément à la méthodologie **ABACODE 2.0**.

---

## 🎯 Objectif

Pallier l'absence d'API REST temps réel pour la station BARAG en utilisant :
- **Données satellitaires** Sentinel-3 SLSTR (SST)
- **Inférence biogéochimique** pour les paramètres dérivés
- **Marquage qualité** conforme ABACODE 2.0

---

## 📊 Architecture du Proxy

```
Copernicus Sentinel-3 (SST)
         ↓
   Récupération T-24h
         ↓
   Inférence Biogéochimique
   (Salinité, pH, O₂, Turbidité)
         ↓
   TimescaleDB (quality_flag=2)
         ↓
   API REST + Grafana
```

---

## 🔬 Paramètres Inférés

### **1. Température de Surface (SST)**
- **Source** : Sentinel-3 SLSTR
- **Résolution** : 1 km
- **Précision** : ±0.1 K
- **Statut** : **Mesurée** (satellite)

### **2. Salinité (PSAL)**
- **Méthode** : Relation empirique avec SST
- **Formule** : `PSAL = 35.0 - (SST - 15.0) × 0.2`
- **Plage** : 30-36 PSU
- **Statut** : **Inférée**

### **3. pH**
- **Méthode** : Relation inverse avec SST (solubilité CO₂)
- **Formule** : `pH = 8.1 - (SST - 15.0) × 0.01`
- **Plage** : 7.5-8.3
- **Statut** : **Inférée**

### **4. Oxygène Dissous (DOX2)**
- **Méthode** : Loi de Henry (solubilité vs température)
- **Formule** : `DOX2 = 280.0 - (SST - 15.0) × 8.0`
- **Plage** : 150-350 µmol/kg
- **Statut** : **Inférée**

### **5. Turbidité (TURB)**
- **Méthode** : Variation saisonnière
- **Valeurs** : Printemps (2.5), Été (3.0), Automne (2.0), Hiver (1.5)
- **Statut** : **Simulée**

---

## 🚀 Installation et Utilisation

### **Étape 1 : Transfert sur le VPS**

```powershell
# Depuis Windows
scp scripts/ingestion_sentinel3.py root@76.13.43.3:/opt/oceansentinel/scripts/
scp requirements-sentinel3.txt root@76.13.43.3:/opt/oceansentinel/
```

### **Étape 2 : Installation des Dépendances**

```bash
# Sur le VPS
cd /opt/oceansentinel
pip3 install -r requirements-sentinel3.txt
```

### **Étape 3 : Configuration**

```bash
# Créer le fichier .env si pas déjà fait
cat >> .env << 'EOF'
# Copernicus Marine Service (optionnel pour vraie API)
CMEMS_USERNAME=votre_username
CMEMS_PASSWORD=votre_password

# Base de données
DB_HOST=localhost
DB_PORT=6543
DB_NAME=oceansentinelle
DB_USER=oceansentinel
DB_PASSWORD=votre_mot_de_passe
EOF
```

### **Étape 4 : Exécution Initiale**

```bash
# Initialiser la base et remplir 30 jours de données
python3 scripts/ingestion_sentinel3.py
```

**Résultat attendu :**
```
================================================================================
Ocean Sentinel V3.0 - Ingestion Sentinel-3 (Proxy Satellitaire)
================================================================================
📊 Initialisation de la base de données...
✅ Base de données initialisée avec succès
🛰️  Récupération des données Sentinel-3...
🔄 Backfill de 30 jours de données Sentinel-3...
✅ Données insérées: 2026-03-18 12:00:00
   Température: 14.50°C
   Salinité (inférée): 35.10 PSU
   pH (inféré): 8.095
   O₂ (inféré): 276.0 µmol/kg
...
✅ Backfill terminé: 30 jours de données insérées
================================================================================
✅ Ingestion Sentinel-3 terminée avec succès
================================================================================
```

### **Étape 5 : Vérification**

```bash
# Vérifier les données insérées
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle -c "
SELECT COUNT(*), MIN(time), MAX(time), station_id 
FROM ocean_data 
GROUP BY station_id;"
```

**Résultat attendu :**
```
 count |          min           |          max           |    station_id    
-------+------------------------+------------------------+------------------
    30 | 2026-03-18 12:00:00+00 | 2026-04-17 12:00:00+00 | BARAG_SENTINEL3
```

### **Étape 6 : Rafraîchir Grafana**

```bash
# Redémarrer Grafana pour recharger les données
docker compose -f /opt/oceansentinel/docker-compose-vps.yml restart grafana
```

Puis accédez à http://76.13.43.3:3000 et vérifiez que les graphiques affichent les données !

---

## 📅 Automatisation (Cron)

Pour mettre à jour quotidiennement :

```bash
# Ajouter au crontab
crontab -e

# Ajouter cette ligne (exécution à 6h du matin)
0 6 * * * cd /opt/oceansentinel && /usr/bin/python3 scripts/ingestion_sentinel3.py >> /var/log/sentinel3_ingestion.log 2>&1
```

---

## 🏷️ Marquage Qualité (ABACODE 2.0)

Les données Sentinel-3 sont marquées avec `quality_flag = 2` :

| quality_flag | Signification | Type de Donnée |
|--------------|---------------|----------------|
| **1** | Mesure in-situ validée | BARAG direct |
| **2** | Donnée inférée/proxy | **Sentinel-3** |
| **3** | Donnée simulée/mock | Test |
| **0** | Donnée invalide | Erreur |

---

## ⚠️ Limites et Incertitudes

### **Biais Connus**

1. **Décalage temporel** : T-24h (latence satellite)
2. **Résolution spatiale** : 1 km (moyenne sur pixel)
3. **Inférence biogéochimique** : Relations empiriques (±10-15% erreur)
4. **Paramètres manquants** : Nutriments, microbiologie

### **Fiabilité Décisionnelle**

| Paramètre | Fiabilité | Usage Recommandé |
|-----------|-----------|------------------|
| **SST** | Haute (satellite) | ✅ Monitoring thermique |
| **PSAL** | Moyenne (inférée) | ⚠️ Tendances seulement |
| **pH** | Moyenne (inférée) | ⚠️ Alertes approximatives |
| **DOX2** | Moyenne (inférée) | ⚠️ Détection anomalies |
| **TURB** | Faible (simulée) | ❌ Indicatif seulement |

---

## 🔄 Migration vers Données Réelles

Lorsque l'API BARAG temps réel sera disponible :

1. **Arrêter** le cron Sentinel-3
2. **Activer** l'ingestion ERDDAP/SEANOE
3. **Conserver** les données Sentinel-3 historiques (archive)
4. **Comparer** les deux sources pour validation

---

## 📚 Références

- **Copernicus Marine Service** : https://marine.copernicus.eu/
- **Sentinel-3 SLSTR** : https://sentinel.esa.int/web/sentinel/missions/sentinel-3
- **COAST-HF** : http://www.coast-hf.fr/
- **ABACODE 2.0** : Méthodologie de marquage qualité données

---

## 🆘 Support

En cas de problème :

```bash
# Vérifier les logs
tail -f /var/log/sentinel3_ingestion.log

# Vérifier la connexion DB
docker exec -it oceansentinel_timescaledb psql -U oceansentinel -d oceansentinelle

# Tester manuellement
python3 scripts/ingestion_sentinel3.py
```

---

**🛰️ Sentinel-3 Proxy** - *Solution transitoire pour maintenir la continuité opérationnelle*
