/**
 * Privacy Policy Page - Politique de confidentialité
 * 
 * Page conforme RGPD et recommandations CNIL
 * Dernière mise à jour : 24 avril 2026
 */

import { Shield, Lock, Eye, Cookie, Users, FileText, Mail, AlertCircle } from 'lucide-react'

export default function Privacy() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-ocean-950 to-ocean-900 border-b-2 border-primary">
        <div className="max-w-7xl mx-auto px-4 py-12 md:py-16">
          <div className="text-center">
            <Shield className="w-16 h-16 mx-auto mb-4 text-primary" />
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
              Politique de Confidentialité
            </h1>
            <p className="text-lg md:text-xl text-white/90 max-w-2xl mx-auto">
              Protection de vos données personnelles et respect de votre vie privée
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
          
          {/* Introduction */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <h2 className="text-2xl font-bold mb-4">Introduction</h2>
            <div className="text-muted-foreground space-y-4">
              <p>
                <strong className="text-foreground">Ocean Sentinel</strong> accorde une importance 
                majeure à la protection de la vie privée et des données personnelles des personnes 
                qui consultent ses sites, participent à ses actions, s'inscrivent à ses communications 
                ou prennent contact avec son équipe.
              </p>

              <p>
                Cette politique explique de manière claire quelles données personnelles peuvent être 
                collectées, pourquoi elles sont utilisées, pendant combien de temps elles sont conservées, 
                à qui elles peuvent être transmises et quels sont vos droits.
              </p>

              <div className="bg-primary/10 border-l-4 border-primary rounded-lg p-4 mt-6">
                <p className="text-sm font-semibold text-foreground mb-2">🔒 Notre engagement</p>
                <p className="text-sm">
                  Collecter uniquement les données nécessaires, les utiliser pour des finalités 
                  légitimes et les protéger sérieusement.
                </p>
              </div>
            </div>
          </section>

          {/* 1. Responsable du traitement */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Users className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">1. Responsable du traitement</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p className="text-foreground font-semibold">
                Le responsable du traitement des données personnelles est :
              </p>
              
              <div className="bg-primary/5 border-l-4 border-primary rounded-lg p-4">
                <p className="font-semibold text-foreground mb-2">Ocean Sentinel</p>
                <p className="text-sm">Projet de surveillance océanographique citoyenne</p>
                <p className="text-sm">Bassin d'Arcachon, Nouvelle-Aquitaine, France</p>
                <p className="text-sm mt-3">
                  <span className="font-semibold">Email RGPD :</span>{' '}
                  <a href="mailto:contact@oceansentinelle.org" className="text-primary hover:underline">
                    contact@oceansentinelle.org
                  </a>
                </p>
              </div>

              <p className="text-sm">
                Le responsable du traitement détermine les finalités et les moyens des traitements 
                de données personnelles réalisés dans le cadre des sites oceansentinelle.fr et 
                ocean-sentinelle.org.
              </p>
            </div>
          </section>

          {/* 2. Données collectées */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <FileText className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">2. Données personnelles collectées</h2>
            </div>
            
            <div className="text-muted-foreground space-y-6">
              <p>
                Ocean Sentinel peut collecter différentes catégories de données selon l'usage du site.
              </p>

              <div className="space-y-4">
                <div className="bg-primary/5 rounded-lg p-4">
                  <h3 className="text-lg font-bold text-foreground mb-2">📝 Données d'identification</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Nom et prénom</li>
                    <li>Organisme représenté (si applicable)</li>
                    <li>Fonction</li>
                  </ul>
                </div>

                <div className="bg-primary/5 rounded-lg p-4">
                  <h3 className="text-lg font-bold text-foreground mb-2">📧 Données de contact</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Adresse email</li>
                    <li>Numéro de téléphone (si fourni)</li>
                  </ul>
                </div>

                <div className="bg-primary/5 rounded-lg p-4">
                  <h3 className="text-lg font-bold text-foreground mb-2">💬 Données transmises volontairement</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Contenu des messages via formulaire</li>
                    <li>Demandes de partenariat</li>
                    <li>Propositions de contribution</li>
                  </ul>
                </div>

                <div className="bg-primary/5 rounded-lg p-4">
                  <h3 className="text-lg font-bold text-foreground mb-2">📊 Données techniques</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Adresse IP</li>
                    <li>Type de navigateur</li>
                    <li>Pages consultées</li>
                    <li>Date et heure de connexion</li>
                    <li>Préférences cookies</li>
                  </ul>
                </div>
              </div>

              <div className="bg-success/10 border-l-4 border-success rounded-lg p-4">
                <p className="text-sm font-semibold text-foreground mb-2">✅ Ce que nous ne faisons pas</p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Nous ne vendons pas vos données personnelles</li>
                  <li>Nous ne demandons jamais vos coordonnées bancaires par email</li>
                  <li>Nous ne vous inscrivons pas à une newsletter sans consentement</li>
                </ul>
              </div>
            </div>
          </section>

          {/* 3. Finalités */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Eye className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">3. Finalités du traitement</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p>Les données personnelles peuvent être utilisées pour :</p>

              <div className="bg-primary/5 rounded-lg p-4">
                <table className="w-full text-sm">
                  <tbody className="divide-y divide-border">
                    <tr>
                      <td className="py-3 font-semibold">Réponse aux demandes</td>
                      <td className="py-3">Répondre aux messages envoyés via formulaire</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Newsletter</td>
                      <td className="py-3">Envoyer des informations sur nos actions (avec consentement)</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Statistiques</td>
                      <td className="py-3">Mesurer l'audience et améliorer les contenus</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Sécurité</td>
                      <td className="py-3">Prévenir les abus, fraudes et usages non autorisés</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Obligations légales</td>
                      <td className="py-3">Respecter les obligations réglementaires</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* 4. Bases légales */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <h2 className="text-2xl font-bold mb-4">4. Bases légales du traitement</h2>
            <div className="text-muted-foreground space-y-4">
              <p>Chaque traitement repose sur une base légale prévue par le RGPD :</p>

              <div className="bg-primary/5 rounded-lg p-4">
                <table className="w-full text-sm">
                  <tbody className="divide-y divide-border">
                    <tr>
                      <td className="py-3 font-semibold">Formulaire de contact</td>
                      <td className="py-3">Intérêt légitime à répondre aux demandes</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Newsletter</td>
                      <td className="py-3">Consentement</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Cookies non essentiels</td>
                      <td className="py-3">Consentement</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Sécurité du site</td>
                      <td className="py-3">Intérêt légitime</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <p className="text-sm">
                Le consentement peut être retiré à tout moment, sans remettre en cause la licéité 
                des traitements réalisés avant son retrait.
              </p>
            </div>
          </section>

          {/* 5. Durées de conservation */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <h2 className="text-2xl font-bold mb-4">5. Durées de conservation</h2>
            <div className="text-muted-foreground space-y-4">
              <p>
                Les données sont conservées uniquement pendant la durée nécessaire à la finalité 
                poursuivie, sauf obligation légale imposant une durée plus longue.
              </p>

              <div className="bg-primary/5 rounded-lg p-4">
                <table className="w-full text-sm">
                  <tbody className="divide-y divide-border">
                    <tr>
                      <td className="py-3 font-semibold">Demandes de contact</td>
                      <td className="py-3">3 ans maximum après le dernier échange</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Newsletter</td>
                      <td className="py-3">Jusqu'au désabonnement</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Logs techniques</td>
                      <td className="py-3">13 mois maximum</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Cookies</td>
                      <td className="py-3">13 mois maximum</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* 6. Destinataires */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <h2 className="text-2xl font-bold mb-4">6. Destinataires des données</h2>
            <div className="text-muted-foreground space-y-4">
              <p>
                Les données personnelles peuvent être accessibles uniquement aux personnes et 
                prestataires qui en ont besoin pour leurs missions.
              </p>

              <h3 className="text-lg font-bold text-foreground mt-6 mb-3">Destinataires internes</h3>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li>Équipe dirigeante</li>
                <li>Équipe communication</li>
                <li>Équipe technique</li>
                <li>Collaborateurs habilités</li>
              </ul>

              <h3 className="text-lg font-bold text-foreground mt-6 mb-3">Sous-traitants</h3>
              <div className="bg-primary/5 rounded-lg p-4">
                <table className="w-full text-sm">
                  <tbody className="divide-y divide-border">
                    <tr>
                      <td className="py-2 font-semibold">Hébergement</td>
                      <td className="py-2">Hostinger (Chypre, UE)</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-semibold">Maintenance</td>
                      <td className="py-2">Équipe technique interne</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-semibold">Statistiques</td>
                      <td className="py-2">Outil analytics conforme CNIL (si activé)</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="bg-success/10 border-l-4 border-success rounded-lg p-4 mt-6">
                <p className="text-sm font-semibold text-foreground mb-2">✅ Engagement</p>
                <p className="text-sm">
                  Les sous-traitants n'agissent que sur instruction d'Ocean Sentinel et doivent 
                  présenter des garanties suffisantes en matière de protection des données.
                </p>
                <p className="text-sm mt-2 font-semibold">
                  Ocean Sentinel ne vend pas les données personnelles des utilisateurs.
                </p>
              </div>
            </div>
          </section>

          {/* 7. Sécurité */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Lock className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">7. Sécurité des données</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p>
                Ocean Sentinel met en œuvre des mesures techniques et organisationnelles adaptées 
                afin de protéger les données personnelles contre l'accès non autorisé, la perte, 
                l'altération, la divulgation ou la destruction.
              </p>

              <h3 className="text-lg font-bold text-foreground mt-6 mb-3">Mesures de sécurité</h3>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li>Accès au site en HTTPS/SSL</li>
                <li>Limitation des accès aux seules personnes habilitées</li>
                <li>Mots de passe robustes</li>
                <li>Sauvegardes régulières</li>
                <li>Mises à jour de sécurité</li>
                <li>Protection anti-spam</li>
                <li>Journalisation technique</li>
                <li>Chiffrement des mots de passe</li>
              </ul>
            </div>
          </section>

          {/* 8. Cookies */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Cookie className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">8. Cookies et traceurs</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p>
                Les sites peuvent utiliser des cookies ou traceurs afin d'assurer leur fonctionnement, 
                mesurer leur audience et améliorer l'expérience utilisateur.
              </p>

              <h3 className="text-lg font-bold text-foreground mt-6 mb-3">Types de cookies</h3>
              <div className="space-y-3">
                <div className="bg-primary/5 rounded-lg p-3">
                  <p className="font-semibold text-foreground text-sm">🔒 Cookies strictement nécessaires</p>
                  <p className="text-sm mt-1">
                    Fonctionnement du site, sécurité, session (exemptés de consentement)
                  </p>
                </div>

                <div className="bg-primary/5 rounded-lg p-3">
                  <p className="font-semibold text-foreground text-sm">📊 Cookies de mesure d'audience</p>
                  <p className="text-sm mt-1">
                    Statistiques anonymisées (si configurés conformément CNIL)
                  </p>
                </div>

                <div className="bg-primary/5 rounded-lg p-3">
                  <p className="font-semibold text-foreground text-sm">⚙️ Cookies de préférences</p>
                  <p className="text-sm mt-1">
                    Mémorisation de vos choix
                  </p>
                </div>
              </div>

              <div className="bg-primary/10 border-l-4 border-primary rounded-lg p-4 mt-6">
                <p className="font-semibold text-foreground mb-2">🍪 Gestion des cookies</p>
                <p className="text-sm">
                  Vous pouvez accepter, refuser ou paramétrer les cookies à tout moment via 
                  les paramètres de votre navigateur.
                </p>
                <p className="text-sm mt-2">
                  Le refus de cookies peut limiter certaines fonctionnalités du site.
                </p>
              </div>
            </div>
          </section>

          {/* 9. Vos droits */}
          <section className="bg-card rounded-2xl border-2 border-primary/40 p-8">
            <div className="flex items-center gap-3 mb-6">
              <AlertCircle className="w-8 h-8 text-primary" />
              <h2 className="text-2xl font-bold m-0">9. Vos droits</h2>
            </div>
            
            <div className="text-muted-foreground space-y-4">
              <p>Conformément au RGPD, vous disposez des droits suivants :</p>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-primary/5 rounded-lg p-4">
                  <p className="font-semibold text-foreground text-sm mb-2">👁️ Droit d'accès</p>
                  <p className="text-sm">Savoir quelles données nous avons sur vous</p>
                </div>

                <div className="bg-primary/5 rounded-lg p-4">
                  <p className="font-semibold text-foreground text-sm mb-2">✏️ Droit de rectification</p>
                  <p className="text-sm">Corriger une erreur</p>
                </div>

                <div className="bg-primary/5 rounded-lg p-4">
                  <p className="font-semibold text-foreground text-sm mb-2">🗑️ Droit d'effacement</p>
                  <p className="text-sm">Demander la suppression de vos données</p>
                </div>

                <div className="bg-primary/5 rounded-lg p-4">
                  <p className="font-semibold text-foreground text-sm mb-2">🚫 Droit d'opposition</p>
                  <p className="text-sm">Refuser certains usages</p>
                </div>

                <div className="bg-primary/5 rounded-lg p-4">
                  <p className="font-semibold text-foreground text-sm mb-2">⏸️ Droit à la limitation</p>
                  <p className="text-sm">Suspendre temporairement un traitement</p>
                </div>

                <div className="bg-primary/5 rounded-lg p-4">
                  <p className="font-semibold text-foreground text-sm mb-2">📦 Droit à la portabilité</p>
                  <p className="text-sm">Récupérer vos données dans un format réutilisable</p>
                </div>
              </div>

              <div className="bg-primary/10 border-l-4 border-primary rounded-lg p-4 mt-6">
                <p className="font-semibold text-foreground mb-2">📧 Exercer vos droits</p>
                <p className="text-sm mb-2">
                  Pour toute demande concernant vos données personnelles, contactez-nous à :
                </p>
                <p className="text-sm">
                  <a href="mailto:contact@oceansentinelle.org" className="text-primary hover:underline font-semibold">
                    contact@oceansentinelle.org
                  </a>
                </p>
                <p className="text-sm mt-3">
                  Une réponse vous sera apportée dans un délai de <strong>30 jours maximum</strong>.
                </p>
              </div>

              <div className="bg-primary/5 rounded-lg p-4">
                <p className="text-sm">
                  <strong className="text-foreground">Réclamation CNIL :</strong> Si vous estimez 
                  que vos droits ne sont pas respectés, vous pouvez introduire une réclamation 
                  auprès de la Commission Nationale de l'Informatique et des Libertés (CNIL).
                </p>
              </div>
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
                Pour toute question relative à la protection de vos données personnelles :
              </p>

              <div className="bg-primary/5 rounded-lg p-4 space-y-2">
                <p className="font-semibold text-foreground">Ocean Sentinel</p>
                <p className="text-sm">
                  <strong>Email RGPD :</strong>{' '}
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

          {/* Engagement final */}
          <section className="bg-gradient-to-r from-primary/10 to-primary/5 border-2 border-primary/40 rounded-2xl p-8">
            <h2 className="text-2xl font-bold mb-4 text-center">Notre engagement</h2>
            <p className="text-muted-foreground text-center max-w-2xl mx-auto">
              Ocean Sentinel s'engage à faire évoluer sa politique de confidentialité avec transparence, 
              dans une logique de <strong className="text-foreground">sobriété numérique</strong>, de{' '}
              <strong className="text-foreground">sécurité</strong>, de{' '}
              <strong className="text-foreground">protection des personnes</strong> et de respect 
              des valeurs environnementales portées par le projet.
            </p>
          </section>

        </div>
      </div>
    </div>
  )
}
