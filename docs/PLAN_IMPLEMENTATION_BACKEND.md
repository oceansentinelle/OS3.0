# Plan d'Implémentation Backend - Ocean Sentinel

## 📋 Vue d'Ensemble

**Projet** : GeM OCÉAN-SENTINELLE  
**Méthodologie** : ABACODE 2.0  
**Infrastructure** : VPS Hostinger (76.13.43.3)  
**Priorité** : Stabilité > Sécurité > Clarté > Performance  
**Date** : 19 avril 2026

---

## 🎯 Objectifs Critiques

1. ✅ **Backend API** : Endpoints `/api/auth/*` avec FastAPI + JWT
2. ✅ **Base de données** : PostgreSQL + pgvector pour RAG
3. ✅ **Stripe** : Webhooks et plans tarifaires SaaS
4. ✅ **Accessibilité** : Tests WCAG 2.2 (WAVE, axe DevTools)
5. ✅ **Déploiement** : Configuration VPS Hostinger + déblocage réseau

---

## 1. Backend API - FastAPI + JWT (Authentification Sécurisée)

### 1.1 Architecture Asynchrone

```python
# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

app = FastAPI(
    title="Ocean Sentinel API",
    version="1.0.0",
    description="API sécurisée pour la plateforme Ocean Sentinel"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://oceansentinel.fr"],  # Production uniquement
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configuration JWT
SECRET_KEY = os.getenv("API_JWT_SECRET")  # 256 bits minimum
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password Hashing avec Argon2 (ANSSI 2026)
pwd_context = PasswordHash((
    Argon2Hasher(
        memory_cost=65536,      # 64 MB
        time_cost=3,            # 3 itérations
        parallelism=4,          # 4 threads
        hash_len=32,            # 32 bytes output
        salt_len=16             # 16 bytes salt
    ),
))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
```

### 1.2 Modèles de Données

```python
# backend/app/models/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=12, description="Minimum 12 caractères")
    consent: bool = Field(..., description="Consentement RGPD")
    consent_timestamp: datetime
    consent_ip_address: Optional[str] = None

class UserInDB(UserBase):
    id: str
    password_hash: str
    email_verified: bool = False
    roles: List[str] = ["free_user"]
    created_at: datetime
    last_login_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    roles: List[str] = []
```

### 1.3 Endpoints d'Authentification

```python
# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.auth import UserCreate, Token, UserInDB
from app.services.auth import AuthService
from app.utils.audit import log_audit_event

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Inscription d'un nouvel utilisateur
    
    Conformité:
    - RGPD: Consentement explicite requis
    - ANSSI 2026: Hashing Argon2
    - Audit: Logs de création de compte
    """
    auth_service = AuthService(db)
    
    # Vérifier si l'email existe déjà
    existing_user = await auth_service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte existe déjà avec cette adresse email"
        )
    
    # Valider la politique de mot de passe
    if not auth_service.validate_password_policy(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe ne respecte pas les critères de sécurité ANSSI 2026"
        )
    
    # Créer l'utilisateur
    new_user = await auth_service.create_user(user)
    
    # Log d'audit
    await log_audit_event(
        db=db,
        user_id=new_user.id,
        action="user.register",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    # Générer les tokens
    access_token = auth_service.create_access_token(
        data={"sub": new_user.id, "email": new_user.email, "roles": new_user.roles}
    )
    refresh_token = await auth_service.create_refresh_token(
        user_id=new_user.id,
        device_info={
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host
        }
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Connexion utilisateur avec email/password
    
    Sécurité:
    - Rate limiting: 5 tentatives max / 15 min
    - Verrouillage compte après 5 échecs
    - Logs de tentatives de connexion
    """
    auth_service = AuthService(db)
    
    # Vérifier rate limiting
    if await auth_service.is_rate_limited(form_data.username, request.client.host):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives de connexion. Réessayez dans 15 minutes."
        )
    
    # Authentifier l'utilisateur
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        await auth_service.increment_failed_login(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier si le compte est verrouillé
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Compte verrouillé jusqu'à {user.locked_until.isoformat()}"
        )
    
    # Réinitialiser les tentatives échouées
    await auth_service.reset_failed_login(user.id)
    
    # Mettre à jour last_login_at
    await auth_service.update_last_login(user.id)
    
    # Log d'audit
    await log_audit_event(
        db=db,
        user_id=user.id,
        action="user.login",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    # Générer les tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email, "roles": user.roles}
    )
    refresh_token = await auth_service.create_refresh_token(
        user_id=user.id,
        device_info={
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host
        }
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Rafraîchir l'access token avec un refresh token valide
    
    Sécurité:
    - Rotation des refresh tokens
    - Révocation automatique de l'ancien token
    """
    auth_service = AuthService(db)
    
    # Valider le refresh token
    token_data = await auth_service.validate_refresh_token(refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré"
        )
    
    # Révoquer l'ancien refresh token
    await auth_service.revoke_refresh_token(refresh_token)
    
    # Créer de nouveaux tokens
    user = await auth_service.get_user_by_id(token_data.user_id)
    
    new_access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email, "roles": user.roles}
    )
    new_refresh_token = await auth_service.create_refresh_token(
        user_id=user.id,
        device_info=token_data.device_info
    )
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(
    refresh_token: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Déconnexion utilisateur
    
    Actions:
    - Révocation du refresh token
    - Log d'audit
    """
    auth_service = AuthService(db)
    
    await auth_service.revoke_refresh_token(refresh_token)
    
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action="user.logout"
    )
    
    return {"message": "Déconnexion réussie"}

@router.delete("/delete-account")
async def delete_account(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Suppression de compte (Droit à l'oubli RGPD)
    
    Conformité:
    - Art. 17 RGPD: Droit à l'effacement
    - Délai: 30 jours maximum
    - Conservation: Données de facturation (10 ans)
    """
    auth_service = AuthService(db)
    
    # Soft delete (marquage pour suppression)
    await auth_service.mark_for_deletion(current_user.id)
    
    # Révocation de tous les tokens
    await auth_service.revoke_all_user_tokens(current_user.id)
    
    # Log d'audit
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action="user.delete_account"
    )
    
    return {
        "message": "Votre compte sera supprimé sous 30 jours conformément au RGPD",
        "deletion_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
```

### 1.4 Service d'Authentification

```python
# backend/app/services/auth.py
from datetime import datetime, timedelta
from typing import Optional
import jwt
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.auth import UserCreate, UserInDB
from app.database.models import User, RefreshToken

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def validate_password_policy(self, password: str) -> bool:
        """
        Validation conforme ANSSI 2026
        """
        if len(password) < 12:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])
    
    async def create_user(self, user: UserCreate) -> UserInDB:
        """
        Créer un nouvel utilisateur avec hashing Argon2
        """
        password_hash = pwd_context.hash(user.password)
        
        db_user = User(
            email=user.email,
            password_hash=password_hash,
            consent_given_at=user.consent_timestamp,
            consent_ip_address=user.consent_ip_address,
            data_processing_consent=user.consent
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return UserInDB.from_orm(db_user)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """
        Authentifier un utilisateur
        """
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not pwd_context.verify(password, user.password_hash):
            return None
        
        return UserInDB.from_orm(user)
    
    def create_access_token(self, data: dict) -> str:
        """
        Créer un JWT access token (30 min)
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def create_refresh_token(self, user_id: str, device_info: dict) -> str:
        """
        Créer un refresh token (7 jours) avec rotation
        """
        token = secrets.token_urlsafe(32)
        token_hash = pwd_context.hash(token)
        
        db_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            device_info=device_info,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        self.db.add(db_token)
        await self.db.commit()
        
        return token
    
    async def is_rate_limited(self, email: str, ip_address: str) -> bool:
        """
        Vérifier le rate limiting (5 tentatives / 15 min)
        """
        # Implémentation avec Redis recommandée
        # Pour l'instant, vérification en DB
        pass
    
    async def increment_failed_login(self, email: str):
        """
        Incrémenter le compteur d'échecs de connexion
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.failed_login_attempts += 1
            
            # Verrouiller après 5 échecs
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            
            await self.db.commit()
```

---

## 2. Base de Données - PostgreSQL + pgvector

### 2.1 Script d'Initialisation

```sql
-- backend/database/init.sql

-- Extension pgvector pour RAG
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table users (déjà définie dans ARCHITECTURE_PORTAIL_API_ALERTES.md)
-- Voir schéma complet précédent

-- Table documents pour RAG
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(500) NOT NULL,
  content TEXT NOT NULL,
  source VARCHAR(255), -- URL, fichier, etc.
  document_type VARCHAR(50), -- 'rapport', 'article', 'alerte'
  
  -- Métadonnées
  author VARCHAR(255),
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Recherche full-text
  search_vector tsvector GENERATED ALWAYS AS (
    to_tsvector('french', coalesce(title, '') || ' ' || coalesce(content, ''))
  ) STORED
);

-- Index full-text search
CREATE INDEX idx_documents_search ON documents USING GIN(search_vector);

-- Table embeddings pour similarité vectorielle
CREATE TABLE embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  
  -- Vecteur (dimension 384 pour all-MiniLM-L6-v2, ou 1536 pour OpenAI)
  embedding vector(384) NOT NULL,
  
  -- Chunk info (pour documents longs)
  chunk_index INTEGER,
  chunk_text TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index HNSW pour recherche de similarité (O(log n))
CREATE INDEX idx_embeddings_hnsw ON embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Fonction de recherche par similarité
CREATE OR REPLACE FUNCTION search_similar_documents(
  query_embedding vector(384),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INTEGER DEFAULT 5
)
RETURNS TABLE (
  document_id UUID,
  title VARCHAR,
  content TEXT,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    d.id,
    d.title,
    e.chunk_text,
    1 - (e.embedding <=> query_embedding) AS similarity
  FROM embeddings e
  JOIN documents d ON e.document_id = d.id
  WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
  ORDER BY e.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- Table pour données océanographiques (TimescaleDB)
CREATE TABLE ocean_data (
  time TIMESTAMPTZ NOT NULL,
  location_id VARCHAR(50) NOT NULL,
  
  -- Paramètres physico-chimiques
  temperature FLOAT,
  salinity FLOAT,
  ph FLOAT,
  dissolved_oxygen FLOAT,
  turbidity FLOAT,
  
  -- Métadonnées
  sensor_id VARCHAR(100),
  quality_flag INTEGER, -- 0: bon, 1: suspect, 2: mauvais
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Hypertable TimescaleDB
SELECT create_hypertable('ocean_data', 'time', if_not_exists => TRUE);

-- Index pour requêtes fréquentes
CREATE INDEX idx_ocean_data_location_time ON ocean_data(location_id, time DESC);
CREATE INDEX idx_ocean_data_ph ON ocean_data(ph, time DESC) WHERE ph IS NOT NULL;
```

### 2.2 Configuration Async SQLAlchemy

```python
# backend/app/database/__init__.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://oceansentinel:password@localhost:5432/oceansentinel"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Vérifier les connexions avant utilisation
    pool_recycle=3600    # Recycler les connexions après 1h
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## 3. Stripe - Webhooks et Plans Tarifaires

### 3.1 Configuration Stripe

```python
# backend/app/routers/stripe_webhooks.py
from fastapi import APIRouter, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import stripe
import os

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook Stripe - Pattern "Recevoir vite, traiter sûrement"
    
    Architecture:
    1. Valider la signature (< 1s)
    2. Écrire dans la queue (< 1s)
    3. Répondre HTTP 200 (< 20s total)
    4. Traiter asynchronement via worker
    """
    payload = await request.body()
    
    try:
        # Validation de la signature Stripe
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Écrire dans la queue (idempotence via event.id)
    await enqueue_stripe_event(db, event)
    
    return {"status": "received"}

async def enqueue_stripe_event(db: AsyncSession, event: dict):
    """
    Écrire l'événement Stripe dans la queue
    """
    from app.database.models import StripeEventQueue
    
    # Vérifier si déjà traité (idempotence)
    existing = await db.execute(
        select(StripeEventQueue).where(StripeEventQueue.stripe_event_id == event.id)
    )
    if existing.scalar_one_or_none():
        return  # Déjà en queue
    
    queue_item = StripeEventQueue(
        stripe_event_id=event.id,
        event_type=event.type,
        payload=event,
        status="pending"
    )
    
    db.add(queue_item)
    await db.commit()
```

### 3.2 Worker de Traitement Asynchrone

```python
# backend/app/workers/stripe_worker.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.database.models import StripeEventQueue, Subscription
from app.services.stripe_service import StripeService

async def process_stripe_events():
    """
    Worker pour traiter les événements Stripe en queue
    
    Dead Letter Queue: Après 3 échecs, marquer comme 'failed'
    """
    while True:
        async with AsyncSessionLocal() as db:
            # Récupérer les événements en attente
            result = await db.execute(
                select(StripeEventQueue)
                .where(StripeEventQueue.status == "pending")
                .where(StripeEventQueue.retry_count < 3)
                .limit(10)
            )
            events = result.scalars().all()
            
            for event_item in events:
                try:
                    await process_single_event(db, event_item)
                    event_item.status = "processed"
                    event_item.processed_at = datetime.utcnow()
                except Exception as e:
                    event_item.retry_count += 1
                    event_item.last_error = str(e)
                    
                    if event_item.retry_count >= 3:
                        event_item.status = "failed"  # Dead Letter Queue
                
                await db.commit()
        
        await asyncio.sleep(5)  # Vérifier toutes les 5 secondes

async def process_single_event(db: AsyncSession, event_item: StripeEventQueue):
    """
    Traiter un événement Stripe spécifique
    """
    event = event_item.payload
    stripe_service = StripeService(db)
    
    if event.type == "customer.subscription.created":
        await stripe_service.handle_subscription_created(event.data.object)
    
    elif event.type == "customer.subscription.updated":
        await stripe_service.handle_subscription_updated(event.data.object)
    
    elif event.type == "customer.subscription.deleted":
        await stripe_service.handle_subscription_deleted(event.data.object)
    
    elif event.type == "invoice.payment_succeeded":
        await stripe_service.handle_payment_succeeded(event.data.object)
    
    elif event.type == "invoice.payment_failed":
        await stripe_service.handle_payment_failed(event.data.object)
```

### 3.3 Plans Tarifaires

```python
# backend/scripts/setup_stripe_products.py
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Créer les produits
products = {
    "basic": stripe.Product.create(
        name="Ocean Sentinel Basic",
        description="Accès de base aux API et alertes",
        metadata={"plan_type": "basic"}
    ),
    "pro": stripe.Product.create(
        name="Ocean Sentinel Pro",
        description="Accès complet avec alertes avancées",
        metadata={"plan_type": "pro"}
    ),
    "enterprise": stripe.Product.create(
        name="Ocean Sentinel Enterprise",
        description="Solution complète pour professionnels",
        metadata={"plan_type": "enterprise"}
    )
}

# Créer les prix
prices = {
    "basic_monthly": stripe.Price.create(
        product=products["basic"].id,
        unit_amount=990,  # 9.90€
        currency="eur",
        recurring={"interval": "month"},
        metadata={"plan_type": "basic_monthly"}
    ),
    "pro_monthly": stripe.Price.create(
        product=products["pro"].id,
        unit_amount=4900,  # 49€
        currency="eur",
        recurring={"interval": "month"},
        trial_period_days=14,
        metadata={"plan_type": "pro_monthly"}
    ),
    "pro_yearly": stripe.Price.create(
        product=products["pro"].id,
        unit_amount=47040,  # 470.40€ (20% réduction)
        currency="eur",
        recurring={"interval": "year"},
        trial_period_days=14,
        metadata={"plan_type": "pro_yearly"}
    ),
    "enterprise": stripe.Price.create(
        product=products["enterprise"].id,
        unit_amount=19900,  # 199€
        currency="eur",
        recurring={"interval": "month"},
        metadata={"plan_type": "enterprise"}
    )
}

print("✅ Produits et prix Stripe créés avec succès")
```

---

## 4. Tests d'Accessibilité WCAG 2.2

### 4.1 Configuration axe-core (CI/CD)

```javascript
// backend/tests/accessibility/axe-test.js
const { AxePuppeteer } = require('@axe-core/puppeteer');
const puppeteer = require('puppeteer');

async function testAccessibility(url) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(url);
  
  const results = await new AxePuppeteer(page)
    .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
    .analyze();
  
  await browser.close();
  
  if (results.violations.length > 0) {
    console.error(`❌ ${results.violations.length} violations d'accessibilité détectées:`);
    results.violations.forEach(violation => {
      console.error(`\n- ${violation.id}: ${violation.description}`);
      console.error(`  Impact: ${violation.impact}`);
      console.error(`  Éléments affectés: ${violation.nodes.length}`);
    });
    process.exit(1);
  } else {
    console.log('✅ Aucune violation d'accessibilité détectée');
  }
}

testAccessibility('http://localhost:3000');
```

### 4.2 Intégration GitHub Actions

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  axe-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install @axe-core/puppeteer puppeteer
      
      - name: Start application
        run: |
          docker-compose up -d
          sleep 10
      
      - name: Run axe-core tests
        run: node backend/tests/accessibility/axe-test.js
      
      - name: Upload results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: accessibility-violations
          path: axe-results.json
```

---

## 5. Déploiement VPS Hostinger

### 5.1 Déblocage Réseau (Action Critique)

```bash
# ÉTAPE 1: Accéder au hPanel Hostinger
# URL: https://hpanel.hostinger.com
# Navigation: VPS > Paramètres > Firewall

# ÉTAPE 2: Ajouter les règles de firewall
# Port 80 (HTTP):  Accept, Protocol: TCP, Port: 80, Source: 0.0.0.0/0
# Port 443 (HTTPS): Accept, Protocol: TCP, Port: 443, Source: 0.0.0.0/0

# ÉTAPE 3: Vérifier depuis le VPS
ssh root@76.13.43.3

# Vérifier UFW (firewall local)
ufw status
# Doit afficher:
# 22/tcp    ALLOW   Anywhere
# 80/tcp    ALLOW   Anywhere
# 443/tcp   ALLOW   Anywhere

# Si non configuré:
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload

# ÉTAPE 4: Tester depuis l'extérieur
curl -I http://76.13.43.3
# Doit retourner HTTP/1.1 200 OK ou 301 Moved Permanently
```

### 5.2 Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - api
    networks:
      - frontend
    restart: unless-stopped

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://oceansentinel:${POSTGRES_PASSWORD}@postgres:5432/oceansentinel
      - API_JWT_SECRET=${API_JWT_SECRET}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
    depends_on:
      - postgres
      - redis
    networks:
      - frontend
      - backend
    restart: unless-stopped

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: python -m app.workers.stripe_worker
    environment:
      - DATABASE_URL=postgresql+asyncpg://oceansentinel:${POSTGRES_PASSWORD}@postgres:5432/oceansentinel
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - backend
    restart: unless-stopped

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_DB=oceansentinel
      - POSTGRES_USER=oceansentinel
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - backend
    restart: unless-stopped

  redis:
    image: redis:alpine
    networks:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  frontend:
  backend:
```

### 5.3 Script de Déploiement

```bash
# deploy.sh
#!/bin/bash

set -e

echo "🚀 Déploiement Ocean Sentinel sur VPS Hostinger"

# Variables
VPS_IP="76.13.43.3"
VPS_USER="root"

# 1. Générer les secrets
echo "📝 Génération des secrets..."
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export API_JWT_SECRET=$(openssl rand -base64 64)

# Sauvegarder dans .env
cat > .env.prod << EOF
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
API_JWT_SECRET=${API_JWT_SECRET}
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
EOF

echo "✅ Secrets générés et sauvegardés dans .env.prod"

# 2. Copier les fichiers sur le VPS
echo "📦 Copie des fichiers sur le VPS..."
rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
  ./ ${VPS_USER}@${VPS_IP}:/opt/oceansentinel/

# 3. Déployer avec Docker Compose
echo "🐳 Déploiement Docker Compose..."
ssh ${VPS_USER}@${VPS_IP} << 'ENDSSH'
cd /opt/oceansentinel
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
ENDSSH

# 4. Vérifier le déploiement
echo "✅ Vérification du déploiement..."
sleep 10
curl -f http://${VPS_IP} || echo "⚠️ Le site n'est pas encore accessible"

echo "🎉 Déploiement terminé!"
echo "📊 Vérifiez les logs: ssh ${VPS_USER}@${VPS_IP} 'docker-compose -f /opt/oceansentinel/docker-compose.prod.yml logs'"
```

---

## 6. Séquence d'Actions Immédiates

### Checklist de Déploiement

```markdown
## Phase 1: Déblocage Réseau (CRITIQUE)
- [ ] Accéder au hPanel Hostinger
- [ ] Ajouter règle firewall: Port 80 TCP Accept 0.0.0.0/0
- [ ] Ajouter règle firewall: Port 443 TCP Accept 0.0.0.0/0
- [ ] Vérifier UFW sur le VPS
- [ ] Tester: `curl -I http://76.13.43.3`

## Phase 2: Base de Données
- [ ] Copier init.sql sur le VPS
- [ ] Démarrer PostgreSQL avec pgvector
- [ ] Exécuter le schéma SQL
- [ ] Vérifier: `psql -U oceansentinel -c "\dx"` (doit afficher vector)

## Phase 3: Backend API
- [ ] Générer API_JWT_SECRET (256 bits)
- [ ] Configurer .env.prod
- [ ] Déployer FastAPI avec Docker
- [ ] Tester: `curl http://76.13.43.3/api/docs`

## Phase 4: Stripe
- [ ] Créer produits et prix (setup_stripe_products.py)
- [ ] Configurer webhook endpoint
- [ ] Tester webhook avec Stripe CLI
- [ ] Démarrer worker asynchrone

## Phase 5: Accessibilité
- [ ] Exécuter axe-core sur page d'accueil
- [ ] Corriger violations critiques
- [ ] Tester avec WAVE
- [ ] Valider navigation clavier

## Phase 6: Monitoring
- [ ] Configurer logs centralisés
- [ ] Mettre en place alertes (Sentry/Datadog)
- [ ] Vérifier métriques Stripe
- [ ] Tester Dead Letter Queue
```

---

## 7. Dead Letter Queue (DLQ) pour Stripe

### 7.1 Modèle de Données

```sql
-- Table pour événements Stripe en échec
CREATE TABLE stripe_event_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_event_id VARCHAR(255) UNIQUE NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  payload JSONB NOT NULL,
  
  -- Statut de traitement
  status VARCHAR(50) DEFAULT 'pending', -- pending, processing, processed, failed
  retry_count INTEGER DEFAULT 0,
  last_error TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  
  -- Index pour requêtes
  CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'processed', 'failed'))
);

CREATE INDEX idx_stripe_queue_status ON stripe_event_queue(status, created_at);
CREATE INDEX idx_stripe_queue_retry ON stripe_event_queue(retry_count) WHERE status = 'pending';
```

### 7.2 Dashboard de Monitoring

```python
# backend/app/routers/admin.py
@router.get("/admin/stripe/failed-events")
async def get_failed_stripe_events(
    current_user: UserInDB = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupérer les événements Stripe en échec (DLQ)
    """
    result = await db.execute(
        select(StripeEventQueue)
        .where(StripeEventQueue.status == "failed")
        .order_by(StripeEventQueue.created_at.desc())
        .limit(100)
    )
    
    failed_events = result.scalars().all()
    
    return {
        "total": len(failed_events),
        "events": [
            {
                "id": event.id,
                "stripe_event_id": event.stripe_event_id,
                "event_type": event.event_type,
                "retry_count": event.retry_count,
                "last_error": event.last_error,
                "created_at": event.created_at.isoformat()
            }
            for event in failed_events
        ]
    }

@router.post("/admin/stripe/retry-event/{event_id}")
async def retry_failed_event(
    event_id: str,
    current_user: UserInDB = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Réessayer manuellement un événement en échec
    """
    result = await db.execute(
        select(StripeEventQueue).where(StripeEventQueue.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    # Réinitialiser pour nouveau traitement
    event.status = "pending"
    event.retry_count = 0
    event.last_error = None
    
    await db.commit()
    
    return {"message": "Événement remis en queue pour traitement"}
```

---

**Document créé le** : 19 avril 2026  
**Version** : 1.0  
**Auteur** : Backend Team - Ocean Sentinel
