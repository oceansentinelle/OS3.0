/**
 * About Page - Le Projet Ocean Sentinel
 * Intelligence Environnementale OSINT v1.2
 */

import { Shield, Satellite, Map, Database, Radio, AlertTriangle } from 'lucide-react'

export default function About() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="bg-gradient-to-br from-ocean-950 via-ocean-900 to-ocean-800 border-b-2 border-primary">
        <div className="max-w-4xl mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold mb-4">Le Projet Ocean Sentinel</h1>
          <p className="text-xl text-primary mb-2">
            Intelligence Environnementale OSINT v1.2
          </p>
          <p className="text-lg text-muted-foreground">
            Système d'Alerte Conchylicole Sentinelle (SACS)
          </p>
        </div>
      </section>
      
      {/* L'Essentiel */}
      <section className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-card border-2 border-primary rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Shield className="w-6 h-6 text-primary" />
            L'Essentiel
          </h2>
          <p className="text-muted-foreground leading-relaxed mb-4">
            Le projet <strong className="text-foreground">Ocean Sentinel</strong> est une plateforme de <strong className="text-primary">renseignement opérationnel</strong> fondée sur l'<strong className="text-primary">OSINT environnementale</strong> (Open Source Intelligence).
          </p>
          <p className="text-muted-foreground leading-relaxed mb-4">
            En s'appuyant exclusivement sur des <strong className="text-foreground">données légales et publiques</strong>, le projet transforme des flux massifs (satellites, modèles météo, données citoyennes) en informations stratégiques pour la protection des territoires littoraux.
          </p>
          <div className="bg-critical/10 border-2 border-critical rounded-lg p-4 mt-4">
            <p className="text-sm font-semibold text-critical mb-2 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Contexte Critique 2024
            </p>
            <p className="text-sm text-muted-foreground">
              Face à l'effondrement du naissain (<strong className="text-critical">76,6 % de mortalité en 2024</strong>), cette approche open source assure une transparence totale et une traçabilité des preuves via la méthode <strong className="text-foreground">ABACODE 2.0</strong>.
            </p>
          </div>
        </div>

        {/* IMINT */}
        <div className="bg-card border-2 border-border rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Satellite className="w-6 h-6 text-primary" />
            IMINT - Intelligence de l'Imagerie
          </h2>
          <p className="text-muted-foreground mb-4">
            L'IMINT repose sur le programme européen <strong className="text-foreground">Copernicus</strong> pour surveiller les phénomènes critiques :
          </p>
          <div className="space-y-4">
            <div className="bg-background rounded-lg p-4 border border-border">
              <h3 className="font-semibold text-primary mb-2">Sentinel-1 (SAR)</h3>
              <p className="text-sm text-muted-foreground">
                Détection des navires illégaux et des marées noires, même sous couverture nuageuse.
              </p>
            </div>
            <div className="bg-background rounded-lg p-4 border border-border">
              <h3 className="font-semibold text-primary mb-2">Sentinel-2, 3 & 5P</h3>
              <p className="text-sm text-muted-foreground">
                Monitoring de la qualité des eaux (chlorophylle-a, turbidité) et des pollutions atmosphériques. 
                L'algorithme <code className="text-xs bg-ocean-900 px-1 py-0.5 rounded">Sen2Cor (Niveau-2A)</code> permet d'isoler les signatures optiques avec une précision de <strong className="text-success">85 % (R² = 0.853)</strong>.
              </p>
            </div>
          </div>
        </div>

        {/* GEOINT */}
        <div className="bg-card border-2 border-border rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Map className="w-6 h-6 text-primary" />
            GEOINT - Intelligence Géospatiale
          </h2>
          <p className="text-muted-foreground mb-4">
            La puissance du GEOINT réside dans la superposition des phénomènes physiques et de l'activité humaine :
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-background rounded-lg p-4 border border-border">
              <h3 className="font-semibold text-primary mb-2">Modèles Physiques</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Flux de houle NOAA (WaveWatch 3)</li>
                <li>• Modèle Litto3D (IGN/SHOM/Ifremer)</li>
                <li>• Expertise Cerema</li>
              </ul>
            </div>
            <div className="bg-background rounded-lg p-4 border border-border">
              <h3 className="font-semibold text-primary mb-2">Dimension Humaine</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Données INSEE (socio-démographie)</li>
                <li>• OpenStreetMap (infrastructures)</li>
                <li>• Identification zones vulnérables</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Preuves OSINT 2024-2025 */}
        <div className="bg-card border-2 border-critical rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Database className="w-6 h-6 text-critical" />
            Acidification et Mortalité : Preuves OSINT 2024-2025
          </h2>
          <p className="text-muted-foreground mb-6">
            L'OSINT permet de documenter "l'invisibilité" de l'acidification. En 2024, le pH des eaux est tombé à <strong className="text-critical">8,04</strong>, provoquant une hausse de l'acidité de <strong className="text-critical">30 % depuis l'ère industrielle</strong>.
          </p>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 px-4 font-semibold">Indicateur OSINT</th>
                  <th className="text-left py-2 px-4 font-semibold">Source</th>
                  <th className="text-left py-2 px-4 font-semibold">Valeur / Application</th>
                </tr>
              </thead>
              <tbody className="text-muted-foreground">
                <tr className="border-b border-border/50">
                  <td className="py-2 px-4">pH Océanique 2024</td>
                  <td className="py-2 px-4">CMEMS / EEA</td>
                  <td className="py-2 px-4 text-critical font-semibold">8,04 (Baisse de 0,07 vs 1985)</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-2 px-4">Mortalité Naissain</td>
                  <td className="py-2 px-4">CAPENA</td>
                  <td className="py-2 px-4 text-critical font-semibold">76,6 % (Alerte rouge SSEM)</td>
                </tr>
                <tr className="border-b border-border/50">
                  <td className="py-2 px-4">Pertes Collecteurs</td>
                  <td className="py-2 px-4">CODEPPI</td>
                  <td className="py-2 px-4 text-critical font-semibold">44 % à l'été 2025</td>
                </tr>
                <tr>
                  <td className="py-2 px-4">Ω<sub>Arag</sub> Trend</td>
                  <td className="py-2 px-4">McGovern et al.</td>
                  <td className="py-2 px-4 text-critical font-semibold">-0,0100 à -0,0145 / an</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Gouvernance Open Source */}
        <div className="bg-card border-2 border-success rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Shield className="w-6 h-6 text-success" />
            Gouvernance Open Source et ABACODE 2.0
          </h2>
          <p className="text-muted-foreground mb-4">
            Le projet est <strong className="text-success">Open Source</strong> pour garantir la souveraineté et l'auditabilité. 
            La méthode <strong className="text-foreground">ABACODE 2.0</strong> impose une rigueur de traçabilité (Source/Date/Méthode) sur chaque point de donnée.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-background rounded-lg p-4 border border-border">
              <h3 className="font-semibold text-success mb-2">Architecture</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• PostgreSQL + pgvector (IA)</li>
                <li>• VPS durcis (Checklist Hardening)</li>
                <li>• TimescaleDB (séries temporelles)</li>
              </ul>
            </div>
            <div className="bg-background rounded-lg p-4 border border-border">
              <h3 className="font-semibold text-success mb-2">Validation</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Cycle "Human-AI-Human"</li>
                <li>• Traçabilité ABACODE 2.0</li>
                <li>• Audit public continu</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Validation et Tests ABACODE 2.0 */}
        <div className="bg-card border-2 border-primary rounded-xl p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Shield className="w-6 h-6 text-primary" />
            Validation et Tests ABACODE 2.0
          </h2>
          <p className="text-muted-foreground mb-6">
            La cohérence de la méthode <strong className="text-foreground">ABACODE 2.0</strong> ne repose pas sur une théorie abstraite, mais sur un <strong className="text-primary">cycle de validation rigoureux</strong> et des environnements de test dédiés qui garantissent la fiabilité du renseignement environnemental.
          </p>

          <div className="space-y-4">
            {/* Validation Statistique */}
            <div className="bg-background rounded-lg p-5 border-l-4 border-success">
              <h3 className="font-semibold text-success mb-2 flex items-center gap-2">
                <span className="bg-success/20 text-success px-2 py-1 rounded text-xs font-bold">95%+</span>
                Validation Statistique et Fractale
              </h3>
              <p className="text-sm text-muted-foreground">
                Le cœur algorithmique a été soumis à des tests de détection de motifs (niveaux 1 et 2) atteignant un <strong className="text-success">taux de succès supérieur à 95 %</strong> sur des jeux de données tests. Le module de base (PRNG PCG64) a été validé par 3 à 5 tests statistiques rigoureux dès les premières phases de développement.
              </p>
            </div>

            {/* Laboratoire CARL */}
            <div className="bg-background rounded-lg p-5 border-l-4 border-primary">
              <h3 className="font-semibold text-primary mb-2">
                Laboratoire de Recherche Appliquée (CARL)
              </h3>
              <p className="text-sm text-muted-foreground">
                Le système utilise un environnement de laboratoire spécifique (<strong className="text-foreground">Cybersecurity Applied Research Lab - CARL</strong>) conçu pour recréer les environnements clients et évaluer les solutions avant tout déploiement opérationnel.
              </p>
            </div>

            {/* Cycle Human-AI-Human */}
            <div className="bg-background rounded-lg p-5 border-l-4 border-warning">
              <h3 className="font-semibold text-warning mb-2">
                Cycle "Human-AI-Human"
              </h3>
              <p className="text-sm text-muted-foreground">
                Pour éviter toute dérive ou hallucination, la méthode impose une <strong className="text-foreground">validation humaine systématique</strong> pour chaque publication ou changement d'impact majeur. Ce protocole agit comme un test qualitatif continu, garantissant que les sorties de l'IA restent alignées avec l'expertise métier.
              </p>
            </div>

            {/* Audit Readiness */}
            <div className="bg-background rounded-lg p-5 border-l-4 border-primary">
              <h3 className="font-semibold text-primary mb-2">
                Preuve par l'Usage (Audit Readiness)
              </h3>
              <p className="text-sm text-muted-foreground">
                La méthode est conçue pour maintenir un état de <strong className="text-foreground">"conformité continue"</strong>. Elle connecte la gouvernance et la sécurité pour simplifier la préparation aux audits, transformant la surveillance en temps réel en une preuve factuelle irréfutable.
              </p>
            </div>

            {/* Application Terrain 2024-2025 */}
            <div className="bg-background rounded-lg p-5 border-l-4 border-critical">
              <h3 className="font-semibold text-critical mb-2 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Application Terrain 2024-2025
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                Le système est actuellement éprouvé par le traitement des données de <strong className="text-critical">mortalité exceptionnelles du Bassin d'Arcachon (76,6 % sur les naissains en 2024)</strong>. Ce déploiement en conditions de crise réelle constitue le test de résilience le plus exigeant pour les algorithmes de corrélation entre pH, température et viabilité biologique.
              </p>
              <div className="bg-critical/10 rounded p-3 mt-2">
                <p className="text-xs text-muted-foreground">
                  L'intégration de la <strong className="text-foreground">surveillance 24/7</strong> et des rapports de traçabilité automatisés garantit que chaque recommandation n'est pas seulement une simulation, mais un résultat vérifié par des protocoles de contrôle éprouvés.
                </p>
              </div>
            </div>
          </div>

          {/* Métriques de Validation */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-success/10 border border-success rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-success mb-1">&gt;95%</div>
              <div className="text-xs text-muted-foreground">Taux de succès tests</div>
            </div>
            <div className="bg-primary/10 border border-primary rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-primary mb-1">24/7</div>
              <div className="text-xs text-muted-foreground">Surveillance continue</div>
            </div>
            <div className="bg-warning/10 border border-warning rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-warning mb-1">100%</div>
              <div className="text-xs text-muted-foreground">Validation humaine</div>
            </div>
          </div>
        </div>

        {/* Podcast OSINT */}
        <div className="bg-card border-2 border-border rounded-xl p-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Radio className="w-6 h-6 text-primary" />
            Stratégie de Médiation : Le Podcast OSINT (60 min)
          </h2>
          <p className="text-muted-foreground mb-6">
            Le podcast audio est conçu comme une restitution du renseignement environnemental au public.
          </p>
          
          <div className="space-y-3">
            {[
              { seq: '01', titre: 'Introduction', duree: '5 min', objectif: 'Cadrer l\'urgence SSEM (Mortalité 2024/25)', son: 'Sons d\'ambiance de port' },
              { seq: '02', titre: 'Le Grand Angle', duree: '15 min', objectif: 'IMINT : Sentinel-2 et thermodynamique pH', son: 'Interview expert Ifremer' },
              { seq: '03', titre: 'Voix du Terrain', duree: '15 min', objectif: 'GEOINT : Risques littoraux et vulnérabilité sociale', son: 'Reportage Litto3D' },
              { seq: '04', titre: 'Le Labo IA', duree: '10 min', objectif: 'Transparence Open Source et ABACODE 2.0', son: 'Chronique rythmée' },
              { seq: '05', titre: 'Table Ronde', duree: '10 min', objectif: 'Stratégies 2050 et planification urbaine', son: 'Dialogue décideurs' },
              { seq: '06', titre: 'Conclusion', duree: '5 min', objectif: 'Synthèse et appel à l\'action', son: 'Signature sonore' },
            ].map((episode) => (
              <div key={episode.seq} className="bg-background rounded-lg p-4 border border-border">
                <div className="flex items-start gap-4">
                  <div className="bg-primary/20 text-primary font-bold text-sm px-3 py-1 rounded-lg">
                    {episode.seq}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold mb-1">{episode.titre} <span className="text-muted-foreground text-sm">({episode.duree})</span></h3>
                    <p className="text-sm text-muted-foreground mb-1">{episode.objectif}</p>
                    <p className="text-xs text-muted-foreground italic">{episode.son}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
