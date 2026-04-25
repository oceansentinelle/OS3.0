/**
 * NewsCard Component - Actualités Sentinelles
 * 
 * Carte d'actualité OSINT avec système de badges ABACODE 2.0
 * - Zone visuelle 50% (image haute résolution)
 * - Zone textuelle 50% (titre, teaser, action)
 * - Badges de métadonnées (Source, Date, Statut, Certification)
 * - Animation hover fluide
 */

import { Shield, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

export interface NewsArticle {
  id: string
  title: string
  teaser: string
  content: string
  image: string
  imageAlt: string
  source: string
  date: string
  status: 'measured' | 'simulated' | 'inferred'
  certified: boolean
  keyData: string
}

interface NewsCardProps {
  article: NewsArticle
}

const STATUS_LABELS = {
  measured: 'Mesuré',
  simulated: 'Simulé',
  inferred: 'Inféré',
}

const STATUS_COLORS = {
  measured: 'bg-emerald-500/10 text-emerald-700 border-emerald-500/30',
  simulated: 'bg-slate-500/10 text-slate-700 border-slate-500/30',
  inferred: 'bg-amber-500/10 text-amber-700 border-amber-500/30',
}

export function NewsCard({ article }: NewsCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <article
      className={cn(
        'group relative overflow-hidden rounded-2xl',
        'border-4 border-primary/40 hover:border-primary',
        'bg-white shadow-lg hover:shadow-2xl hover:shadow-primary/20',
        'transition-all duration-300'
      )}
    >
      {/* ABACODE 2.0 Badge Bar */}
      <div className="flex items-center gap-2 flex-wrap px-4 py-2 bg-gradient-to-r from-ocean-950 to-ocean-900 text-xs">
        <span className="text-white/90 font-semibold">{article.source}</span>
        <span className="text-white/50">•</span>
        <span className="text-white/90">{article.date}</span>
        <span className="text-white/50">•</span>
        <span className={cn(
          'px-2 py-0.5 rounded-full border font-semibold',
          STATUS_COLORS[article.status]
        )}>
          {STATUS_LABELS[article.status]}
        </span>
        {article.certified && (
          <>
            <span className="text-white/50">•</span>
            <span className="flex items-center gap-1 text-primary font-semibold">
              <Shield className="w-3 h-3" />
              ABACODE Certifié
            </span>
          </>
        )}
      </div>

      {/* Content Grid: 50% Image / 50% Text */}
      <div className="grid md:grid-cols-2 gap-0">
        {/* Visual Zone (50%) */}
        <div className="relative h-48 sm:h-64 md:h-full overflow-hidden bg-ocean-950">
          <img
            src={article.image}
            alt={article.imageAlt}
            className="w-full h-full object-cover object-center transition-transform duration-500 group-hover:scale-110"
            loading="lazy"
            decoding="async"
            width="800"
            height="600"
          />
          {/* Overlay gradient for better text readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>

        {/* Textual Zone (50%) */}
        <div className="flex flex-col p-6">
          <h3 className="text-2xl font-bold mb-3 text-ocean-950 group-hover:text-primary transition-colors">
            {article.title}
          </h3>
          <p className="text-sm text-ocean-700 mb-4 leading-relaxed">
            {article.teaser}
          </p>
          
          {/* Expandable Content */}
          {isExpanded && (
            <div className="mb-4 p-4 bg-ocean-50 rounded-lg border-2 border-primary/20">
              <p className="text-sm text-ocean-800 leading-relaxed whitespace-pre-line">
                {article.content}
              </p>
            </div>
          )}
          
          {/* Read More Button */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={cn(
              'inline-flex items-center gap-2 self-start mb-4',
              'px-4 py-2 rounded-lg',
              'text-sm font-semibold text-primary',
              'hover:bg-primary/10 transition-colors'
            )}
          >
            {isExpanded ? (
              <>
                Lire moins
                <ChevronUp className="w-4 h-4" />
              </>
            ) : (
              <>
                Lire plus
                <ChevronDown className="w-4 h-4" />
              </>
            )}
          </button>
          
          {/* Key Data Highlight */}
          <div className="bg-primary/10 border-l-4 border-primary px-4 py-3">
            <p className="text-xs font-semibold text-ocean-950 uppercase tracking-wide mb-1">
              Donnée Clé
            </p>
            <p className="text-sm text-ocean-800 font-medium">
              {article.keyData}
            </p>
          </div>
        </div>
      </div>
    </article>
  )
}
