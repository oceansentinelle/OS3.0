# 🚒 RUNBOOK: OCEAN-SENTINEL-API-DEGRADATION

**Nom du Runbook**: `OCEAN-SENTINEL-API-DEGRADATION`  
**Version**: 1.0.0  
**Dernière mise à jour**: 2026-04-25  
**Propriétaire**: Équipe DevOps Ocean Sentinel

---

## 🎯 Déclencheur (Trigger)

**Alerte**: Taux d'erreurs 5xx > 5% **OU** Latence P99 > 3s sur endpoints `/api/v1/*`

**Canaux de notification**:
- PagerDuty (N2/N3)
- Slack #incidents-prod
- Email ops@oceansentinelle.fr

---

## 📊 Contexte & Impact

### Dépendances
- **API externe**: `https://oceansentinelle.fr/api/v1`
- **Endpoints critiques**:
  - `/api/v1/stations` (Liste stations)
  - `/api/v1/station/{id}/latest` (Données temps réel)
  - `/api/v1/meteo/arcachon` (Météo marine)

### Impact Business
- **Haute sévérité**: Dashboard utilisateurs affiche données obsolètes
- **Moyenne sévérité**: Alertes SACS (hypoxie/acidification) retardées
- **SLA**: 99.5% uptime mensuel (tolérance: 3.6h downtime/mois)

---

## 🔍 ÉTAPE 1: Détection et Triage (5 min)

### Actions N1 (Automatisées)

```bash
# 1. Vérifier état Circuit Breaker
curl http://localhost:9090/metrics | grep circuit_breaker_state
# Attendu: circuit_breaker_state{api="ocean_sentinel"} 0  (0=CLOSED, 1=OPEN, 2=HALF_OPEN)

# 2. Vérifier taux d'erreur actuel
curl http://localhost:9090/api/v1/query?query='rate(http_requests_total{status=~"5.."}[5m])'

# 3. Vérifier latence P99
curl http://localhost:9090/api/v1/query?query='histogram_quantile(0.99, http_request_duration_seconds)'
```

### Dashboard Grafana
- **URL**: `https://grafana.oceansentinelle.fr/d/ocean-api`
- **Panels clés**:
  - Golden Signals (Latency, Traffic, Errors, Saturation)
  - Circuit Breaker State
  - Retry Budget Consumption

### Questions de Triage
- [ ] Toutes les stations affectées ou seulement `BARAG_PROXY` / `ARCACHON_EYRAC` ?
- [ ] L'erreur est-elle côté client (4xx) ou serveur (5xx) ?
- [ ] Le Circuit Breaker est-il ouvert (OPEN) ?

---

## 🔬 ÉTAPE 2: Diagnostic (10 min)

### Logs Structurés (ELK/Loki)

```bash
# Filtrer erreurs 5xx dernières 15 minutes
kubectl logs -l app=ocean-sentinel-client --since=15m | \
  jq 'select(.status >= 500 and .endpoint | contains("oceansentinelle.fr"))'

# Rechercher Correlation IDs
grep "trace_id: 550e8400-e29b-41d4-a716-446655440000" /var/log/ocean-sentinel/*.log
```

### Test Manuel (Health Check)

```bash
# Test depuis serveur production
curl -I -m 5 https://oceansentinelle.fr/health
# Attendu: HTTP/2 200

# Test avec timeout court
time curl -s https://oceansentinelle.fr/api/v1/stations | jq .
# Attendu: < 2s
```

### Vérification DNS/Réseau

```bash
# Résolution DNS
dig oceansentinelle.fr +short

# Test connectivité
traceroute oceansentinelle.fr

# Vérifier certificat SSL
openssl s_client -connect oceansentinelle.fr:443 -servername oceansentinelle.fr < /dev/null 2>&1 | \
  openssl x509 -noout -dates
```

---

## 🛠️ ÉTAPE 3: Mitigation / Remédiation (15 min)

### Scénario A: Erreur 5xx Généralisée (API Tierce Down)

**Action**: Laisser Circuit Breaker en position OPEN

```bash
# Vérifier que CB est ouvert
curl http://localhost:9090/metrics | grep 'circuit_breaker_state{api="ocean_sentinel"} 1'

# Activer Graceful Degradation (cache)
kubectl set env deployment/ocean-sentinel-client ENABLE_CACHE_FALLBACK=true
```

**Communication**:
```
🔴 INCIDENT: Dégradation API Ocean Sentinel
Cause: Erreurs 5xx côté fournisseur
Impact: Données météo affichent dernière valeur en cache (max 5 min périmée)
Action: Circuit Breaker activé, surveillance en cours
ETA: Dépend du rétablissement fournisseur
```

### Scénario B: Timeout / Latence Élevée

**Action**: Réduire timeout temporairement

```bash
# Passer timeout de 5s à 2s
kubectl set env deployment/ocean-sentinel-client HTTP_READ_TIMEOUT_MS=2000

# Augmenter retry budget si nécessaire
kubectl set env deployment/ocean-sentinel-client RETRY_BUDGET_PERCENT=15
```

### Scénario C: Erreur 429 (Rate Limit)

**Action**: Activer backoff agressif

```bash
# Augmenter délai base backoff
kubectl set env deployment/ocean-sentinel-client BACKOFF_BASE_DELAY_MS=500

# Réduire taux requêtes côté client
kubectl set env deployment/ocean-sentinel-client CLIENT_RATE_LIMIT_RPS=5
```

---

## 📢 ÉTAPE 4: Communication & Clôture (10 min)

### Page de Statut

**URL**: `https://status.oceansentinelle.fr`

**Template Message**:
```
🟡 Dégradation partielle - Données météo marines
Début: 2026-04-25 15:40 UTC
Cause: Instabilité API externe Ocean Sentinel
Impact: Affichage données en cache (périmées max 5 min)
Prochaine mise à jour: Dans 30 minutes
```

### Post-Mortem (Blameless)

**Deadline**: 48h après résolution

**Sections obligatoires**:
1. **Timeline** (format ISO 8601)
2. **Root Cause** (5 Whys)
3. **Impact** (utilisateurs affectés, durée)
4. **Actions correctives** (court terme / long terme)
5. **Action Items** (avec assignés et deadlines)

**Template**:
```markdown
# Post-Mortem: OCEAN-SENTINEL-API-DEGRADATION-20260425

## Résumé Exécutif
[1 paragraphe max]

## Timeline
- 15:40 UTC: Alerte déclenchée (latence P99 > 3s)
- 15:42 UTC: Circuit Breaker ouvert automatiquement
- 15:45 UTC: Cache fallback activé
- 16:10 UTC: API tierce rétablie
- 16:15 UTC: Circuit Breaker fermé, service normal

## Root Cause Analysis (5 Whys)
1. Pourquoi latence élevée ? → API tierce retournait 503
2. Pourquoi 503 ? → Surcharge serveur chez fournisseur
3. Pourquoi surcharge ? → Pic trafic non anticipé
4. Pourquoi non anticipé ? → Pas de communication préalable
5. Pourquoi pas de communication ? → Absence SLA formalisé

## Impact
- Durée: 35 minutes
- Utilisateurs affectés: ~1200 (Dashboard)
- Données périmées: Max 5 minutes (cache)
- SLA: Respecté (< 3.6h/mois)

## Actions Correctives
### Court terme (< 1 semaine)
- [ ] Formaliser SLA avec fournisseur API (@ops-lead)
- [ ] Augmenter TTL cache à 15 min (@backend-dev)

### Long terme (< 1 mois)
- [ ] Implémenter fallback sur API secondaire (@architect)
- [ ] Ajouter alertes proactives (latence P95 > 2s) (@sre)
```

---

## 🧪 Tests de Validation Post-Incident

```bash
# 1. Vérifier Circuit Breaker fermé
curl http://localhost:9090/metrics | grep 'circuit_breaker_state{api="ocean_sentinel"} 0'

# 2. Vérifier latence normalisée
curl http://localhost:9090/api/v1/query?query='histogram_quantile(0.99, http_request_duration_seconds)' | \
  jq '.data.result[0].value[1] | tonumber < 1'  # Doit être < 1s

# 3. Vérifier taux erreur < 1%
curl http://localhost:9090/api/v1/query?query='rate(http_requests_total{status=~"5.."}[5m])' | \
  jq '.data.result[0].value[1] | tonumber < 0.01'

# 4. Test end-to-end
curl -s https://oceansentinelle.fr/api/v1/meteo/arcachon | jq '.wind_speed' | grep -E '^[0-9]+\.[0-9]+$'
```

---

## 📞 Contacts Escalade

| Niveau | Rôle | Contact | Délai réponse |
|--------|------|---------|---------------|
| N1 | Ops On-Call | ops-oncall@oceansentinelle.fr | 5 min |
| N2 | SRE Lead | sre-lead@oceansentinelle.fr | 15 min |
| N3 | CTO | cto@oceansentinelle.fr | 30 min |

**Fournisseur API**:
- Support Ocean Sentinel: support@oceansentinelle.fr
- Status Page: https://status.oceansentinelle.fr

---

## 📚 Références

- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Google SRE Book - Handling Overload](https://sre.google/sre-book/handling-overload/)
- [OpenAPI Spec](../backend/openapi.yaml)
- [Client Config](../backend/client_config.yaml)
