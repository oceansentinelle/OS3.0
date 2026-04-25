/**
 * Home Page - Page d'accueil
 */

import { Link } from 'react-router-dom'
import { BarChart3, Bell, Zap, Shield, BookOpen, Mic, Newspaper } from 'lucide-react'
import { NewsCard } from '@/components/news/NewsCard'
import { NEWS_ARTICLES } from '@/data/newsArticles'

export default function Home() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#f0f4f8' }}>
      {/* Hero Section - Bloc Image Pur */}
      <section className="border-b-2 border-primary">
        {/* Bloc Image Dédié - Avec fond de secours */}
        <div className="relative w-full h-[500px] md:h-[600px] lg:h-[700px] overflow-hidden bg-gradient-to-br from-ocean-900 to-ocean-950">
          {/* Image de fond */}
          <img
            src="/images/bassin-arcachon-hero.jpg"
            alt="Bassin d'Arcachon - Banc de sable et eaux turquoise"
            className="w-full h-full object-cover object-center"
            loading="lazy"
            decoding="async"
          />
          
          {/* Overlay gradient pour lisibilité du texte */}
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/50 to-black/70" />
          
          {/* Contenu superposé */}
          <div className="absolute inset-0 flex flex-col items-center justify-center px-4 text-center">
            <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-6 text-white drop-shadow-2xl max-w-4xl">
              Surveillance Océanographique<br className="hidden sm:block" />
              <span className="sm:hidden"> </span>Temps Réel
            </h1>
            <p className="text-lg md:text-xl lg:text-2xl text-white/95 mb-6 md:mb-8 drop-shadow-lg max-w-3xl">
              Données environnementales du Bassin d'Arcachon<br className="hidden sm:block" />
              <span className="sm:hidden"> </span>Système SACS • Alertes critiques • API REST
            </p>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 px-6 md:px-8 py-3 md:py-4 bg-primary text-primary-foreground rounded-xl font-bold text-base md:text-lg hover:bg-primary/90 transition-colors shadow-2xl shadow-primary/50 touch-target"
            >
              <BarChart3 className="w-5 h-5 md:w-6 md:h-6" />
              <span>Accéder aux données en direct</span>
            </Link>
          </div>
        </div>
      </section>
      
      {/* Features Grid */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Dashboard SACS */}
          <div className="bg-card border-2 border-border rounded-xl p-6 hover:border-primary transition-colors">
            <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center mb-4">
              <BarChart3 className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold mb-2" style={{ color: '#f8fafc' }}>Données en direct SACS</h3>
            <p className="text-sm mb-4" style={{ color: '#f0f4f8' }}>
              Visualisez en temps réel les paramètres océanographiques des stations BARAG et EYRAC.
            </p>
            <Link to="/dashboard" className="text-primary font-semibold hover:underline">
              Voir le dashboard →
            </Link>
          </div>
          
          {/* Alertes */}
          <div className="bg-card border-2 border-border rounded-xl p-6 hover:border-primary transition-colors">
            <div className="w-12 h-12 bg-critical/20 rounded-xl flex items-center justify-center mb-4">
              <Bell className="w-6 h-6 text-critical" />
            </div>
            <h3 className="text-xl font-bold mb-2" style={{ color: '#f8fafc' }}>Alertes Environnementales</h3>
            <p className="text-sm mb-4" style={{ color: '#f0f4f8' }}>
              Recevez des notifications critiques sur l'hypoxie, l'acidification et la température.
            </p>
          </div>
          
          {/* API REST */}
          <div className="bg-card border-2 border-border rounded-xl p-6 hover:border-primary transition-colors">
            <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold mb-2" style={{ color: '#f8fafc' }}>API REST</h3>
            <p className="text-sm mb-4" style={{ color: '#f0f4f8' }}>
              Accédez aux données via notre API professionnelle pour vos applications.
            </p>
            <Link to="/api" className="text-primary font-semibold hover:underline">
              Documentation →
            </Link>
          </div>
          
          {/* Règle de Vérité */}
          <div className="bg-card border-2 border-border rounded-xl p-6 hover:border-primary transition-colors">
            <div className="w-12 h-12 bg-success/20 rounded-xl flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-success" />
            </div>
            <h3 className="text-xl font-bold mb-2" style={{ color: '#f8fafc' }}>Règle de Vérité</h3>
            <p className="text-sm mb-4" style={{ color: '#f0f4f8' }}>
              Chaque donnée est accompagnée de son badge de traçabilité : MESURÉ, INFÉRÉ ou SIMULÉ.
            </p>
          </div>
          
          {/* Le Projet */}
          <div className="bg-card border-2 border-border rounded-xl p-6 hover:border-primary transition-colors">
            <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center mb-4">
              <BookOpen className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold mb-2" style={{ color: '#f8fafc' }}>Le Projet</h3>
            <p className="text-sm mb-4" style={{ color: '#f0f4f8' }}>
              Découvrez l'architecture SACS et les sources de données (COAST-HF, Sentinel-3, Hub'Eau).
            </p>
            <Link to="/about" className="text-primary font-semibold hover:underline">
              En savoir plus →
            </Link>
          </div>
          
          {/* Podcast */}
          <div className="bg-card border-2 border-border rounded-xl p-6 hover:border-primary transition-colors">
            <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center mb-4">
              <Mic className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold mb-2" style={{ color: '#f8fafc' }}>Podcast</h3>
            <p className="text-sm mb-4" style={{ color: '#f0f4f8' }}>
              Écoutez nos épisodes sur l'OSINT océanographique et la règle ABACODE.
            </p>
            <Link to="/podcast" className="text-primary font-semibold hover:underline">
              Écouter →
            </Link>
          </div>
        </div>
      </section>

      {/* Actualités Sentinelles Section */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="flex items-center gap-3 mb-8">
          <Newspaper className="w-8 h-8 text-primary" />
          <h2 className="text-3xl font-bold text-ocean-950">Actualités Sentinelles</h2>
        </div>
        <p className="text-lg text-ocean-700 mb-12 max-w-3xl">
          Flux OSINT environnemental : renseignement open-source sur l'état du Bassin d'Arcachon. 
          Toutes les données sont certifiées <strong>ABACODE 2.0</strong> pour garantir leur traçabilité et leur fiabilité.
        </p>
        
        <div className="space-y-8">
          {NEWS_ARTICLES.map(article => (
            <NewsCard key={article.id} article={article} />
          ))}
        </div>
      </section>
    </div>
  )
}
