/**
 * Legal Page - Mentions légales
 * 
 * Page conforme RGPD et réglementation française
 * Dernière mise à jour : 24 avril 2026
 */

import { Scale, Shield, Mail, Server, Cookie, FileText } from 'lucide-react'

export default function Legal() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-ocean-950 to-ocean-900 border-b-2 border-primary">
        <div className="max-w-7xl mx-auto px-4 py-12 md:py-16">
          <div className="text-center">
            <Scale className="w-16 h-16 mx-auto mb-4 text-primary" />
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
              Mentions Légales
            </h1>
            <p className="text-lg md:text-xl text-white/90 max-w-2xl mx-auto">
              Informations légales et réglementaires relatives à Ocean Sentinel
            </p>
            <p className="text-sm text-white/70 mt-4">
              Dernière mise à jour : 24 avril 2026
            </p>
          </div>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="prose prose-invert max-w-none space-y-12">
          
          {/* 1. Éditeur */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <FileText className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">1. Éditeur du site</h2>
            </div>
            
            <div className="space-y-4 text-muted-foreground">
              <p className="text-foreground font-semibold">
                Les sites <span className="text-primary">oceansentinelle.fr</span> et{' '}
                <span className="text-primary">ocean-sentinelle.org</span> sont édités par :
              </p>
              
              <div className="bg-primary/5 border-l-4 border-primary rounded-lg p-4">
                <p className="font-semibold text-foreground mb-2">Ocean Sentinel</p>
                <p className="text-sm">Projet de surveillance océanographique citoyenne</p>
                <p className="text-sm">Bassin d'Arcachon, Nouvelle-Aquitaine, France</p>
                <p className="text-sm mt-3">
                  <span className="font-semibold">Email :</span>{' '}
                  <a href="mailto:contact@oceansentinelle.org" className="text-primary hover:underline">
                    contact@oceansentinelle.org
                  </a>
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Administration :</span>{' '}
                  <a href="mailto:admin@oceansentinelle.fr" className="text-primary hover:underline">
                    admin@oceansentinelle.fr
                  </a>
                </p>
              </div>

              <p className="text-sm">
                Ocean Sentinel a pour objet de contribuer à la protection des océans, 
                à la sensibilisation environnementale, à l'écologie marine, à l'innovation 
                durable et à la mobilisation citoyenne à travers la collecte et la diffusion 
                de données océanographiques en temps réel.
              </p>
            </div>
          </section>

          {/* 2. Directeur de publication */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <h2 className="text-2xl font-bold mb-4">2. Directeur de publication</h2>
            <div className="text-muted-foreground space-y-2">
              <p>
                <span className="font-semibold text-foreground">Directeur de publication :</span> AZTRM-D
              </p>
              <p>
                <span className="font-semibold text-foreground">Responsable de rédaction :</span> Équipe Ocean Sentinel
              </p>
              <p className="text-sm mt-4">
                Le directeur de publication est responsable des contenus publiés sur les sites, 
                sous réserve des contenus fournis par des tiers, commentaires, contributions 
                externes ou contenus intégrés depuis des plateformes tierces.
              </p>
            </div>
          </section>

          {/* 3. Hébergement */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Server className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">3. Hébergement</h2>
            </div>
            
            <div className="text-muted-foreground space-y-3">
              <p className="text-foreground font-semibold">Les sites sont hébergés par :</p>
              
              <div className="bg-primary/5 border-l-4 border-primary rounded-lg p-4">
                <p className="font-semibold text-foreground">Hostinger International Ltd.</p>
                <p className="text-sm">61 Lordou Vironos Street, 6023 Larnaca, Chypre</p>
                <p className="text-sm mt-2">
                  <span className="font-semibold">Site web :</span>{' '}
                  <a 
                    href="https://www.hostinger.com/fr" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    www.hostinger.com
                  </a>
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Serveur VPS :</span> 76.13.43.3
                </p>
              </div>

              <p className="text-sm">
                L'hébergeur assure le stockage technique des contenus et données nécessaires 
                au fonctionnement des sites.
              </p>
            </div>
          </section>

          {/* 4. Propriété intellectuelle */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Shield className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">4. Propriété intellectuelle</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p>
                L'ensemble des éléments présents sur les sites <strong className="text-foreground">oceansentinelle.fr</strong> et{' '}
                <strong className="text-foreground">ocean-sentinelle.org</strong>, notamment les textes, logos, noms, 
                graphismes, photographies, vidéos, cartes, schémas, bases documentaires, interfaces, 
                éléments visuels, codes, contenus pédagogiques et éléments de marque, est protégé 
                par le droit de la propriété intellectuelle.
              </p>

              <p>
                Sauf mention contraire, ces éléments sont la propriété exclusive d'<strong className="text-foreground">Ocean Sentinel</strong> ou 
                font l'objet d'une autorisation d'utilisation.
              </p>

              <div className="bg-destructive/10 border-l-4 border-destructive rounded-lg p-4">
                <p className="text-sm font-semibold text-foreground mb-2">⚠️ Interdiction</p>
                <p className="text-sm">
                  Toute reproduction, représentation, modification, adaptation, extraction, 
                  réutilisation, diffusion ou exploitation totale ou partielle des contenus, 
                  sans autorisation écrite préalable, est interdite.
                </p>
              </div>

              <div className="bg-success/10 border-l-4 border-success rounded-lg p-4">
                <p className="text-sm font-semibold text-foreground mb-2">✅ Citation autorisée</p>
                <p className="text-sm">
                  Les contenus pédagogiques ou scientifiques peuvent être cités à des fins 
                  d'information, de recherche ou de sensibilisation, sous réserve de mentionner 
                  clairement la source, le nom du site et, lorsque cela est possible, un lien 
                  vers la page concernée.
                </p>
              </div>
            </div>
          </section>

          {/* 5. Données personnelles */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Shield className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">5. Données personnelles - RGPD</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p>
                Dans le cadre de l'utilisation des sites, <strong className="text-foreground">Ocean Sentinel</strong> peut 
                être amené à traiter des données personnelles.
              </p>

              <p>
                Les traitements sont réalisés conformément au <strong className="text-foreground">Règlement général 
                sur la protection des données (RGPD)</strong>, à la loi Informatique et Libertés 
                et aux recommandations de la CNIL.
              </p>

              <h3 className="text-xl font-bold text-foreground mt-6 mb-3">Données collectées</h3>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li>Nom et prénom (formulaire de contact)</li>
                <li>Adresse email (contact, newsletter)</li>
                <li>Message transmis via formulaire</li>
                <li>Données techniques : adresse IP, navigateur, terminal</li>
                <li>Préférences de cookies</li>
              </ul>

              <h3 className="text-xl font-bold text-foreground mt-6 mb-3">Finalités</h3>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li>Répondre aux demandes envoyées via les formulaires</li>
                <li>Gérer les inscriptions à la newsletter (si activée)</li>
                <li>Assurer la sécurité du site</li>
                <li>Mesurer l'audience du site</li>
                <li>Améliorer les contenus et services proposés</li>
              </ul>

              <h3 className="text-xl font-bold text-foreground mt-6 mb-3">Durées de conservation</h3>
              <div className="bg-primary/5 rounded-lg p-4">
                <table className="w-full text-sm">
                  <tbody className="divide-y divide-border">
                    <tr>
                      <td className="py-2 font-semibold">Demande de contact</td>
                      <td className="py-2">Durée nécessaire au traitement + 1 an</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-semibold">Newsletter</td>
                      <td className="py-2">Jusqu'au désabonnement</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-semibold">Logs techniques</td>
                      <td className="py-2">13 mois maximum</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-semibold">Cookies</td>
                      <td className="py-2">13 mois maximum</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h3 className="text-xl font-bold text-foreground mt-6 mb-3">Vos droits</h3>
              <p>Conformément au RGPD, vous disposez des droits suivants :</p>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li>Droit d'accès à vos données</li>
                <li>Droit de rectification</li>
                <li>Droit d'effacement</li>
                <li>Droit d'opposition</li>
                <li>Droit à la limitation du traitement</li>
                <li>Droit à la portabilité</li>
                <li>Droit de retirer votre consentement</li>
                <li>Droit d'introduire une réclamation auprès de la CNIL</li>
              </ul>

              <div className="bg-primary/10 border-l-4 border-primary rounded-lg p-4 mt-6">
                <p className="font-semibold text-foreground mb-2">📧 Exercer vos droits</p>
                <p className="text-sm">
                  Pour exercer vos droits, contactez-nous à :{' '}
                  <a href="mailto:contact@oceansentinelle.org" className="text-primary hover:underline">
                    contact@oceansentinelle.org
                  </a>
                </p>
                <p className="text-sm mt-2">
                  Une réponse vous sera apportée dans un délai de 30 jours maximum.
                </p>
              </div>
            </div>
          </section>

          {/* 6. Cookies */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Cookie className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">6. Cookies et traceurs</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p>
                Les sites peuvent utiliser des cookies ou traceurs afin d'assurer leur 
                fonctionnement, mesurer leur audience et améliorer l'expérience utilisateur.
              </p>

              <h3 className="text-xl font-bold text-foreground mt-6 mb-3">Types de cookies</h3>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li><strong>Cookies strictement nécessaires</strong> : Fonctionnement du site (exemptés de consentement)</li>
                <li><strong>Cookies de mesure d'audience</strong> : Statistiques anonymisées (si configurés conformément CNIL)</li>
                <li><strong>Cookies de préférences</strong> : Mémorisation de vos choix</li>
              </ul>

              <div className="bg-primary/10 border-l-4 border-primary rounded-lg p-4 mt-6">
                <p className="font-semibold text-foreground mb-2">🍪 Gestion des cookies</p>
                <p className="text-sm">
                  Vous pouvez accepter, refuser ou paramétrer les cookies à tout moment 
                  via les paramètres de votre navigateur.
                </p>
                <p className="text-sm mt-2">
                  Le refus de cookies peut limiter certaines fonctionnalités du site.
                </p>
              </div>
            </div>
          </section>

          {/* 7. Responsabilité */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <h2 className="text-2xl font-bold mb-4">7. Responsabilité</h2>
            <div className="text-muted-foreground space-y-4">
              <p>
                Les sites ont pour objectif de diffuser des informations relatives à la 
                protection des océans, à l'écologie marine, à la sensibilisation 
                environnementale et aux initiatives citoyennes.
              </p>

              <p>
                Les informations publiées sont fournies à titre informatif, pédagogique 
                ou documentaire. Malgré le soin apporté à leur rédaction, elles ne 
                constituent pas un avis scientifique, juridique ou technique personnalisé.
              </p>

              <div className="bg-primary/5 border-l-4 border-primary rounded-lg p-4">
                <p className="text-sm font-semibold text-foreground mb-2">
                  ⚠️ Limitation de responsabilité
                </p>
                <p className="text-sm">
                  Ocean Sentinel ne peut être tenu responsable des dommages directs ou 
                  indirects résultant de l'utilisation du site, d'erreurs ou d'omissions 
                  dans les contenus, ou d'indisponibilité temporaire du site.
                </p>
              </div>
            </div>
          </section>

          {/* 8. Liens externes */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <h2 className="text-2xl font-bold mb-4">8. Liens hypertextes</h2>
            <div className="text-muted-foreground space-y-4">
              <p>
                Les sites peuvent contenir des liens vers des sites tiers, partenaires, 
                institutions, plateformes scientifiques ou réseaux sociaux.
              </p>

              <p className="text-sm">
                Ocean Sentinel n'exerce aucun contrôle permanent sur ces sites externes 
                et ne peut être responsable de leurs contenus, pratiques ou politiques 
                de confidentialité.
              </p>
            </div>
          </section>

          {/* 9. Droit applicable */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <h2 className="text-2xl font-bold mb-4">9. Droit applicable</h2>
            <div className="text-muted-foreground space-y-4">
              <p>
                Les présentes mentions légales sont soumises au <strong className="text-foreground">droit français</strong>.
              </p>

              <p className="text-sm">
                En cas de litige, les parties rechercheront prioritairement une solution 
                amiable. À défaut, les juridictions compétentes seront déterminées 
                conformément aux règles de procédure applicables.
              </p>
            </div>
          </section>

          {/* 10. Contact */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Mail className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">10. Contact</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p>
                Pour toute question relative au site, aux contenus, aux partenariats, 
                aux données personnelles ou à l'exercice de droits :
              </p>

              <div className="bg-primary/5 rounded-lg p-4 space-y-2">
                <p className="font-semibold text-foreground">Ocean Sentinel</p>
                <p className="text-sm">
                  <strong>Email général :</strong>{' '}
                  <a href="mailto:contact@oceansentinelle.org" className="text-primary hover:underline">
                    contact@oceansentinelle.org
                  </a>
                </p>
                <p className="text-sm">
                  <strong>Email administration :</strong>{' '}
                  <a href="mailto:admin@oceansentinelle.fr" className="text-primary hover:underline">
                    admin@oceansentinelle.fr
                  </a>
                </p>
                <p className="text-sm mt-3">
                  <strong>Localisation :</strong> Bassin d'Arcachon, Nouvelle-Aquitaine, France
                </p>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  )
}
