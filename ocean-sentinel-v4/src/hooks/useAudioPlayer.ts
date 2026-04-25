/**
 * useAudioPlayer - Hook principal pour la gestion audio avancée
 * 
 * Fonctionnalités :
 * - Play/Pause/Stop avec retry automatique
 * - Skip avant/arrière configurable
 * - Contrôle volume avec fade
 * - Vitesse lecture (0.5x à 2x)
 * - Mémorisation position (localStorage)
 * - Auto-play épisode suivant
 * - Mode repeat (off/one/all)
 * - Mode shuffle
 * - Gestion erreurs réseau avec retry
 * - MediaSession API (contrôles natifs mobile)
 */

import { useState, useRef, useEffect, useCallback } from 'react'

export interface Episode {
  id: string
  title: string
  description: string
  duration: string
  date: string
  audioUrl: string
}

export type RepeatMode = 'off' | 'one' | 'all'

interface UseAudioPlayerOptions {
  episodes: Episode[]
  onEpisodeEnd?: (episode: Episode) => void
  onError?: (error: Error) => void
  autoPlay?: boolean
  saveProgress?: boolean
}

export function useAudioPlayer({
  episodes,
  onEpisodeEnd,
  onError,
  autoPlay = false,
  saveProgress = true,
}: UseAudioPlayerOptions) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [currentEpisode, setCurrentEpisode] = useState<Episode | null>(episodes[0] || null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [playbackRate, setPlaybackRate] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [repeatMode, setRepeatMode] = useState<RepeatMode>('off')
  const [isShuffleEnabled, setIsShuffleEnabled] = useState(false)
  const [playedEpisodes, setPlayedEpisodes] = useState<Set<string>>(new Set())
  
  const retryCountRef = useRef(0)
  const maxRetries = 3
  
  // Mémorisation position
  const saveProgressToStorage = useCallback((episodeId: string, time: number) => {
    if (!saveProgress) return
    try {
      localStorage.setItem(`audio_progress_${episodeId}`, time.toString())
      localStorage.setItem(`audio_progress_timestamp_${episodeId}`, Date.now().toString())
    } catch (e) {
      console.warn('Failed to save progress:', e)
    }
  }, [saveProgress])
  
  const loadProgressFromStorage = useCallback((episodeId: string): number => {
    if (!saveProgress) return 0
    try {
      const savedTime = localStorage.getItem(`audio_progress_${episodeId}`)
      const timestamp = localStorage.getItem(`audio_progress_timestamp_${episodeId}`)
      
      // Expire après 7 jours
      if (savedTime && timestamp) {
        const age = Date.now() - parseInt(timestamp)
        if (age < 7 * 24 * 60 * 60 * 1000) {
          return parseFloat(savedTime)
        }
      }
    } catch (e) {
      console.warn('Failed to load progress:', e)
    }
    return 0
  }, [saveProgress])
  
  // Initialisation audio element
  useEffect(() => {
    const audio = new Audio()
    audio.preload = 'metadata'
    audioRef.current = audio
    
    return () => {
      audio.pause()
      audio.src = ''
    }
  }, [])
  
  // Chargement épisode
  useEffect(() => {
    const audio = audioRef.current
    if (!audio || !currentEpisode) return
    
    setIsLoading(true)
    setError(null)
    retryCountRef.current = 0
    
    // Sauvegarder position de l'ancien épisode
    if (audio.src && currentTime > 0) {
      const oldEpisodeId = episodes.find(ep => audio.src.includes(ep.audioUrl))?.id
      if (oldEpisodeId) {
        saveProgressToStorage(oldEpisodeId, currentTime)
      }
    }
    
    // Charger nouvel épisode
    audio.src = currentEpisode.audioUrl
    audio.volume = volume
    audio.playbackRate = playbackRate
    
    // Restaurer position sauvegardée
    const savedTime = loadProgressFromStorage(currentEpisode.id)
    if (savedTime > 0) {
      audio.currentTime = savedTime
      setCurrentTime(savedTime)
    } else {
      setCurrentTime(0)
    }
    
    // Update MediaSession API
    if ('mediaSession' in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: currentEpisode.title,
        artist: 'Ocean Sentinel - Podcast SACS',
        album: 'Bulletins d\'alerte conchylicole',
        artwork: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      })
    }
  }, [currentEpisode?.id])
  
  // Event listeners
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    
    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime)
      
      // Sauvegarder toutes les 10 secondes
      if (currentEpisode && Math.floor(audio.currentTime) % 10 === 0) {
        saveProgressToStorage(currentEpisode.id, audio.currentTime)
      }
    }
    
    const handleLoadedMetadata = () => {
      setDuration(audio.duration)
      setIsLoading(false)
    }
    
    const handleCanPlay = () => {
      setIsLoading(false)
      if (autoPlay && isPlaying) {
        audio.play().catch(handlePlayError)
      }
    }
    
    const handleEnded = () => {
      setIsPlaying(false)
      
      if (currentEpisode) {
        // Sauvegarder comme terminé
        saveProgressToStorage(currentEpisode.id, 0)
        onEpisodeEnd?.(currentEpisode)
        
        // Auto-play suivant
        if (repeatMode === 'one') {
          audio.currentTime = 0
          audio.play().catch(handlePlayError)
          setIsPlaying(true)
        } else {
          playNext()
        }
      }
    }
    
    const handleError = () => {
      const errorMsg = `Erreur de chargement audio: ${audio.error?.message || 'Inconnu'}`
      setError(errorMsg)
      setIsLoading(false)
      setIsPlaying(false)
      
      // Retry automatique
      if (retryCountRef.current < maxRetries) {
        retryCountRef.current++
        setTimeout(() => {
          audio.load()
          if (isPlaying) {
            audio.play().catch(handlePlayError)
          }
        }, 1000 * retryCountRef.current)
      } else {
        onError?.(new Error(errorMsg))
      }
    }
    
    const handlePlayError = (err: Error) => {
      console.error('Play error:', err)
      setIsPlaying(false)
      setError('Impossible de lire l\'audio')
      onError?.(err)
    }
    
    const handleLoadStart = () => setIsLoading(true)
    const handleWaiting = () => setIsLoading(true)
    const handlePlaying = () => {
      setIsLoading(false)
      setIsPlaying(true)
    }
    const handlePause = () => setIsPlaying(false)
    
    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('canplay', handleCanPlay)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('error', handleError)
    audio.addEventListener('loadstart', handleLoadStart)
    audio.addEventListener('waiting', handleWaiting)
    audio.addEventListener('playing', handlePlaying)
    audio.addEventListener('pause', handlePause)
    
    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('canplay', handleCanPlay)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('error', handleError)
      audio.removeEventListener('loadstart', handleLoadStart)
      audio.removeEventListener('waiting', handleWaiting)
      audio.removeEventListener('playing', handlePlaying)
      audio.removeEventListener('pause', handlePause)
    }
  }, [currentEpisode, isPlaying, autoPlay, repeatMode])
  
  // MediaSession handlers
  useEffect(() => {
    if (!('mediaSession' in navigator)) return
    
    navigator.mediaSession.setActionHandler('play', () => play())
    navigator.mediaSession.setActionHandler('pause', () => pause())
    navigator.mediaSession.setActionHandler('previoustrack', () => playPrevious())
    navigator.mediaSession.setActionHandler('nexttrack', () => playNext())
    navigator.mediaSession.setActionHandler('seekbackward', () => skip(-10))
    navigator.mediaSession.setActionHandler('seekforward', () => skip(10))
    
    return () => {
      navigator.mediaSession.setActionHandler('play', null)
      navigator.mediaSession.setActionHandler('pause', null)
      navigator.mediaSession.setActionHandler('previoustrack', null)
      navigator.mediaSession.setActionHandler('nexttrack', null)
      navigator.mediaSession.setActionHandler('seekbackward', null)
      navigator.mediaSession.setActionHandler('seekforward', null)
    }
  }, [currentEpisode])
  
  // Actions
  const play = useCallback(async () => {
    const audio = audioRef.current
    if (!audio || isLoading) return
    
    try {
      await audio.play()
      setIsPlaying(true)
      setError(null)
    } catch (err) {
      console.error('Play failed:', err)
      setIsPlaying(false)
      setError('Impossible de lire l\'audio')
      onError?.(err as Error)
    }
  }, [isLoading, onError])
  
  const pause = useCallback(() => {
    const audio = audioRef.current
    if (!audio) return
    
    audio.pause()
    setIsPlaying(false)
    
    // Sauvegarder position
    if (currentEpisode) {
      saveProgressToStorage(currentEpisode.id, audio.currentTime)
    }
  }, [currentEpisode, saveProgressToStorage])
  
  const togglePlay = useCallback(() => {
    if (isPlaying) {
      pause()
    } else {
      play()
    }
  }, [isPlaying, play, pause])
  
  const stop = useCallback(() => {
    const audio = audioRef.current
    if (!audio) return
    
    audio.pause()
    audio.currentTime = 0
    setIsPlaying(false)
    setCurrentTime(0)
  }, [])
  
  const skip = useCallback((seconds: number) => {
    const audio = audioRef.current
    if (!audio) return
    
    const newTime = Math.max(0, Math.min(audio.duration || 0, audio.currentTime + seconds))
    audio.currentTime = newTime
    setCurrentTime(newTime)
  }, [])
  
  const seek = useCallback((time: number) => {
    const audio = audioRef.current
    if (!audio) return
    
    audio.currentTime = time
    setCurrentTime(time)
  }, [])
  
  const changeVolume = useCallback((newVolume: number) => {
    const audio = audioRef.current
    if (!audio) return
    
    const clampedVolume = Math.max(0, Math.min(1, newVolume))
    audio.volume = clampedVolume
    setVolume(clampedVolume)
    
    // Sauvegarder préférence
    try {
      localStorage.setItem('audio_volume', clampedVolume.toString())
    } catch (e) {
      console.warn('Failed to save volume:', e)
    }
  }, [])
  
  const changePlaybackRate = useCallback((rate: number) => {
    const audio = audioRef.current
    if (!audio) return
    
    const clampedRate = Math.max(0.5, Math.min(2, rate))
    audio.playbackRate = clampedRate
    setPlaybackRate(clampedRate)
    
    // Sauvegarder préférence
    try {
      localStorage.setItem('audio_playback_rate', clampedRate.toString())
    } catch (e) {
      console.warn('Failed to save playback rate:', e)
    }
  }, [])
  
  const playEpisode = useCallback((episode: Episode) => {
    const wasPlaying = isPlaying
    pause()
    setCurrentEpisode(episode)
    
    if (wasPlaying) {
      setTimeout(() => play(), 100)
    }
  }, [isPlaying, pause, play])
  
  const playNext = useCallback(() => {
    if (!currentEpisode) return
    
    let nextEpisode: Episode | null = null
    
    if (isShuffleEnabled) {
      // Mode shuffle : épisode aléatoire non joué
      const unplayedEpisodes = episodes.filter(ep => !playedEpisodes.has(ep.id) && ep.id !== currentEpisode.id)
      
      if (unplayedEpisodes.length > 0) {
        const randomIndex = Math.floor(Math.random() * unplayedEpisodes.length)
        nextEpisode = unplayedEpisodes[randomIndex]
      } else if (repeatMode === 'all') {
        // Tous joués, recommencer
        setPlayedEpisodes(new Set())
        const randomIndex = Math.floor(Math.random() * episodes.length)
        nextEpisode = episodes[randomIndex]
      }
    } else {
      // Mode normal : épisode suivant
      const currentIndex = episodes.findIndex(ep => ep.id === currentEpisode.id)
      
      if (currentIndex < episodes.length - 1) {
        nextEpisode = episodes[currentIndex + 1]
      } else if (repeatMode === 'all') {
        nextEpisode = episodes[0]
      }
    }
    
    if (nextEpisode) {
      setPlayedEpisodes(prev => new Set(prev).add(currentEpisode.id))
      playEpisode(nextEpisode)
    }
  }, [currentEpisode, episodes, isShuffleEnabled, playedEpisodes, repeatMode, playEpisode])
  
  const playPrevious = useCallback(() => {
    if (!currentEpisode) return
    
    const audio = audioRef.current
    if (!audio) return
    
    // Si > 3 secondes, recommencer épisode
    if (audio.currentTime > 3) {
      audio.currentTime = 0
      setCurrentTime(0)
      return
    }
    
    // Sinon, épisode précédent
    const currentIndex = episodes.findIndex(ep => ep.id === currentEpisode.id)
    
    if (currentIndex > 0) {
      playEpisode(episodes[currentIndex - 1])
    } else if (repeatMode === 'all') {
      playEpisode(episodes[episodes.length - 1])
    }
  }, [currentEpisode, episodes, repeatMode, playEpisode])
  
  const toggleRepeat = useCallback(() => {
    setRepeatMode(prev => {
      if (prev === 'off') return 'all'
      if (prev === 'all') return 'one'
      return 'off'
    })
  }, [])
  
  const toggleShuffle = useCallback(() => {
    setIsShuffleEnabled(prev => !prev)
    setPlayedEpisodes(new Set())
  }, [])
  
  return {
    // State
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
    
    // Actions
    play,
    pause,
    togglePlay,
    stop,
    skip,
    seek,
    changeVolume,
    changePlaybackRate,
    playEpisode,
    playNext,
    playPrevious,
    toggleRepeat,
    toggleShuffle,
    
    // Ref
    audioRef,
  }
}
