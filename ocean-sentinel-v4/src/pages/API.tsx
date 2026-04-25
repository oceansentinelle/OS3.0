/**
 * API Documentation Page
 * 
 * Documentation de l'API REST Ocean Sentinel
 * - Endpoints disponibles
 * - Flux de données MCP TimescaleDB
 * - Exemples de réponses
 * - Règle de Vérité SACS
 * 
 * ⚠️ AUCUNE REQUÊTE RÉSEAU (Sécurité absolue)
 */

import { Code, Database, Zap, Shield, CheckCircle } from 'lucide-react'
import { TruthBadge } from '@/components/badges/TruthBadge'

export default function API() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="bg-gradient-to-br from-ocean-950 to-ocean-900 border-b-2 border-primary">
        <div className="max-w-4xl mx-auto px-4 py-12">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-10 h-10 text-primary" />
            <h1 className="text-4xl font-bold">API REST</h1>
          </div>
          <p className="text-xl text-muted-foreground">
            Accédez aux données océanographiques temps réel via notre API professionnelle
          </p>
        </div>
      </section>
      
      {/* Architecture */}
      <section className="max-w-4xl mx-auto px-4 py-12 space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Database className="w-6 h-6 text-primary" />
          Architecture DB-First
        </h2>
        
        <div className="bg-card border-2 border-border rounded-xl p-6 space-y-4">
          <p className="text-muted-foreground">
            L'API Ocean Sentinel est connectée directement à une base de données <strong>TimescaleDB</strong> via le protocole <strong>MCP (Model Context Protocol)</strong>.
          </p>
          
          <div className="bg-ocean-900 border border-primary/30 rounded-lg p-4 font-mono text-sm">
            <div className="text-success">✓ TimescaleDB (PostgreSQL 15)</div>
            <div className="text-success">✓ Connexion MCP sécurisée</div>
            <div className="text-success">✓ Données temps réel (rafraîchissement 5 min)</div>
            <div className="text-success">✓ Stations: BARAG_PROXY, ARCACHON_EYRAC</div>
          </div>
        </div>
      </section>
      
      {/* Endpoints */}
      <section className="max-w-4xl mx-auto px-4 py-12 space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Code className="w-6 h-6 text-primary" />
          Endpoints disponibles
        </h2>
        
        {/* GET /station/{id}/latest */}
        <div className="bg-card border-2 border-border rounded-xl overflow-hidden">
          <div className="bg-ocean-900 px-6 py-4 border-b border-border">
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 bg-success text-success-dark font-bold text-sm rounded">GET</span>
              <code className="text-lg font-mono">/api/v1/station/{'{station_id}'}/latest</code>
            </div>
          </div>
          
          <div className="p-6 space-y-4">
            <p className="text-muted-foreground">
              Récupère les dernières mesures validées pour une station donnée.
            </p>
            
            <div>
              <h4 className="font-semibold mb-2">Paramètres</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex gap-2">
                  <code className="bg-ocean-900 px-2 py-1 rounded">station_id</code>
                  <span className="text-muted-foreground">: BARAG_PROXY ou ARCACHON_EYRAC</span>
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-2">Exemple de réponse</h4>
              <pre className="bg-ocean-950 border border-border rounded-lg p-4 overflow-x-auto text-xs">
{`{
  "station_id": "BARAG_PROXY",
  "timestamp": "2026-04-23T16:07:16.126231Z",
  "parameters": [
    {
      "name": "TEMP",
      "value": 18.5,
      "unit": "°C",
      "status": "measured",
      "source": "COAST-HF Ifremer",
      "timestamp": "2026-04-23T16:07:16Z",
      "quality_score": 0.95,
      "is_critical": false
    },
    {
      "name": "DOX2",
      "value": 135.0,
      "unit": "µmol/kg",
      "status": "measured",
      "source": "COAST-HF Ifremer",
      "timestamp": "2026-04-23T16:07:16Z",
      "quality_score": 0.88,
      "is_critical": true
    }
  ]
}`}
              </pre>
            </div>
          </div>
        </div>
      </section>
      
      {/* SACS Truth Badges */}
      <section className="max-w-4xl mx-auto px-4 py-12 space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Shield className="w-6 h-6 text-primary" />
          Règle de Vérité SACS
        </h2>
        
        <p className="text-muted-foreground">
          Chaque donnée est accompagnée d'un <strong>badge de fiabilité</strong> selon sa source :
        </p>
        
        <div className="space-y-4">
          {/* MESURÉ */}
          <div className="bg-card border-2 border-truth-measured rounded-xl p-6">
            <div className="flex items-center gap-3 mb-3">
              <TruthBadge status="measured" />
              <h3 className="text-lg font-bold">MESURÉ (Capteur direct)</h3>
            </div>
            <p className="text-sm text-muted-foreground mb-2">
              Données issues de capteurs physiques installés sur site (COAST-HF, Hub'Eau BRGM).
            </p>
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-truth-measured" />
              <span className="font-semibold">Fiabilité : 100%</span>
            </div>
          </div>
          
          {/* INFÉRÉ */}
          <div className="bg-card border-2 border-truth-inferred rounded-xl p-6">
            <div className="flex items-center gap-3 mb-3">
              <TruthBadge status="inferred" />
              <h3 className="text-lg font-bold">INFÉRÉ (Proxy satellitaire)</h3>
            </div>
            <p className="text-sm text-muted-foreground mb-2">
              Données estimées par télédétection satellitaire (Sentinel-3 OLCI, réflectance océanique).
            </p>
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-truth-inferred" />
              <span className="font-semibold">Fiabilité : 70-90%</span>
            </div>
          </div>
          
          {/* SIMULÉ */}
          <div className="bg-card border-2 border-truth-simulated rounded-xl p-6">
            <div className="flex items-center gap-3 mb-3">
              <TruthBadge status="simulated" />
              <h3 className="text-lg font-bold">SIMULÉ (Modèle numérique)</h3>
            </div>
            <p className="text-sm text-muted-foreground mb-2">
              Données générées par modèle numérique océanographique (MARS3D Ifremer).
            </p>
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-truth-simulated" />
              <span className="font-semibold">Fiabilité : 50-70%</span>
            </div>
          </div>
        </div>
      </section>
      
      {/* Rate Limiting */}
      <section className="max-w-4xl mx-auto px-4 py-12 space-y-6">
        <h2 className="text-2xl font-bold">Limites & Sécurité</h2>
        
        <div className="bg-card border-2 border-border rounded-xl p-6 space-y-4">
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold mb-1">Rate Limiting</h3>
              <p className="text-sm text-muted-foreground">
                100 requêtes par minute par adresse IP
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold mb-1">CORS</h3>
              <p className="text-sm text-muted-foreground">
                Accès restreint au domaine oceansentinelle.fr
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold mb-1">Graceful Degradation</h3>
              <p className="text-sm text-muted-foreground">
                En cas d'erreur, l'API retourne un message générique sans exposer de détails techniques (stack trace SQL masqué).
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
