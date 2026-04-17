#!/bin/bash
# ============================================================================
# Plan de Commits Git - Ocean Sentinel V3.0
# ============================================================================

# Mission 1-3 : Infrastructure de base
git add docker-compose.yml docker-compose-v3.yml
git add scripts/ingestion_stream.py scripts/test_ingestion_*.py scripts/inspect_netcdf.py
git add requirements.txt requirements-ingestion.txt
git add .env.vps.example
git add OCEAN_SENTINEL_V3_README.md.mdd QUICK_REFERENCE.md
git commit -m "feat: Infrastructure de base TimescaleDB + Ingestion NOAA

- Docker Compose pour TimescaleDB + service d'ingestion
- Scripts d'ingestion ERDDAP avec gestion erreurs
- Scripts de test et inspection NetCDF
- Documentation README et Quick Reference
- Missions 1-3 complétées"

# Mission 4 : Failover ERDDAP/SEANOE
git add scripts/test_mission4_failover.py
git commit -m "feat: Système de failover ERDDAP/SEANOE

- Failover automatique si ERDDAP indisponible
- Test de basculement ERDDAP → SEANOE
- Gestion robuste des erreurs réseau
- Mission 4 complétée"

# Mission 5 : Machine Learning
git add scripts/ml_pipeline.py requirements-ml.txt
git commit -m "feat: Pipeline Machine Learning pour prédictions océanographiques

- Modèle LSTM pour prédiction température/salinité
- Pipeline complet : ingestion → entraînement → prédiction
- Détection anomalies avec Isolation Forest
- Mission 5 complétée"

# Mission 6 : Backups automatiques
git add setup-backups.sh
git commit -m "feat: Système de backups automatiques TimescaleDB

- Backups quotidiens avec rotation (7 jours)
- Compression gzip
- Cron job automatique
- Mission 6 complétée"

# Mission 7 : Compétence agent v1.0
git add .agents/skills/ocean-sentinel-ops/SKILL.md
git add .agents/skills/ocean-sentinel-ops/README.md
git add .agents/skills/ocean-sentinel-ops/scripts/check_logs.sh
git add .agents/skills/ocean-sentinel-ops/scripts/query_prod_db.py
git commit -m "feat: Compétence agent Ocean Sentinel Ops v1.0

- Skill pour monitoring VPS via agent Antigravity
- Scripts de vérification logs et requêtes DB
- Documentation agent avec divulgation progressive
- Mission 7 complétée"

# Mission 8 : API REST + Grafana + SACS
git add api/ Dockerfile.api
git add grafana/
git add docker-compose-vps-full.yml
git add test_mission8.sh
git add MISSION_8_API_GRAFANA_SACS.md
git commit -m "feat: API REST FastAPI + Grafana + Alertes SACS

- API REST 5 routes (health, latest, history, alerts)
- Grafana avec provisioning automatique
- Dashboard 8 panneaux (température, salinité, pH, O₂)
- Système d'alertes SACS (pH < 7.8, O₂ < 150)
- Optimisé pour VPS 512 Mo RAM
- Mission 8 complétée"

# Mission 9 : Déploiement VPS + Agent v2.0
git add docker-compose-vps.yml
git add scripts/harden_vps.sh vps-setup.sh
git add deploy_mission9.ps1 deploy_to_vps.sh deploy-to-vps.sh
git add .agents/skills/ocean-sentinel-ops/scripts/monitor.py
git add MISSION_9_DEPLOIEMENT_GUIDE.md
git add QUERY_SCRIPT_GUIDE.md
git commit -m "feat: Déploiement production VPS + Agent monitoring v2.0

- Déploiement complet sur VPS Hostinger (76.13.43.3)
- Configuration pare-feu UFW + Hostinger
- Script de monitoring Python (monitor.py)
- Compétence agent v2.0.0 avec monitoring API REST
- Scripts de déploiement automatisés
- Guide de déploiement complet
- Mission 9 complétée (95%)"

# Fichiers de configuration VPS (non commitables)
git add .gitignore
echo ".env.vps" >> .gitignore
echo "scripts/__pycache__/" >> .gitignore
git commit -m "chore: Ajout .gitignore pour fichiers sensibles"

echo "✅ Tous les commits créés avec succès !"
echo ""
echo "Vérifiez l'historique avec:"
echo "  git log --oneline --graph --all"
