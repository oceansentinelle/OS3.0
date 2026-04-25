/**
 * Footer Component
 * Pied de page avec liens légaux, contact et informations projet
 */

import { Link } from 'react-router-dom'
import { Mail, Github, ExternalLink } from 'lucide-react'

export function Footer() {
  const currentYear = new Date().getFullYear()
  
  return (
    <footer className="bg-card border-t-2 border-primary mt-12">
      <div className="max-w-7xl mx-auto px-4 py-8 md:py-12">
        {/* Grid principale */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Colonne 1 : À propos */}
          <div>
            <h3 className="text-lg font-bold mb-4 text-primary">Ocean Sentinel</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Plateforme de surveillance océanographique en temps réel pour le Bassin d'Arcachon.
              Système SACS (Système d'Alerte Conchylicole Sentinelle).
            </p>
            <div className="flex gap-4">
              <a
                href="https://github.com/oceansentinel"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="mailto:contact@oceansentinelle.fr"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>
          
          {/* Colonne 2 : Navigation */}
          <div>
            <h3 className="text-lg font-bold mb-4">Navigation</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Accueil
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="text-muted-foreground hover:text-primary transition-colors">
                  Données en direct
                </Link>
              </li>
              <li>
                <Link to="/podcast" className="text-muted-foreground hover:text-primary transition-colors">
                  Podcasts SACS
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-muted-foreground hover:text-primary transition-colors">
                  À propos
                </Link>
              </li>
              <li>
                <Link to="/api" className="text-muted-foreground hover:text-primary transition-colors">
                  Documentation API
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Colonne 3 : Légal */}
          <div>
            <h3 className="text-lg font-bold mb-4">Informations légales</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/contact" className="text-muted-foreground hover:text-primary transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link to="/mentions-legales" className="text-muted-foreground hover:text-primary transition-colors">
                  Mentions légales
                </Link>
              </li>
              <li>
                <Link to="/politique-confidentialite" className="text-muted-foreground hover:text-primary transition-colors">
                  Politique de confidentialité
                </Link>
              </li>
              <li>
                <a
                  href="https://www.hostinger.com/fr?REFERRALCODE=UPFACIDENATP"
                  target="_blank"
                  rel="noopener noreferrer sponsored"
                  className="text-muted-foreground hover:text-primary transition-colors inline-flex items-center gap-1"
                >
                  Hébergement Hostinger
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        {/* Séparateur */}
        <div className="border-t border-border pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
            <p>
              © {currentYear} Ocean Sentinel. Tous droits réservés.
            </p>
            <p className="text-xs">
              VPS Hostinger • 76.13.43.3 • React 18 + TypeScript + TailwindCSS
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
