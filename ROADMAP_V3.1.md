# Roadmap Ocean Sentinel V3.1

## Objectif : Activation des Workers et Ingestion de Données

### Phase 1 : Workers (Semaine 1-2)
- [ ] Corriger les health checks des workers
- [ ] Activer l'orchestrator
- [ ] Configurer l'ingest_worker (ERDDAP)
- [ ] Tester transform_worker
- [ ] Activer alert_worker

### Phase 2 : Ingestion ERDDAP (Semaine 3)
- [ ] Configurer les endpoints ERDDAP COAST-HF
- [ ] Implémenter le parser de données
- [ ] Créer les pipelines d'ingestion
- [ ] Tester avec stations Arcachon Eyrac et Cap Ferret

### Phase 3 : Système d'Alertes SACS (Semaine 4)
- [ ] Implémenter la détection d'anomalies
- [ ] Configurer les seuils d'alerte
- [ ] Créer les notifications (email, webhook)
- [ ] Tester les alertes en conditions réelles

### Phase 4 : Monitoring (Semaine 5)
- [ ] Déployer Grafana
- [ ] Créer les dashboards de monitoring
- [ ] Configurer les alertes Prometheus

### Phase 5 : Frontend Complet (Semaine 6-8)
- [ ] Déployer l'application React/Next.js
- [ ] Intégrer les graphiques de données
- [ ] Ajouter la carte interactive
- [ ] Implémenter l'authentification

## Critères de Succès V3.1
- ✅ Workers opérationnels (healthy)
- ✅ Données ERDDAP ingérées toutes les heures
- ✅ Alertes SACS fonctionnelles
- ✅ Grafana accessible et configuré
- ✅ Frontend React déployé
