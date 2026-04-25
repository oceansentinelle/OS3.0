/**
 * Podcast Page - Bulletins vocaux
 * 
 * Lecteur audio nouvelle génération pour les bulletins d'alerte SACS
 * - Interface manipulable à une main
 * - Contrôles ARIA complets (WCAG 2.2 AA)
 * - Playlist fluide avec auto-play
 * - Transitions seamless entre épisodes
 * - Contrôle volume avec mute
 * - Vitesse lecture (0.5x à 2x)
 * - Mode repeat (off/one/all) et shuffle
 * - Mémorisation position d'écoute
 * - Partage et téléchargement
 * - Gestion erreurs réseau avec retry
 * - MediaSession API (contrôles natifs mobile)
 */

import { Play, Pause, SkipBack, SkipForward, Mic, Repeat, Repeat1, Shuffle, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAudioPlayer } from '@/hooks/useAudioPlayer'
import { VolumeControl } from '@/components/audio/VolumeControl'
import { PlaybackSpeed } from '@/components/audio/PlaybackSpeed'
import { ShareMenu } from '@/components/audio/ShareMenu'

import type { Episode } from '@/hooks/useAudioPlayer'

// Épisodes NotebookLM
const EPISODES: Episode[] = [
  {
    id: '001',
    title: 'Bulletin SACS #1 - Alerte Hypoxie Avril 2026',
    description: 'Analyse de la crise hypoxique détectée sur le Bassin d\'Arcachon. Recommandations pour les ostréiculteurs.',
    duration: '8:32',
    date: '23 avril 2026',
    audioUrl: '/audio/sacs-001-hypoxie-avril-2026.mp3',
  },
  {
    id: '002',
    title: 'Bulletin SACS #2 - Alerte Acidification Avril 2026',
    description: 'Analyse de l\'acidification océanique et impact sur les coquillages. Mesures préventives pour les conchyliculteurs.',
    duration: '12:15',
    date: '23 avril 2026',
    audioUrl: '/audio/sacs-002-acidification-avril-2026.mp3',
  },
  {
    id: '003',
    title: 'Bulletin SACS #3 - IA et Satellites contre l\'Hécatombe Ostréicole',
    description: 'Comment l\'intelligence artificielle et l\'observation satellitaire révolutionnent la surveillance des eaux conchylicoles.',
    duration: '11:30',
    date: '24 avril 2026',
    audioUrl: '/audio/sacs-003-ia-satellites-avril-2026.mp3',
  },
  {
    id: '004',
    title: 'Bulletin SACS #4 - Le Paradoxe des Huîtres Géantes d\'Arcachon',
    description: 'Enquête sur le phénomène des huîtres géantes du Bassin d\'Arcachon. Analyse des facteurs environnementaux et implications pour la conchyliculture. Opportunités et défis pour les ostréiculteurs.',
    duration: '13:05',
    date: '24 avril 2026',
    audioUrl: '/audio/sacs-004-huitres-geantes-avril-2026.mp3',
  },
]

export default function Podcast() {
  const {
    currentEpisode,
    isPlaying,
    currentTime,
    duration,
    volume,
    playbackRate,
    isLoading,
    error,
    repeatMode,
    isShuffleEnabled,
    togglePlay,
    skip,
    seek,
    changeVolume,
    changePlaybackRate,
    playEpisode,
    toggleRepeat,
    toggleShuffle,
  } = useAudioPlayer({
    episodes: EPISODES,
    autoPlay: false,
    saveProgress: true,
  })
  
  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    seek(time)
  }
  
  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }
  
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#ffffff' }}>
      {/* Hero */}
      <section className="bg-gradient-to-br from-ocean-950 to-ocean-900 border-b-2 border-primary">
        <div className="max-w-4xl mx-auto px-4 py-12">
          <div className="flex items-center gap-3 mb-4">
            <Mic className="w-10 h-10 text-primary" />
            <h1 className="text-4xl font-bold" style={{ color: '#f8fafc' }}>Podcast SACS</h1>
          </div>
          <p className="text-xl" style={{ color: '#f0f4f8' }}>
            Bulletins vocaux d'alerte pour les ostréiculteurs du Bassin d'Arcachon
          </p>
        </div>
      </section>
      
      {/* Player */}
      {currentEpisode && (
        <section className="max-w-2xl mx-auto px-4 py-12">
          <div className="border-4 border-primary rounded-2xl overflow-hidden shadow-2xl shadow-primary/30" style={{ backgroundColor: '#ffffff' }}>
            {/* Episode Info */}
            <div className="p-8 space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-primary/20 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Mic className="w-8 h-8 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="text-2xl font-bold mb-2" style={{ color: '#001d3d' }}>{currentEpisode.title}</h2>
                  <p className="text-sm mb-2" style={{ color: '#003566' }}>{currentEpisode.description}</p>
                  <div className="flex items-center gap-4 text-xs" style={{ color: '#003566' }}>
                    <span>📅 {currentEpisode.date}</span>
                    <span>⏱️ {currentEpisode.duration}</span>
                  </div>
                </div>
              </div>
              
              {/* Error Message */}
              {error && (
                <div className="flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/40 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              )}
              
              {/* Progress Bar */}
              <div className="space-y-2">
                <input
                  type="range"
                  min="0"
                  max={duration || 0}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-2 bg-ocean-800 rounded-full appearance-none cursor-pointer
                    [&::-webkit-slider-thumb]:appearance-none
                    [&::-webkit-slider-thumb]:w-4
                    [&::-webkit-slider-thumb]:h-4
                    [&::-webkit-slider-thumb]:rounded-full
                    [&::-webkit-slider-thumb]:bg-primary
                    [&::-webkit-slider-thumb]:cursor-pointer
                    [&::-webkit-slider-thumb]:shadow-lg
                    [&::-moz-range-thumb]:w-4
                    [&::-moz-range-thumb]:h-4
                    [&::-moz-range-thumb]:rounded-full
                    [&::-moz-range-thumb]:bg-primary
                    [&::-moz-range-thumb]:border-0
                    [&::-moz-range-thumb]:cursor-pointer
                    [&::-moz-range-thumb]:shadow-lg"
                  aria-label="Position de lecture"
                  aria-valuemin={0}
                  aria-valuemax={duration}
                  aria-valuenow={currentTime}
                  aria-valuetext={`${formatTime(currentTime)} sur ${formatTime(duration)}`}
                />
                <div className="flex justify-between text-xs" style={{ color: '#003566' }}>
                  <span>{formatTime(currentTime)}</span>
                  <span>-{formatTime(duration - currentTime)}</span>
                </div>
              </div>
              
              {/* Controls */}
              <div className="flex items-center justify-center gap-4 pt-4">
                <button
                  onClick={() => skip(-10)}
                  className="touch-target p-3 rounded-full bg-ocean-800 hover:bg-ocean-700 transition-colors"
                  aria-label="Reculer de 10 secondes"
                  disabled={isLoading}
                >
                  <SkipBack className="w-6 h-6" />
                </button>
                
                <button
                  onClick={togglePlay}
                  className="touch-target p-6 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-lg shadow-primary/50 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label={isPlaying ? 'Pause' : 'Lecture'}
                  aria-pressed={isPlaying}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : isPlaying ? (
                    <Pause className="w-8 h-8" />
                  ) : (
                    <Play className="w-8 h-8" />
                  )}
                </button>
                
                <button
                  onClick={() => skip(10)}
                  className="touch-target p-3 rounded-full bg-ocean-800 hover:bg-ocean-700 transition-colors"
                  aria-label="Avancer de 10 secondes"
                  disabled={isLoading}
                >
                  <SkipForward className="w-6 h-6" />
                </button>
              </div>
              
              {/* Advanced Controls */}
              <div className="flex items-center justify-between pt-4 border-t border-border">
                <div className="flex items-center gap-2">
                  <button
                    onClick={toggleShuffle}
                    className={cn(
                      "p-2 rounded-lg transition-colors",
                      isShuffleEnabled
                        ? "bg-primary/20 text-primary"
                        : "hover:bg-primary/10"
                    )}
                    aria-label="Mode aléatoire"
                    aria-pressed={isShuffleEnabled}
                  >
                    <Shuffle className="w-5 h-5" />
                  </button>
                  
                  <button
                    onClick={toggleRepeat}
                    className={cn(
                      "p-2 rounded-lg transition-colors",
                      repeatMode !== 'off'
                        ? "bg-primary/20 text-primary"
                        : "hover:bg-primary/10"
                    )}
                    aria-label={`Mode répétition: ${repeatMode === 'off' ? 'désactivé' : repeatMode === 'one' ? 'un épisode' : 'tous'}`}
                  >
                    {repeatMode === 'one' ? (
                      <Repeat1 className="w-5 h-5" />
                    ) : (
                      <Repeat className="w-5 h-5" />
                    )}
                  </button>
                </div>
                
                <div className="flex items-center gap-4">
                  <VolumeControl volume={volume} onChange={changeVolume} />
                  <PlaybackSpeed playbackRate={playbackRate} onChange={changePlaybackRate} />
                  <ShareMenu episode={currentEpisode} currentTime={currentTime} />
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
      
      {/* Episodes List */}
      <section className="max-w-4xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-bold mb-6" style={{ color: '#001d3d' }}>Tous les épisodes</h2>
        
        <div className="space-y-4">
          {EPISODES.map(episode => (
            <button
              key={episode.id}
              onClick={() => playEpisode(episode)}
              disabled={isLoading}
              className={cn(
                'w-full text-left p-6 rounded-xl border-4 transition-all',
                currentEpisode?.id === episode.id
                  ? 'border-primary shadow-lg shadow-primary/20 bg-primary/5'
                  : 'border-primary/40 hover:border-primary hover:shadow-lg hover:shadow-primary/20 bg-white'
              )}
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Mic className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold mb-1" style={{ color: '#001d3d' }}>{episode.title}</h3>
                  <p className="text-sm mb-2" style={{ color: '#003566' }}>{episode.description}</p>
                  <div className="flex items-center gap-4 text-xs" style={{ color: '#003566' }}>
                    <span>{episode.date}</span>
                    <span>•</span>
                    <span>{episode.duration}</span>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
