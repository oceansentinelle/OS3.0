/**
 * Contact Page - Page de contact simplifiée
 * 
 * Affichage simple et direct des coordonnées de contact
 * Emails : contact@oceansentinelle.org, admin@oceansentinelle.fr
 */

import { Mail, MapPin, Clock } from 'lucide-react'

export default function Contact() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-ocean-950 to-ocean-900 border-b-2 border-primary">
        <div className="max-w-7xl mx-auto px-4 py-12 md:py-16">
          <div className="text-center">
            <Mail className="w-16 h-16 mx-auto mb-4 text-primary" />
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
              Contactez-nous
            </h1>
            <p className="text-lg md:text-xl text-white/90 max-w-2xl mx-auto">
              Une question sur Ocean Sentinel ? Notre équipe est à votre écoute.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Cards */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="grid gap-6">
          {/* Email Contact Général */}
          <a
            href="mailto:contact@oceansentinelle.org"
            className="group bg-card rounded-2xl border-4 border-primary/40 hover:border-primary p-8 transition-all hover:shadow-2xl hover:shadow-primary/20"
          >
            <div className="flex items-start gap-6">
              <div className="bg-primary/10 p-4 rounded-xl group-hover:bg-primary/20 transition-colors">
                <Mail className="w-8 h-8 text-primary" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">
                  Contact général
                </h2>
                <p className="text-muted-foreground mb-4">
                  Pour toutes vos questions sur Ocean Sentinel, nos données océanographiques,
                  ou pour établir un partenariat.
                </p>
                <p className="text-xl font-mono font-bold text-primary">
                  contact@oceansentinelle.org
                </p>
              </div>
            </div>
          </a>

          {/* Email Administration */}
          <a
            href="mailto:admin@oceansentinelle.fr"
            className="group bg-card rounded-2xl border-4 border-primary/40 hover:border-primary p-8 transition-all hover:shadow-2xl hover:shadow-primary/20"
          >
            <div className="flex items-start gap-6">
              <div className="bg-primary/10 p-4 rounded-xl group-hover:bg-primary/20 transition-colors">
                <Mail className="w-8 h-8 text-primary" />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2 group-hover:text-primary transition-colors">
                  Administration
                </h2>
                <p className="text-muted-foreground mb-4">
                  Pour les questions techniques, problèmes d'accès à l'API,
                  ou gestion du VPS Hostinger.
                </p>
                <p className="text-xl font-mono font-bold text-primary">
                  admin@oceansentinelle.fr
                </p>
              </div>
            </div>
          </a>

          {/* Informations complémentaires */}
          <div className="grid md:grid-cols-2 gap-6 mt-6">
            {/* Localisation */}
            <div className="bg-card rounded-2xl border-2 border-primary/40 p-6">
              <div className="flex items-center gap-3 mb-4">
                <MapPin className="w-6 h-6 text-primary" />
                <h3 className="text-xl font-bold">Localisation</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                <span className="font-semibold text-foreground">Bassin d'Arcachon</span><br />
                Nouvelle-Aquitaine, France<br />
                <span className="text-xs">VPS Hostinger • IP: 76.13.43.3</span>
              </p>
            </div>

            {/* Délai de réponse */}
            <div className="bg-card rounded-2xl border-2 border-primary/40 p-6">
              <div className="flex items-center gap-3 mb-4">
                <Clock className="w-6 h-6 text-primary" />
                <h3 className="text-xl font-bold">Délai de réponse</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Nous répondons généralement dans un délai de{' '}
                <span className="font-semibold text-foreground">48 heures ouvrées</span>.
                Pour les urgences, précisez-le dans l'objet de votre email.
              </p>
            </div>
          </div>

          {/* Note importante */}
          <div className="bg-primary/10 border-l-4 border-primary rounded-lg p-6 mt-6">
            <h3 className="font-bold mb-2 text-lg">📧 Comment nous contacter ?</h3>
            <p className="text-sm text-muted-foreground mb-3">
              Cliquez simplement sur l'une des cartes ci-dessus pour ouvrir votre client email
              (Gmail, Outlook, Thunderbird...) avec l'adresse pré-remplie.
            </p>
            <p className="text-sm text-muted-foreground">
              Vous pouvez aussi copier l'adresse email et nous écrire directement depuis
              votre application de messagerie préférée.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
