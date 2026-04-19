"""
OCEAN SENTINEL - Stripe Event Worker avec Dead Letter Queue
Architecture: "Recevoir vite, traiter sûrement"

Complexité temporelle:
- Réception webhook: O(1) - < 1s
- Écriture en queue: O(1) - < 1s
- Traitement async: O(n) où n = nombre d'événements en attente

Garanties:
- Idempotence: Même événement traité 1 seule fois
- Résilience: 3 tentatives avant DLQ
- Traçabilité: Logs complets de chaque étape
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.database.models import (
    StripeEventQueue,
    Subscription,
    User,
    AuditLog
)
from app.services.stripe_service import StripeService
from app.utils.notifications import send_admin_alert

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration Worker
WORKER_POLL_INTERVAL = 5  # secondes
MAX_RETRY_COUNT = 3
BATCH_SIZE = 10
DLQ_ALERT_THRESHOLD = 10  # Alerter admin si > 10 événements en DLQ


class StripeEventWorker:
    """
    Worker asynchrone pour traiter les événements Stripe
    
    Pattern:
    1. Poll la queue toutes les 5 secondes
    2. Traite par batch de 10 événements
    3. Retry 3 fois en cas d'échec
    4. Envoie en DLQ après 3 échecs
    5. Alerte admin si DLQ > seuil
    """
    
    def __init__(self):
        self.running = False
        self.processed_count = 0
        self.failed_count = 0
        self.dlq_count = 0
    
    async def start(self):
        """
        Démarrer le worker en mode continu
        """
        self.running = True
        logger.info("🚀 Stripe Event Worker démarré")
        
        try:
            while self.running:
                await self._process_batch()
                await asyncio.sleep(WORKER_POLL_INTERVAL)
        except KeyboardInterrupt:
            logger.info("⏹️  Arrêt du worker demandé")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Erreur critique dans le worker: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """
        Arrêter le worker proprement
        """
        logger.info("⏸️  Arrêt du worker en cours...")
        self.running = False
        
        # Attendre la fin du batch en cours
        await asyncio.sleep(2)
        
        logger.info(f"✅ Worker arrêté. Stats: {self.processed_count} traités, "
                   f"{self.failed_count} échecs, {self.dlq_count} en DLQ")
    
    async def _process_batch(self):
        """
        Traiter un batch d'événements en attente
        
        Complexité: O(n) où n = BATCH_SIZE
        """
        async with AsyncSessionLocal() as db:
            try:
                # Récupérer les événements en attente
                result = await db.execute(
                    select(StripeEventQueue)
                    .where(StripeEventQueue.status == "pending")
                    .where(StripeEventQueue.retry_count < MAX_RETRY_COUNT)
                    .order_by(StripeEventQueue.created_at.asc())
                    .limit(BATCH_SIZE)
                    .with_for_update(skip_locked=True)  # Éviter les conflits multi-workers
                )
                events = result.scalars().all()
                
                if not events:
                    return  # Rien à traiter
                
                logger.info(f"📦 Traitement de {len(events)} événements")
                
                # Traiter chaque événement
                for event_item in events:
                    await self._process_single_event(db, event_item)
                
                await db.commit()
                
                # Vérifier le seuil DLQ
                await self._check_dlq_threshold(db)
                
            except Exception as e:
                logger.error(f"❌ Erreur lors du traitement du batch: {e}", exc_info=True)
                await db.rollback()
    
    async def _process_single_event(
        self,
        db: AsyncSession,
        event_item: StripeEventQueue
    ):
        """
        Traiter un événement Stripe individuel
        
        Args:
            db: Session de base de données
            event_item: Événement à traiter
        
        Returns:
            None (modifie event_item en place)
        """
        event_id = event_item.stripe_event_id
        event_type = event_item.event_type
        
        logger.info(f"⚙️  Traitement événement {event_id} (type: {event_type}, "
                   f"tentative {event_item.retry_count + 1}/{MAX_RETRY_COUNT})")
        
        try:
            # Marquer comme "en cours"
            event_item.status = "processing"
            await db.flush()
            
            # Traiter selon le type d'événement
            stripe_service = StripeService(db)
            event_data = event_item.payload
            
            if event_type == "customer.subscription.created":
                await stripe_service.handle_subscription_created(event_data["data"]["object"])
            
            elif event_type == "customer.subscription.updated":
                await stripe_service.handle_subscription_updated(event_data["data"]["object"])
            
            elif event_type == "customer.subscription.deleted":
                await stripe_service.handle_subscription_deleted(event_data["data"]["object"])
            
            elif event_type == "invoice.payment_succeeded":
                await stripe_service.handle_payment_succeeded(event_data["data"]["object"])
            
            elif event_type == "invoice.payment_failed":
                await stripe_service.handle_payment_failed(event_data["data"]["object"])
            
            elif event_type == "checkout.session.completed":
                await stripe_service.handle_checkout_completed(event_data["data"]["object"])
            
            else:
                logger.warning(f"⚠️  Type d'événement non géré: {event_type}")
                # Marquer comme traité quand même pour éviter de bloquer la queue
            
            # Succès
            event_item.status = "processed"
            event_item.processed_at = datetime.utcnow()
            self.processed_count += 1
            
            logger.info(f"✅ Événement {event_id} traité avec succès")
            
        except stripe.error.StripeError as e:
            # Erreur Stripe (API, réseau, etc.)
            await self._handle_failure(event_item, f"Stripe API Error: {str(e)}")
        
        except Exception as e:
            # Erreur applicative
            await self._handle_failure(event_item, f"Application Error: {str(e)}")
    
    async def _handle_failure(
        self,
        event_item: StripeEventQueue,
        error_message: str
    ):
        """
        Gérer l'échec d'un événement
        
        Stratégie:
        - Retry < 3: Incrémenter retry_count, repasser en "pending"
        - Retry >= 3: Marquer comme "failed" (DLQ)
        """
        event_item.retry_count += 1
        event_item.last_error = error_message
        
        if event_item.retry_count >= MAX_RETRY_COUNT:
            # Dead Letter Queue
            event_item.status = "failed"
            self.dlq_count += 1
            self.failed_count += 1
            
            logger.error(
                f"💀 Événement {event_item.stripe_event_id} envoyé en DLQ "
                f"après {MAX_RETRY_COUNT} tentatives. Erreur: {error_message}"
            )
            
            # Alerter l'admin
            await send_admin_alert(
                subject=f"Stripe Event DLQ: {event_item.stripe_event_id}",
                message=f"L'événement {event_item.stripe_event_id} ({event_item.event_type}) "
                       f"a échoué après {MAX_RETRY_COUNT} tentatives.\n\n"
                       f"Dernière erreur: {error_message}\n\n"
                       f"Action requise: Vérifier et réessayer manuellement via /admin/stripe/retry-event"
            )
        else:
            # Retry
            event_item.status = "pending"
            logger.warning(
                f"⚠️  Événement {event_item.stripe_event_id} en échec "
                f"(tentative {event_item.retry_count}/{MAX_RETRY_COUNT}). "
                f"Erreur: {error_message}"
            )
    
    async def _check_dlq_threshold(self, db: AsyncSession):
        """
        Vérifier si le nombre d'événements en DLQ dépasse le seuil
        
        Si oui, alerter l'admin pour intervention manuelle
        """
        result = await db.execute(
            select(StripeEventQueue)
            .where(StripeEventQueue.status == "failed")
        )
        dlq_events = result.scalars().all()
        dlq_count = len(dlq_events)
        
        if dlq_count >= DLQ_ALERT_THRESHOLD:
            logger.warning(
                f"🚨 ALERTE DLQ: {dlq_count} événements en échec "
                f"(seuil: {DLQ_ALERT_THRESHOLD})"
            )
            
            # Grouper par type d'erreur
            error_summary = {}
            for event in dlq_events:
                error_type = event.last_error.split(":")[0] if event.last_error else "Unknown"
                error_summary[error_type] = error_summary.get(error_type, 0) + 1
            
            # Alerter l'admin
            await send_admin_alert(
                subject=f"🚨 ALERTE DLQ Stripe: {dlq_count} événements en échec",
                message=f"Le nombre d'événements Stripe en Dead Letter Queue a atteint {dlq_count}.\n\n"
                       f"Répartition des erreurs:\n" +
                       "\n".join([f"- {error}: {count} événements" 
                                 for error, count in error_summary.items()]) +
                       f"\n\nAction requise: Consulter /admin/stripe/failed-events"
            )


class StripeService:
    """
    Service pour traiter les événements Stripe
    
    Chaque méthode handle_* correspond à un type d'événement Stripe
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def handle_subscription_created(self, subscription_data: Dict[str, Any]):
        """
        Gérer la création d'un abonnement
        
        Actions:
        1. Créer l'enregistrement Subscription
        2. Attribuer le rôle correspondant au user
        3. Log d'audit
        """
        stripe_subscription_id = subscription_data["id"]
        stripe_customer_id = subscription_data["customer"]
        stripe_price_id = subscription_data["items"]["data"][0]["price"]["id"]
        
        logger.info(f"📝 Création abonnement {stripe_subscription_id}")
        
        # Récupérer l'utilisateur via customer_id
        result = await self.db.execute(
            select(User).where(User.stripe_customer_id == stripe_customer_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"Utilisateur non trouvé pour customer {stripe_customer_id}")
        
        # Déterminer le plan
        plan_type = self._get_plan_type_from_price_id(stripe_price_id)
        
        # Créer la subscription
        subscription = Subscription(
            user_id=user.id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_price_id=stripe_price_id,
            plan_type=plan_type,
            status="active",
            current_period_start=datetime.fromtimestamp(subscription_data["current_period_start"]),
            current_period_end=datetime.fromtimestamp(subscription_data["current_period_end"]),
            trial_end=datetime.fromtimestamp(subscription_data["trial_end"]) 
                      if subscription_data.get("trial_end") else None
        )
        
        self.db.add(subscription)
        
        # Attribuer le rôle
        await self._assign_role_for_plan(user.id, plan_type)
        
        # Log d'audit
        await self._log_audit(
            user_id=user.id,
            action="subscription.created",
            details={
                "stripe_subscription_id": stripe_subscription_id,
                "plan_type": plan_type
            }
        )
        
        logger.info(f"✅ Abonnement {stripe_subscription_id} créé pour user {user.id}")
    
    async def handle_subscription_updated(self, subscription_data: Dict[str, Any]):
        """
        Gérer la mise à jour d'un abonnement
        
        Cas d'usage:
        - Changement de plan
        - Renouvellement
        - Annulation programmée
        """
        stripe_subscription_id = subscription_data["id"]
        
        logger.info(f"🔄 Mise à jour abonnement {stripe_subscription_id}")
        
        # Récupérer la subscription
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.stripe_subscription_id == stripe_subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise ValueError(f"Subscription non trouvée: {stripe_subscription_id}")
        
        # Mettre à jour les champs
        subscription.status = subscription_data["status"]
        subscription.current_period_start = datetime.fromtimestamp(
            subscription_data["current_period_start"]
        )
        subscription.current_period_end = datetime.fromtimestamp(
            subscription_data["current_period_end"]
        )
        
        if subscription_data.get("cancel_at_period_end"):
            subscription.canceled_at = datetime.utcnow()
        
        # Si changement de plan
        new_price_id = subscription_data["items"]["data"][0]["price"]["id"]
        if new_price_id != subscription.stripe_price_id:
            old_plan = subscription.plan_type
            new_plan = self._get_plan_type_from_price_id(new_price_id)
            
            subscription.stripe_price_id = new_price_id
            subscription.plan_type = new_plan
            
            # Mettre à jour le rôle
            await self._assign_role_for_plan(subscription.user_id, new_plan)
            
            logger.info(f"📊 Changement de plan: {old_plan} → {new_plan}")
        
        await self._log_audit(
            user_id=subscription.user_id,
            action="subscription.updated",
            details={"stripe_subscription_id": stripe_subscription_id}
        )
    
    async def handle_subscription_deleted(self, subscription_data: Dict[str, Any]):
        """
        Gérer la suppression d'un abonnement
        
        Actions:
        1. Marquer la subscription comme canceled
        2. Rétrograder l'utilisateur au plan free
        3. Révoquer les clés API premium
        """
        stripe_subscription_id = subscription_data["id"]
        
        logger.info(f"🗑️  Suppression abonnement {stripe_subscription_id}")
        
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.stripe_subscription_id == stripe_subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            logger.warning(f"⚠️  Subscription déjà supprimée: {stripe_subscription_id}")
            return
        
        # Marquer comme canceled
        subscription.status = "canceled"
        subscription.canceled_at = datetime.utcnow()
        
        # Rétrograder au plan free
        await self._assign_role_for_plan(subscription.user_id, "free")
        
        # Révoquer les clés API si nécessaire
        await self._revoke_premium_api_keys(subscription.user_id)
        
        await self._log_audit(
            user_id=subscription.user_id,
            action="subscription.deleted",
            details={"stripe_subscription_id": stripe_subscription_id}
        )
    
    async def handle_payment_succeeded(self, invoice_data: Dict[str, Any]):
        """
        Gérer un paiement réussi
        
        Actions:
        1. Enregistrer la transaction
        2. Envoyer email de confirmation
        """
        invoice_id = invoice_data["id"]
        amount = invoice_data["amount_paid"] / 100  # Centimes → Euros
        
        logger.info(f"💰 Paiement réussi: {amount}€ (invoice {invoice_id})")
        
        # Récupérer la subscription
        stripe_subscription_id = invoice_data.get("subscription")
        if stripe_subscription_id:
            result = await self.db.execute(
                select(Subscription)
                .where(Subscription.stripe_subscription_id == stripe_subscription_id)
            )
            subscription = result.scalar_one_or_none()
            
            if subscription:
                await self._log_audit(
                    user_id=subscription.user_id,
                    action="payment.succeeded",
                    details={
                        "invoice_id": invoice_id,
                        "amount": amount,
                        "currency": invoice_data["currency"]
                    }
                )
                
                # TODO: Envoyer email de confirmation
    
    async def handle_payment_failed(self, invoice_data: Dict[str, Any]):
        """
        Gérer un paiement échoué
        
        Actions:
        1. Marquer la subscription comme past_due
        2. Envoyer email d'alerte
        3. Limiter l'accès API si > 7 jours
        """
        invoice_id = invoice_data["id"]
        
        logger.warning(f"❌ Paiement échoué: invoice {invoice_id}")
        
        stripe_subscription_id = invoice_data.get("subscription")
        if stripe_subscription_id:
            result = await self.db.execute(
                select(Subscription)
                .where(Subscription.stripe_subscription_id == stripe_subscription_id)
            )
            subscription = result.scalar_one_or_none()
            
            if subscription:
                subscription.status = "past_due"
                
                await self._log_audit(
                    user_id=subscription.user_id,
                    action="payment.failed",
                    details={"invoice_id": invoice_id}
                )
                
                # TODO: Envoyer email d'alerte
    
    async def handle_checkout_completed(self, session_data: Dict[str, Any]):
        """
        Gérer la complétion d'une session de checkout
        
        Actions:
        1. Créer le customer Stripe si nouveau
        2. Lier au user existant
        """
        session_id = session_data["id"]
        customer_id = session_data["customer"]
        client_reference_id = session_data.get("client_reference_id")  # user_id
        
        logger.info(f"🛒 Checkout complété: {session_id}")
        
        if client_reference_id:
            # Lier le customer Stripe au user
            await self.db.execute(
                update(User)
                .where(User.id == client_reference_id)
                .values(stripe_customer_id=customer_id)
            )
            
            logger.info(f"🔗 Customer {customer_id} lié au user {client_reference_id}")
    
    # Méthodes utilitaires
    
    def _get_plan_type_from_price_id(self, price_id: str) -> str:
        """
        Mapper un price_id Stripe vers un plan_type
        """
        # TODO: Récupérer depuis la config ou DB
        price_mapping = {
            "price_basic_monthly": "basic_monthly",
            "price_pro_monthly": "pro_monthly",
            "price_pro_yearly": "pro_yearly",
            "price_enterprise": "enterprise"
        }
        
        return price_mapping.get(price_id, "free")
    
    async def _assign_role_for_plan(self, user_id: str, plan_type: str):
        """
        Attribuer le rôle correspondant au plan
        """
        from app.database.models import UserRole, Role
        
        # Mapper plan → rôle
        plan_to_role = {
            "free": "free_user",
            "basic_monthly": "free_user",
            "pro_monthly": "premium_user",
            "pro_yearly": "premium_user",
            "enterprise": "premium_user"
        }
        
        role_name = plan_to_role.get(plan_type, "free_user")
        
        # Récupérer le rôle
        result = await self.db.execute(
            select(Role).where(Role.name == role_name)
        )
        role = result.scalar_one()
        
        # Supprimer les anciens rôles
        await self.db.execute(
            delete(UserRole).where(UserRole.user_id == user_id)
        )
        
        # Ajouter le nouveau rôle
        user_role = UserRole(user_id=user_id, role_id=role.id)
        self.db.add(user_role)
    
    async def _revoke_premium_api_keys(self, user_id: str):
        """
        Révoquer les clés API premium lors de la rétrogradation
        """
        from app.database.models import APIKey
        
        # Marquer les clés comme révoquées
        await self.db.execute(
            update(APIKey)
            .where(APIKey.user_id == user_id)
            .where(APIKey.is_active == True)
            .values(is_active=False, revoked_at=datetime.utcnow())
        )
        
        logger.info(f"🔑 Clés API révoquées pour user {user_id}")
    
    async def _log_audit(self, user_id: str, action: str, details: Dict[str, Any]):
        """
        Enregistrer un log d'audit
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type="subscription",
            details=details
        )
        self.db.add(audit_log)


# Point d'entrée du worker
async def main():
    """
    Démarrer le worker Stripe
    """
    worker = StripeEventWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
