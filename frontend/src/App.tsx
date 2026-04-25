import { useState } from 'react'
import { IntentPreview } from '../components/os/intent-preview'

function App() {
  const [showIntentPreview, setShowIntentPreview] = useState(false)

  const mockIntentData = {
    agent: 'OrchestratorAgent',
    objective: 'Ingérer données synthétiques Arcachon (température, salinité, courants)',
    sources: ['OceanSentinel-SynthNode-Arcachon', 'PostgreSQL', 'TimescaleDB'],
    duration: '~2 secondes',
    confidence: 0.95,
    impact: 'Ajout de 1 mesure océanographique dans raw_ingestion_log. Aucune modification de données existantes.',
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-900 via-ocean-deep to-neutral-800">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-12 text-center">
          <h1 className="text-h1 font-bold text-white mb-4">
            🌊 Ocean Sentinel V3.1
          </h1>
          <p className="text-xl text-neutral-200">
            Plateforme de Surveillance Océanographique avec Agentic UX
          </p>
        </header>

        <main className="max-w-4xl mx-auto">
          <div className="bg-card/80 backdrop-blur-lg rounded-lg border border-border p-8 shadow-xl">
            <h2 className="text-h2 font-semibold text-foreground mb-6">
              Test Intent Preview Component
            </h2>
            
            <button
              onClick={() => setShowIntentPreview(!showIntentPreview)}
              className="px-6 py-3 bg-brand-primary text-white rounded-lg hover:bg-brand-dark transition-colors focus-visible-ring touch-target"
            >
              {showIntentPreview ? 'Masquer' : 'Afficher'} Intent Preview
            </button>

            {showIntentPreview && (
              <div className="mt-6">
                <IntentPreview
                  agent={mockIntentData.agent}
                  objective={mockIntentData.objective}
                  sources={mockIntentData.sources}
                  duration={mockIntentData.duration}
                  confidence={mockIntentData.confidence}
                  impact={mockIntentData.impact}
                  onValidate={() => alert('✅ Intention validée')}
                  onCorrect={() => alert('✏️ Correction demandée')}
                  onInterrupt={() => alert('🛑 Agent interrompu')}
                  onDefer={() => alert('⏸️ Action différée')}
                />
              </div>
            )}
          </div>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-card/60 backdrop-blur rounded-lg p-6 border border-border">
              <div className="text-4xl mb-3">📊</div>
              <h3 className="text-h4 font-semibold text-foreground mb-2">
                Données Temps Réel
              </h3>
              <p className="text-muted-foreground">
                Température, salinité, courants marins
              </p>
            </div>

            <div className="bg-card/60 backdrop-blur rounded-lg p-6 border border-border">
              <div className="text-4xl mb-3">🚨</div>
              <h3 className="text-h4 font-semibold text-foreground mb-2">
                Alertes Écologiques
              </h3>
              <p className="text-muted-foreground">
                Détection automatique d'anomalies
              </p>
            </div>

            <div className="bg-card/60 backdrop-blur rounded-lg p-6 border border-border">
              <div className="text-4xl mb-3">🔌</div>
              <h3 className="text-h4 font-semibold text-foreground mb-2">
                API REST
              </h3>
              <p className="text-muted-foreground">
                Accès programmatique aux données
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
