# Architecture Portail API & Alertes - Ocean Sentinel

## 📐 Architecture Technique Complète

**Projet** : Espace Abonné "Portail API & Alertes"  
**Approche** : Dashboard-First avec séparation stricte Public/Privé  
**Conformité** : RGPD, RGAA 5.0 (WCAG 2.2 AA), ANSSI 2026, Loi Pouvoir d'Achat  
**Évolutivité** : SaaS-Ready avec RBAC et Stripe Billing  
**Date** : 19 avril 2026

---

## 1. Schéma Architectural Global

### 1.1 Structure de Routage (Séparation Public/Privé)

```
┌─────────────────────────────────────────────────────────────┐
│                    OCEAN SENTINEL                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    ZONE PUBLIQUE                             │
├─────────────────────────────────────────────────────────────┤
│  /                          → Page d'accueil                 │
│  /about                     → À propos                       │
│  /features                  → Fonctionnalités                │
│  /pricing                   → Tarifs (Free/Premium)          │
│  /docs                      → Documentation publique         │
│  /blog                      → Blog                           │
│                                                              │
│  /auth/register             → Inscription (Email/Password)   │
│  /auth/login                → Connexion                      │
│  /auth/forgot-password      → Récupération mot de passe      │
│  /auth/reset-password/:token → Réinitialisation             │
│                                                              │
│  /legal/mentions            → Mentions légales               │
│  /legal/privacy             → Politique de confidentialité   │
│  /legal/cgu                 → CGU                            │
│  /legal/accessibility       → Déclaration accessibilité      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              ZONE PRIVÉE (Authentification requise)          │
├─────────────────────────────────────────────────────────────┤
│  /portal                    → Dashboard principal            │
│  /portal/overview           → Vue d'ensemble                 │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         API & ALERTES (Section principale)          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  /portal/api                                        │   │
│  │    ├─ /keys              → Gestion clés API         │   │
│  │    ├─ /documentation     → Docs API privées         │   │
│  │    ├─ /usage             → Statistiques d'usage     │   │
│  │    └─ /webhooks          → Configuration webhooks   │   │
│  │                                                      │   │
│  │  /portal/alerts                                     │   │
│  │    ├─ /dashboard         → Tableau de bord alertes  │   │
│  │    ├─ /configure         → Configuration alertes    │   │
│  │    ├─ /history           → Historique alertes       │   │
│  │    └─ /notifications     → Préférences notifs       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  /portal/data               → Données océaniques             │
│  /portal/analytics          → Analyses et graphiques         │
│  /portal/reports            → Rapports générés              │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              PARAMÈTRES & COMPTE                    │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  /portal/settings                                   │   │
│  │    ├─ /profile           → Profil utilisateur       │   │
│  │    ├─ /security          → Sécurité (2FA, sessions) │   │
│  │    ├─ /billing           → Facturation (Stripe)     │   │
│  │    ├─ /subscription      → Gestion abonnement       │   │
│  │    ├─ /preferences       → Préférences              │   │
│  │    └─ /delete-account    → Suppression compte (3 clics)│ │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  /portal/support            → Support & Contact              │
│  /portal/changelog          → Nouveautés                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              ZONE ADMIN (Role: admin uniquement)             │
├─────────────────────────────────────────────────────────────┤
│  /admin                     → Dashboard admin                │
│  /admin/users               → Gestion utilisateurs           │
│  /admin/api-keys            → Supervision clés API           │
│  /admin/alerts              → Gestion alertes système        │
│  /admin/analytics           → Analytics globales             │
│  /admin/billing             → Gestion facturation            │
│  /admin/logs                → Logs système                   │
└─────────────────────────────────────────────────────────────┘
```

---

### 1.2 Architecture Base de Données (PostgreSQL + RBAC)

```sql
-- ============================================
-- SCHÉMA DE DONNÉES AVEC RBAC
-- ============================================

-- Table des utilisateurs
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL, -- bcrypt avec salt
  email_verified BOOLEAN DEFAULT false,
  email_verification_token VARCHAR(255),
  
  -- Métadonnées
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ,
  
  -- Sécurité
  failed_login_attempts INTEGER DEFAULT 0,
  locked_until TIMESTAMPTZ,
  two_factor_enabled BOOLEAN DEFAULT false,
  two_factor_secret VARCHAR(255),
  
  -- RGPD
  consent_given_at TIMESTAMPTZ,
  consent_ip_address INET,
  data_processing_consent BOOLEAN DEFAULT false,
  
  -- Soft delete
  deleted_at TIMESTAMPTZ,
  
  CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Index pour performance
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================
-- RBAC (Role-Based Access Control)
-- ============================================

-- Table des rôles
CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insertion des rôles de base
INSERT INTO roles (name, description) VALUES
  ('free_user', 'Utilisateur gratuit avec accès limité aux API et alertes'),
  ('premium_user', 'Utilisateur premium avec accès complet'),
  ('admin', 'Administrateur avec tous les privilèges');

-- Table de liaison utilisateurs-rôles (many-to-many)
CREATE TABLE user_roles (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
  assigned_at TIMESTAMPTZ DEFAULT NOW(),
  assigned_by UUID REFERENCES users(id),
  PRIMARY KEY (user_id, role_id)
);

-- Table des permissions
CREATE TABLE permissions (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  resource VARCHAR(50) NOT NULL, -- 'api', 'alerts', 'data', 'admin'
  action VARCHAR(50) NOT NULL,   -- 'read', 'write', 'delete', 'manage'
  description TEXT
);

-- Insertion des permissions de base
INSERT INTO permissions (name, resource, action, description) VALUES
  ('api.keys.read', 'api', 'read', 'Consulter ses clés API'),
  ('api.keys.create', 'api', 'write', 'Créer des clés API (limité pour free)'),
  ('api.keys.delete', 'api', 'delete', 'Supprimer ses clés API'),
  ('api.usage.read', 'api', 'read', 'Consulter statistiques d''usage API'),
  
  ('alerts.read', 'alerts', 'read', 'Consulter les alertes'),
  ('alerts.configure', 'alerts', 'write', 'Configurer les alertes'),
  ('alerts.manage', 'alerts', 'manage', 'Gestion avancée des alertes (premium)'),
  
  ('data.read', 'data', 'read', 'Accès aux données océaniques'),
  ('data.export', 'data', 'write', 'Export de données (premium)'),
  
  ('admin.users.manage', 'admin', 'manage', 'Gestion des utilisateurs'),
  ('admin.system.manage', 'admin', 'manage', 'Gestion système complète');

-- Table de liaison rôles-permissions
CREATE TABLE role_permissions (
  role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
  permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
  PRIMARY KEY (role_id, permission_id)
);

-- Attribution des permissions aux rôles
-- Free User
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'free_user' AND p.name IN (
  'api.keys.read', 'api.keys.create', 'api.usage.read',
  'alerts.read', 'alerts.configure', 'data.read'
);

-- Premium User (toutes les permissions sauf admin)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'premium_user' AND p.resource != 'admin';

-- Admin (toutes les permissions)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'admin';

-- ============================================
-- ABONNEMENTS (Stripe Integration Ready)
-- ============================================

CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Stripe
  stripe_customer_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255),
  stripe_price_id VARCHAR(255),
  
  -- Plan
  plan_type VARCHAR(50) NOT NULL, -- 'free', 'premium_monthly', 'premium_yearly'
  status VARCHAR(50) DEFAULT 'active', -- 'active', 'canceled', 'past_due', 'trialing'
  
  -- Dates
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  trial_end TIMESTAMPTZ,
  canceled_at TIMESTAMPTZ,
  
  -- Métadonnées
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(user_id)
);

-- Quotas par plan
CREATE TABLE subscription_quotas (
  id SERIAL PRIMARY KEY,
  plan_type VARCHAR(50) UNIQUE NOT NULL,
  
  -- Limites API
  api_calls_per_month INTEGER,
  api_keys_limit INTEGER,
  api_rate_limit_per_minute INTEGER,
  
  -- Limites Alertes
  alerts_limit INTEGER,
  alert_channels TEXT[], -- ['email', 'webhook', 'sms']
  
  -- Limites Données
  data_retention_days INTEGER,
  export_enabled BOOLEAN,
  
  -- Features
  features JSONB
);

-- Insertion des quotas
INSERT INTO subscription_quotas (plan_type, api_calls_per_month, api_keys_limit, api_rate_limit_per_minute, alerts_limit, alert_channels, data_retention_days, export_enabled, features) VALUES
  ('free', 10000, 1, 10, 3, ARRAY['email'], 30, false, '{"support": "community", "sla": null}'),
  ('premium_monthly', 1000000, 10, 100, 50, ARRAY['email', 'webhook', 'sms'], 365, true, '{"support": "priority", "sla": "99.9%", "custom_webhooks": true}'),
  ('premium_yearly', 1000000, 10, 100, 50, ARRAY['email', 'webhook', 'sms'], 365, true, '{"support": "priority", "sla": "99.9%", "custom_webhooks": true, "discount": "20%"}');

-- ============================================
-- CLÉS API
-- ============================================

CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Clé
  key_hash VARCHAR(255) NOT NULL UNIQUE, -- Hash de la clé (ne jamais stocker en clair)
  key_prefix VARCHAR(20) NOT NULL, -- Préfixe visible (ex: "os_live_abc...")
  
  -- Métadonnées
  name VARCHAR(100) NOT NULL,
  description TEXT,
  
  -- Permissions
  scopes TEXT[], -- ['read:data', 'write:alerts', etc.]
  
  -- Sécurité
  last_used_at TIMESTAMPTZ,
  last_used_ip INET,
  
  -- Statut
  is_active BOOLEAN DEFAULT true,
  expires_at TIMESTAMPTZ,
  
  -- Dates
  created_at TIMESTAMPTZ DEFAULT NOW(),
  revoked_at TIMESTAMPTZ,
  
  CONSTRAINT max_keys_per_user CHECK (
    (SELECT COUNT(*) FROM api_keys WHERE user_id = api_keys.user_id AND is_active = true) <= 10
  )
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id) WHERE is_active = true;
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);

-- ============================================
-- USAGE API (Métriques)
-- ============================================

CREATE TABLE api_usage (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
  
  -- Requête
  endpoint VARCHAR(255) NOT NULL,
  method VARCHAR(10) NOT NULL,
  status_code INTEGER,
  
  -- Métriques
  response_time_ms INTEGER,
  request_size_bytes INTEGER,
  response_size_bytes INTEGER,
  
  -- Contexte
  ip_address INET,
  user_agent TEXT,
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Hypertable TimescaleDB pour performance
SELECT create_hypertable('api_usage', 'timestamp', if_not_exists => TRUE);

-- Index pour requêtes fréquentes
CREATE INDEX idx_api_usage_user_time ON api_usage(user_id, timestamp DESC);
CREATE INDEX idx_api_usage_key_time ON api_usage(api_key_id, timestamp DESC);

-- ============================================
-- ALERTES
-- ============================================

CREATE TABLE alert_configurations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Configuration
  name VARCHAR(100) NOT NULL,
  description TEXT,
  
  -- Conditions (JSON pour flexibilité)
  conditions JSONB NOT NULL,
  -- Exemple: {"type": "threshold", "metric": "ph", "operator": "<=", "value": 7.5, "location": "arcachon"}
  
  -- Canaux de notification
  notification_channels JSONB NOT NULL,
  -- Exemple: [{"type": "email", "address": "user@example.com"}, {"type": "webhook", "url": "https://..."}]
  
  -- Statut
  is_active BOOLEAN DEFAULT true,
  
  -- Métadonnées
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_triggered_at TIMESTAMPTZ
);

CREATE INDEX idx_alerts_user_active ON alert_configurations(user_id) WHERE is_active = true;

-- Historique des alertes déclenchées
CREATE TABLE alert_history (
  id BIGSERIAL PRIMARY KEY,
  alert_config_id UUID REFERENCES alert_configurations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Déclenchement
  triggered_at TIMESTAMPTZ DEFAULT NOW(),
  trigger_value JSONB, -- Valeur qui a déclenché l'alerte
  
  -- Notification
  notification_sent BOOLEAN DEFAULT false,
  notification_channels_used JSONB,
  notification_errors JSONB,
  
  -- Statut
  acknowledged BOOLEAN DEFAULT false,
  acknowledged_at TIMESTAMPTZ,
  acknowledged_by UUID REFERENCES users(id)
);

SELECT create_hypertable('alert_history', 'triggered_at', if_not_exists => TRUE);

-- ============================================
-- SESSIONS (JWT Refresh Tokens)
-- ============================================

CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Token
  token_hash VARCHAR(255) NOT NULL UNIQUE,
  
  -- Métadonnées
  device_info JSONB, -- User-Agent, OS, Browser
  ip_address INET,
  
  -- Expiration
  expires_at TIMESTAMPTZ NOT NULL,
  
  -- Dates
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ,
  
  -- Révocation
  revoked BOOLEAN DEFAULT false,
  revoked_at TIMESTAMPTZ
);

CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id) WHERE revoked = false;
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at) WHERE revoked = false;

-- ============================================
-- LOGS D'AUDIT (RGPD Compliance)
-- ============================================

CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Action
  action VARCHAR(100) NOT NULL, -- 'user.login', 'user.register', 'api_key.created', etc.
  resource_type VARCHAR(50),
  resource_id VARCHAR(255),
  
  -- Détails
  details JSONB,
  
  -- Contexte
  ip_address INET,
  user_agent TEXT,
  
  -- Timestamp
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('audit_logs', 'timestamp', if_not_exists => TRUE);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, timestamp DESC);

-- ============================================
-- FONCTIONS UTILITAIRES
-- ============================================

-- Fonction pour vérifier les permissions
CREATE OR REPLACE FUNCTION user_has_permission(
  p_user_id UUID,
  p_permission_name VARCHAR
) RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.id
    WHERE ur.user_id = p_user_id
      AND p.name = p_permission_name
  );
END;
$$ LANGUAGE plpgsql STABLE;

-- Fonction pour obtenir les quotas d'un utilisateur
CREATE OR REPLACE FUNCTION get_user_quotas(p_user_id UUID)
RETURNS TABLE (
  api_calls_per_month INTEGER,
  api_keys_limit INTEGER,
  api_rate_limit_per_minute INTEGER,
  alerts_limit INTEGER,
  alert_channels TEXT[],
  data_retention_days INTEGER,
  export_enabled BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    sq.api_calls_per_month,
    sq.api_keys_limit,
    sq.api_rate_limit_per_minute,
    sq.alerts_limit,
    sq.alert_channels,
    sq.data_retention_days,
    sq.export_enabled
  FROM subscriptions s
  JOIN subscription_quotas sq ON s.plan_type = sq.plan_type
  WHERE s.user_id = p_user_id
    AND s.status = 'active';
END;
$$ LANGUAGE plpgsql STABLE;

-- Trigger pour updated_at automatique
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_configurations_updated_at BEFORE UPDATE ON alert_configurations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 2. Mention RGPD Exacte (Art. 13)

### Texte Juridique Complet pour Inscription

```
═══════════════════════════════════════════════════════════════
INFORMATIONS SUR LA PROTECTION DE VOS DONNÉES PERSONNELLES
(Article 13 du RGPD)
═══════════════════════════════════════════════════════════════

Responsable du traitement :
Ocean Sentinel SAS
RCS Bordeaux : XXX XXX XXX
Siège social : [Adresse complète]
Représentant légal : [Nom et fonction]
Contact : contact@oceansentinel.fr

Délégué à la Protection des Données (DPO) :
Email : dpo@oceansentinel.fr
Formulaire : https://oceansentinel.fr/contact-dpo

Finalité de la collecte :
Vos données (adresse email et mot de passe chiffré) sont collectées 
pour les finalités suivantes :
• Création et gestion de votre compte utilisateur
• Génération et gestion de vos clés d'accès API
• Configuration et envoi d'alertes océanographiques personnalisées
• Suivi de votre consommation API (facturation pour abonnés payants)
• Amélioration de nos services

Base légale du traitement :
• Consentement explicite (Art. 6.1.a du RGPD) pour l'inscription
• Exécution du contrat (Art. 6.1.b) pour la fourniture des services API
• Intérêt légitime (Art. 6.1.f) pour la sécurité et la prévention de la fraude

Données collectées :
• Données d'identification : adresse email
• Données de connexion : mot de passe (chiffré bcrypt), adresse IP, 
  horodatage des connexions
• Données d'usage : statistiques d'utilisation de l'API, historique 
  des alertes
• Données de paiement : gérées exclusivement par notre prestataire 
  Stripe (certifié PCI-DSS), nous ne stockons aucune donnée bancaire

Destinataires des données :
Vos données sont strictement réservées à un usage interne. Elles 
peuvent être partagées avec :
• Nos sous-traitants techniques (hébergement : Hostinger, paiement : 
  Stripe) sous contrat de confidentialité et garanties RGPD
• Autorités légales sur réquisition judiciaire

Aucune vente, location ou partage à des tiers commerciaux.

Transferts hors Union Européenne :
Les données sont hébergées dans l'UE (Hostinger - Pays-Bas).
Pour Stripe (USA), des clauses contractuelles types (CCT) approuvées 
par la Commission Européenne garantissent un niveau de protection adéquat.

Durée de conservation :
• Compte actif : durée de vie du compte
• Après suppression de compte : 30 jours maximum (obligations légales 
  de traçabilité), puis effacement définitif
• Logs de sécurité : 12 mois (conformité ANSSI)
• Données de facturation : 10 ans (obligation comptable française)

Vos droits (RGPD et Loi Informatique et Libertés) :
Vous disposez à tout moment des droits suivants :

✓ Droit d'accès (Art. 15) : obtenir une copie de vos données
✓ Droit de rectification (Art. 16) : corriger des données inexactes
✓ Droit à l'effacement / "droit à l'oubli" (Art. 17) : supprimer vos 
  données (procédure "3 clics" dans Paramètres > Supprimer mon compte)
✓ Droit de limitation du traitement (Art. 18)
✓ Droit à la portabilité (Art. 20) : récupérer vos données dans un 
  format structuré (JSON/CSV)
✓ Droit de retrait du consentement (Art. 7.3) : à tout moment, sans 
  affecter la licéité du traitement antérieur
✓ Droit d'opposition (Art. 21) : vous opposer au traitement pour des 
  motifs légitimes
✓ Droit de définir des directives post-mortem (Art. 85 Loi IL)

Pour exercer ces droits :
• Email DPO : dpo@oceansentinel.fr (réponse sous 1 mois, extensible 
  à 3 mois si complexe avec notification)
• Formulaire sécurisé : https://oceansentinel.fr/contact-dpo
• Courrier : Ocean Sentinel - DPO, [Adresse postale complète]

Une pièce d'identité pourra être demandée pour vérifier votre identité.

Droit de réclamation auprès de l'autorité de contrôle :
Si vous estimez que vos droits ne sont pas respectés, vous pouvez 
introduire une réclamation auprès de la CNIL :
• En ligne : https://www.cnil.fr/fr/plaintes
• Par courrier : CNIL, 3 Place de Fontenoy, TSA 80715, 
  75334 PARIS CEDEX 07

Prise de décision automatisée :
Aucune décision produisant des effets juridiques vous concernant 
n'est prise sur le seul fondement d'un traitement automatisé.

Sécurité des données :
Nous mettons en œuvre les mesures techniques et organisationnelles 
appropriées conformément aux recommandations de l'ANSSI 2026 :
• Chiffrement SSL/TLS 1.3 pour toutes les communications
• Hachage des mots de passe (bcrypt, facteur 12)
• Authentification à deux facteurs (2FA) disponible
• Surveillance et détection des intrusions
• Sauvegardes chiffrées quotidiennes
• Audits de sécurité réguliers

Obligation de notification :
En cas de violation de données susceptible d'engendrer un risque 
élevé pour vos droits et libertés, nous vous en informerons dans 
les 72 heures conformément à l'Art. 34 du RGPD.

Consentement :
En cochant la case ci-dessus et en cliquant sur "Créer mon compte", 
vous reconnaissez avoir pris connaissance de ces informations et 
consentez au traitement de vos données personnelles dans les 
conditions décrites.

Dernière mise à jour : 19 avril 2026
Version : 2.0
```

---

## 3. Sécurité - Recommandations ANSSI 2026

### 3.1 Politique de Mots de Passe

```javascript
// Validation conforme ANSSI 2026
const PASSWORD_POLICY = {
  minLength: 12,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
  specialChars: '!@#$%^&*()_+-=[]{}|;:,.<>?',
  
  // Interdictions
  forbiddenPatterns: [
    /^(.)\1+$/, // Caractères répétés
    /^(012|123|234|345|456|567|678|789|890)+/, // Suites numériques
    /^(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)+/i, // Suites alphabétiques
  ],
  
  // Liste noire (mots de passe communs)
  blacklist: [
    'password', 'motdepasse', '123456', 'azerty', 'qwerty',
    'admin', 'root', 'user', 'ocean', 'sentinel'
  ],
  
  // Vérification contre fuite (Have I Been Pwned API)
  checkPwnedPasswords: true,
  
  // Expiration (recommandation : pas d'expiration forcée si fort)
  expirationDays: null,
  
  // Historique (empêcher réutilisation des 5 derniers)
  historyCount: 5
};
```

### 3.2 JWT Configuration

```javascript
const JWT_CONFIG = {
  // Access Token (courte durée)
  accessToken: {
    secret: process.env.JWT_ACCESS_SECRET, // 256 bits minimum
    algorithm: 'HS256',
    expiresIn: '15m', // 15 minutes
    issuer: 'oceansentinel.fr',
    audience: 'oceansentinel-api'
  },
  
  // Refresh Token (longue durée, stocké en DB)
  refreshToken: {
    secret: process.env.JWT_REFRESH_SECRET, // Différent de l'access
    algorithm: 'HS256',
    expiresIn: '7d', // 7 jours
    issuer: 'oceansentinel.fr',
    audience: 'oceansentinel-api'
  },
  
  // Rotation des tokens
  rotateRefreshToken: true, // Nouveau refresh token à chaque utilisation
  
  // Révocation
  useTokenBlacklist: true // Redis pour tokens révoqués
};
```

---

## 4. Plan de Navigation Détaillé

### 4.1 Dashboard Principal (/portal)

```
┌────────────────────────────────────────────────────────────────┐
│  [Logo] Ocean Sentinel Portal          [👤 User] [🔔] [⚙️]    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Bienvenue, user@example.com                             │ │
│  │  Plan actuel : Free (Passer à Premium)                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐│
│  │  📊 API Usage   │  │  🔔 Alertes     │  │  📈 Données    ││
│  │  8,234 / 10,000 │  │  2 actives      │  │  Dernière MAJ  ││
│  │  calls ce mois  │  │  1 déclenchée   │  │  Il y a 5 min  ││
│  └─────────────────┘  └─────────────────┘  └────────────────┘│
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  🔑 Mes Clés API                          [+ Nouvelle]   │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │  Production Key      os_live_abc***  Créée il y a 2j    │ │
│  │  Development Key     os_test_xyz***  Créée il y a 5j    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  📬 Alertes Récentes                                     │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │  ⚠️  pH < 7.5 détecté - Bassin d'Arcachon  Il y a 2h   │ │
│  │  ✓  Température normale - Zone A         Il y a 6h     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 Section API & Alertes

#### Gestion des Clés API (/portal/api/keys)

```
┌────────────────────────────────────────────────────────────────┐
│  Gestion des Clés API                                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Quota : 1 / 1 clé utilisée (Plan Free)                       │
│  [Passer à Premium pour 10 clés]                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Production Key                                          │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │  os_live_abc123def456ghi789jkl012mno345pqr678      │ │ │
│  │  │  [📋 Copier]  [👁️ Afficher]  [🗑️ Révoquer]        │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  │                                                          │ │
│  │  Créée le : 17 avril 2026 à 14:32                       │ │
│  │  Dernière utilisation : Il y a 3 heures                 │ │
│  │  Permissions : read:data, write:alerts                  │ │
│  │  Expiration : Aucune                                     │ │
│  │                                                          │ │
│  │  📊 Statistiques (30 derniers jours)                    │ │
│  │  • Requêtes : 8,234                                      │ │
│  │  • Taux de succès : 99.2%                                │ │
│  │  • Temps de réponse moyen : 124ms                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [+ Créer une nouvelle clé API] (Désactivé - Limite atteinte) │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

#### Configuration des Alertes (/portal/alerts/configure)

```
┌────────────────────────────────────────────────────────────────┐
│  Configuration des Alertes                                     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Quota : 2 / 3 alertes configurées (Plan Free)                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Alerte pH Critique - Arcachon              [✓ Active]  │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │  Condition : pH <= 7.5                             │ │ │
│  │  │  Zone : Bassin d'Arcachon                          │ │ │
│  │  │  Notifications : 📧 Email                          │ │ │
│  │  │  Dernière alerte : Il y a 2 heures                 │ │ │
│  │  │  [✏️ Modifier]  [🗑️ Supprimer]                    │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Température Anormale - Zone A              [✓ Active]  │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │  Condition : Température > 25°C                    │ │ │
│  │  │  Zone : Zone A                                      │ │ │
│  │  │  Notifications : 📧 Email                          │ │ │
│  │  │  Dernière alerte : Jamais déclenchée               │ │ │
│  │  │  [✏️ Modifier]  [🗑️ Supprimer]                    │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [+ Créer une nouvelle alerte]                                │
│                                                                 │
│  💡 Passez à Premium pour :                                   │
│  • 50 alertes simultanées                                      │
│  • Notifications par Webhook et SMS                            │
│  • Alertes complexes multi-critères                            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 5. Livrables - Code HTML/CSS/JS

Les fichiers de code seront créés séparément pour respecter la limite de tokens.

### Structure des fichiers à créer :

1. `/frontend/auth/register.html` - Formulaire d'inscription
2. `/frontend/auth/login.html` - Formulaire de connexion
3. `/frontend/portal/dashboard.html` - Dashboard principal
4. `/frontend/portal/api-keys.html` - Gestion clés API
5. `/frontend/portal/alerts.html` - Configuration alertes
6. `/frontend/portal/settings-delete.html` - Suppression compte (3 clics)
7. `/frontend/assets/css/portal.css` - Styles globaux
8. `/frontend/assets/js/auth.js` - Logique authentification
9. `/frontend/assets/js/portal.js` - Logique dashboard

---

## 6. Checklist de Conformité

### ✅ RGAA 5.0 / WCAG 2.2 AA

- [ ] Contraste minimum 4.5:1 (texte normal)
- [ ] Contraste minimum 3:1 (texte large >18pt)
- [ ] Navigation clavier complète (Tab, Shift+Tab, Enter, Espace)
- [ ] Focus visible sur tous les éléments interactifs
- [ ] Labels ARIA complets (aria-label, aria-describedby, aria-required)
- [ ] Rôles ARIA appropriés (role="navigation", "main", "alert")
- [ ] Messages d'erreur avec aria-live="polite" ou "assertive"
- [ ] Alternatives textuelles pour images (alt)
- [ ] Structure sémantique HTML5 (header, nav, main, section, footer)
- [ ] Responsive design (mobile-first)
- [ ] Zoom jusqu'à 200% sans perte de fonctionnalité

### ✅ RGPD

- [ ] Minimisation des données (email + password uniquement)
- [ ] Consentement explicite (checkbox non pré-cochée)
- [ ] Mention Art. 13 complète sous le formulaire
- [ ] Identification du responsable de traitement
- [ ] Contact DPO accessible
- [ ] Droits de l'utilisateur expliqués
- [ ] Durée de conservation spécifiée
- [ ] Procédure de suppression de compte (3 clics)
- [ ] Logs d'audit pour traçabilité
- [ ] Chiffrement des données sensibles

### ✅ Sécurité ANSSI 2026

- [ ] HTTPS/TLS 1.3 obligatoire
- [ ] Mots de passe : bcrypt (facteur 12 minimum)
- [ ] Politique de mots de passe : 12+ caractères, complexité
- [ ] JWT avec rotation des refresh tokens
- [ ] Rate limiting sur endpoints sensibles
- [ ] Protection CSRF
- [ ] Headers de sécurité (CSP, HSTS, X-Frame-Options)
- [ ] 2FA disponible
- [ ] Détection de tentatives de connexion suspectes
- [ ] Logs de sécurité (12 mois)

### ✅ Loi Pouvoir d'Achat (Résiliation 3 clics)

- [ ] Clic 1 : Bouton visible dans Paramètres
- [ ] Clic 2 : Récapitulatif des conséquences
- [ ] Clic 3 : Confirmation finale
- [ ] Gratuité totale
- [ ] Pas de labyrinthe ou dark patterns
- [ ] Délai d'effacement : 30 jours maximum

---

**Document créé le** : 19 avril 2026  
**Version** : 1.0  
**Auteur** : Architecture Team - Ocean Sentinel
