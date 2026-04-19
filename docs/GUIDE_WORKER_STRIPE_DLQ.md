# Guide Worker Stripe avec Dead Letter Queue

## 🎯 Architecture "Recevoir vite, traiter sûrement"

### Principe

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUX WEBHOOK STRIPE                       │
└─────────────────────────────────────────────────────────────┘

1. Stripe envoie événement → /api/webhooks/stripe
   ↓ Validation signature (< 1s)
   
2. Écriture en queue (DB) avec idempotence
   ↓ Vérification: event.id déjà en queue ?
   
3. Réponse HTTP 200 à Stripe (< 20s total)
   ↓ Stripe considère l'événement comme reçu
   
4. Worker asynchrone poll la queue (toutes les 5s)
   ↓ Traitement par batch de 10 événements
   
5. Traitement réel (peut prendre plusieurs secondes)
   ↓ Appels DB, Stripe API, emails, etc.
   
6. Succès → Marquer "processed"
   Échec → Retry (max 3 fois)
   3 échecs → Dead Letter Queue (DLQ)
```

### Complexité Temporelle

- **Webhook reception**: O(1) - < 1 seconde
- **Queue write**: O(1) - < 1 seconde
- **Worker processing**: O(n) où n = nombre d'événements en attente
- **Retry logic**: O(1) par événement

---

## 📊 Schéma de Base de Données

### Table stripe_event_queue

```sql
CREATE TABLE stripe_event_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_event_id VARCHAR(255) UNIQUE NOT NULL,  -- Idempotence
  event_type VARCHAR(100) NOT NULL,
  payload JSONB NOT NULL,
  
  -- Statut de traitement
  status VARCHAR(50) DEFAULT 'pending',
  -- Valeurs: 'pending', 'processing', 'processed', 'failed'
  
  retry_count INTEGER DEFAULT 0,
  last_error TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  
  CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'processed', 'failed'))
);

-- Index pour performance
CREATE INDEX idx_stripe_queue_status ON stripe_event_queue(status, created_at);
CREATE INDEX idx_stripe_queue_retry ON stripe_event_queue(retry_count) 
  WHERE status = 'pending';
CREATE INDEX idx_stripe_queue_failed ON stripe_event_queue(created_at DESC) 
  WHERE status = 'failed';
```

---

## 🚀 Déploiement du Worker

### 1. Configuration Docker Compose

```yaml
# docker-compose.prod.yml
services:
  stripe-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    environment:
      - DATABASE_URL=postgresql+asyncpg://oceansentinel:${POSTGRES_PASSWORD}@postgres:5432/oceansentinel
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - WORKER_POLL_INTERVAL=5
      - MAX_RETRY_COUNT=3
      - BATCH_SIZE=10
    depends_on:
      - postgres
      - redis
    networks:
      - backend
    restart: unless-stopped
    deploy:
      replicas: 2  # 2 workers pour redondance
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### 2. Démarrage

```bash
# Démarrer tous les services
docker-compose -f docker-compose.prod.yml up -d

# Vérifier les logs du worker
docker-compose logs -f stripe-worker

# Résultat attendu:
# stripe-worker_1  | 🚀 Stripe Event Worker démarré
# stripe-worker_1  | 📦 Traitement de 0 événements (queue vide)
```

### 3. Scaling (Multi-Workers)

```bash
# Augmenter à 5 workers
docker-compose -f docker-compose.prod.yml up -d --scale stripe-worker=5

# Vérifier
docker-compose ps stripe-worker
# Résultat:
# stripe-worker_1   running
# stripe-worker_2   running
# stripe-worker_3   running
# stripe-worker_4   running
# stripe-worker_5   running
```

**Avantages du multi-workers** :
- **Redondance** : Si un worker crash, les autres continuent
- **Performance** : Traitement parallèle des événements
- **Lock optimiste** : `SELECT ... FOR UPDATE SKIP LOCKED` évite les conflits

---

## 🔄 Cycle de Vie d'un Événement

### Cas 1 : Succès du Premier Coup

```
1. Webhook reçu → Queue (status: pending, retry_count: 0)
2. Worker poll → Récupère l'événement
3. Traitement → Succès
4. Update → (status: processed, processed_at: NOW())
```

### Cas 2 : Échec puis Succès

```
1. Webhook reçu → Queue (status: pending, retry_count: 0)
2. Worker poll → Récupère l'événement
3. Traitement → Échec (ex: DB timeout)
4. Update → (status: pending, retry_count: 1, last_error: "DB timeout")
5. Worker poll (5s plus tard) → Récupère à nouveau
6. Traitement → Succès
7. Update → (status: processed, processed_at: NOW())
```

### Cas 3 : Dead Letter Queue (3 échecs)

```
1. Webhook reçu → Queue (status: pending, retry_count: 0)
2. Tentative 1 → Échec → (retry_count: 1)
3. Tentative 2 → Échec → (retry_count: 2)
4. Tentative 3 → Échec → (retry_count: 3)
5. DLQ → (status: failed)
6. Alerte admin → Email envoyé
```

---

## 🛠️ Gestion de la Dead Letter Queue

### 1. Consulter les Événements en Échec

```bash
# Via API Admin
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://oceansentinel.fr/api/admin/stripe/failed-events

# Résultat:
{
  "total": 3,
  "events": [
    {
      "id": "abc-123",
      "stripe_event_id": "evt_1234567890",
      "event_type": "invoice.payment_failed",
      "retry_count": 3,
      "last_error": "Stripe API Error: Invalid customer ID",
      "created_at": "2026-04-19T00:30:00Z"
    }
  ]
}
```

### 2. Réessayer Manuellement

```bash
# Réessayer un événement spécifique
curl -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://oceansentinel.fr/api/admin/stripe/retry-event/abc-123

# Résultat:
{
  "message": "Événement remis en queue pour traitement"
}
```

### 3. Requête SQL Directe

```sql
-- Voir tous les événements en DLQ
SELECT 
  stripe_event_id,
  event_type,
  retry_count,
  last_error,
  created_at
FROM stripe_event_queue
WHERE status = 'failed'
ORDER BY created_at DESC;

-- Réessayer manuellement (réinitialiser)
UPDATE stripe_event_queue
SET 
  status = 'pending',
  retry_count = 0,
  last_error = NULL
WHERE id = 'abc-123';
```

---

## 📈 Monitoring et Alertes

### 1. Métriques Clés

```python
# Endpoint de monitoring
@router.get("/api/admin/stripe/metrics")
async def get_stripe_metrics(db: AsyncSession = Depends(get_db)):
    """
    Métriques du worker Stripe
    """
    # Événements en attente
    pending = await db.scalar(
        select(func.count()).select_from(StripeEventQueue)
        .where(StripeEventQueue.status == "pending")
    )
    
    # Événements en DLQ
    failed = await db.scalar(
        select(func.count()).select_from(StripeEventQueue)
        .where(StripeEventQueue.status == "failed")
    )
    
    # Événements traités (dernières 24h)
    processed_24h = await db.scalar(
        select(func.count()).select_from(StripeEventQueue)
        .where(StripeEventQueue.status == "processed")
        .where(StripeEventQueue.processed_at > datetime.utcnow() - timedelta(hours=24))
    )
    
    # Temps de traitement moyen
    avg_processing_time = await db.scalar(
        select(func.avg(
            extract('epoch', StripeEventQueue.processed_at - StripeEventQueue.created_at)
        ))
        .select_from(StripeEventQueue)
        .where(StripeEventQueue.status == "processed")
        .where(StripeEventQueue.processed_at > datetime.utcnow() - timedelta(hours=24))
    )
    
    return {
        "pending": pending,
        "failed": failed,
        "processed_24h": processed_24h,
        "avg_processing_time_seconds": round(avg_processing_time or 0, 2),
        "dlq_alert": failed >= 10  # Seuil d'alerte
    }
```

### 2. Dashboard Grafana

```yaml
# Requête Prometheus
stripe_events_pending{job="oceansentinel"}
stripe_events_failed{job="oceansentinel"}
stripe_events_processed_total{job="oceansentinel"}
stripe_processing_time_seconds{job="oceansentinel"}
```

### 3. Alertes Automatiques

```python
# app/utils/notifications.py
async def send_admin_alert(subject: str, message: str):
    """
    Envoyer une alerte admin
    
    Canaux:
    - Email (priorité haute)
    - Slack (si configuré)
    - SMS (si > 50 événements en DLQ)
    """
    # Email
    await send_email(
        to=os.getenv("ADMIN_EMAIL"),
        subject=f"[OCEAN SENTINEL] {subject}",
        body=message
    )
    
    # Slack
    if os.getenv("SLACK_WEBHOOK_URL"):
        await send_slack_notification(
            webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
            message=f"🚨 {subject}\n\n{message}"
        )
```

---

## 🧪 Tests

### 1. Test Unitaire du Worker

```python
# tests/test_stripe_worker.py
import pytest
from app.workers.stripe_worker import StripeEventWorker
from app.database.models import StripeEventQueue

@pytest.mark.asyncio
async def test_worker_processes_event_successfully(db_session):
    """
    Tester le traitement réussi d'un événement
    """
    # Créer un événement de test
    event = StripeEventQueue(
        stripe_event_id="evt_test_123",
        event_type="customer.subscription.created",
        payload={
            "id": "evt_test_123",
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_123",
                    "customer": "cus_123",
                    "items": {
                        "data": [{"price": {"id": "price_pro_monthly"}}]
                    },
                    "current_period_start": 1713484800,
                    "current_period_end": 1716163200
                }
            }
        },
        status="pending"
    )
    db_session.add(event)
    await db_session.commit()
    
    # Traiter
    worker = StripeEventWorker()
    await worker._process_single_event(db_session, event)
    
    # Vérifier
    await db_session.refresh(event)
    assert event.status == "processed"
    assert event.processed_at is not None
    assert event.retry_count == 0

@pytest.mark.asyncio
async def test_worker_retries_on_failure(db_session):
    """
    Tester le retry en cas d'échec
    """
    event = StripeEventQueue(
        stripe_event_id="evt_test_456",
        event_type="invoice.payment_failed",
        payload={"invalid": "data"},  # Données invalides
        status="pending"
    )
    db_session.add(event)
    await db_session.commit()
    
    worker = StripeEventWorker()
    await worker._process_single_event(db_session, event)
    
    await db_session.refresh(event)
    assert event.status == "pending"  # Remis en queue
    assert event.retry_count == 1
    assert event.last_error is not None

@pytest.mark.asyncio
async def test_worker_sends_to_dlq_after_max_retries(db_session):
    """
    Tester l'envoi en DLQ après 3 échecs
    """
    event = StripeEventQueue(
        stripe_event_id="evt_test_789",
        event_type="customer.subscription.updated",
        payload={"invalid": "data"},
        status="pending",
        retry_count=2  # Déjà 2 tentatives
    )
    db_session.add(event)
    await db_session.commit()
    
    worker = StripeEventWorker()
    await worker._process_single_event(db_session, event)
    
    await db_session.refresh(event)
    assert event.status == "failed"  # DLQ
    assert event.retry_count == 3
```

### 2. Test d'Intégration avec Stripe CLI

```bash
# Installer Stripe CLI
# https://stripe.com/docs/stripe-cli

# Se connecter
stripe login

# Écouter les webhooks en local
stripe listen --forward-to http://localhost:8000/api/webhooks/stripe

# Dans un autre terminal, déclencher un événement
stripe trigger customer.subscription.created

# Vérifier les logs du worker
docker-compose logs -f stripe-worker

# Résultat attendu:
# ⚙️  Traitement événement evt_... (type: customer.subscription.created)
# ✅ Événement evt_... traité avec succès
```

---

## 🔐 Sécurité

### 1. Validation de Signature Stripe

```python
# app/routers/stripe_webhooks.py
@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook Stripe avec validation de signature
    """
    payload = await request.body()
    
    try:
        # Validation OBLIGATOIRE
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Payload invalide
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Signature invalide → Tentative de fraude
        logger.warning(f"⚠️  Signature Stripe invalide depuis {request.client.host}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Écrire en queue (idempotence)
    await enqueue_stripe_event(db, event)
    
    return {"status": "received"}
```

### 2. Idempotence

```python
async def enqueue_stripe_event(db: AsyncSession, event: dict):
    """
    Écrire l'événement en queue avec idempotence
    
    Garantie: Un événement Stripe n'est jamais traité 2 fois
    """
    # Vérifier si déjà en queue
    existing = await db.execute(
        select(StripeEventQueue)
        .where(StripeEventQueue.stripe_event_id == event.id)
    )
    
    if existing.scalar_one_or_none():
        logger.info(f"ℹ️  Événement {event.id} déjà en queue (idempotence)")
        return  # Déjà traité ou en cours
    
    # Créer l'entrée
    queue_item = StripeEventQueue(
        stripe_event_id=event.id,
        event_type=event.type,
        payload=event,
        status="pending"
    )
    
    db.add(queue_item)
    await db.commit()
    
    logger.info(f"✅ Événement {event.id} ajouté à la queue")
```

---

## 📋 Checklist de Déploiement

```markdown
## Prérequis
- [ ] Réseau VPS débloqué (ports 80/443)
- [ ] PostgreSQL avec table stripe_event_queue
- [ ] Variables d'environnement configurées:
  - [ ] STRIPE_SECRET_KEY
  - [ ] STRIPE_WEBHOOK_SECRET
  - [ ] DATABASE_URL
  - [ ] ADMIN_EMAIL

## Déploiement Worker
- [ ] Build image Docker: `docker build -f Dockerfile.worker -t oceansentinel-worker .`
- [ ] Démarrer worker: `docker-compose up -d stripe-worker`
- [ ] Vérifier logs: `docker-compose logs -f stripe-worker`
- [ ] Tester avec Stripe CLI: `stripe trigger payment_intent.succeeded`

## Configuration Stripe Dashboard
- [ ] Créer endpoint webhook: https://oceansentinel.fr/api/webhooks/stripe
- [ ] Sélectionner événements:
  - [ ] customer.subscription.created
  - [ ] customer.subscription.updated
  - [ ] customer.subscription.deleted
  - [ ] invoice.payment_succeeded
  - [ ] invoice.payment_failed
  - [ ] checkout.session.completed
- [ ] Copier Signing Secret → STRIPE_WEBHOOK_SECRET

## Monitoring
- [ ] Configurer alertes DLQ (seuil: 10 événements)
- [ ] Tester alerte admin: Créer événement invalide
- [ ] Vérifier métriques: GET /api/admin/stripe/metrics
- [ ] Dashboard Grafana configuré

## Tests
- [ ] Test unitaire worker: `pytest tests/test_stripe_worker.py`
- [ ] Test intégration Stripe CLI
- [ ] Test retry (simuler échec DB)
- [ ] Test DLQ (3 échecs consécutifs)
- [ ] Test idempotence (envoyer 2x même événement)
```

---

**Document créé le** : 19 avril 2026  
**Version** : 1.0  
**Auteur** : Backend Team - Ocean Sentinel
