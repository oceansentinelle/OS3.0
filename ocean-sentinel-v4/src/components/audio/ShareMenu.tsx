/**
 * ShareMenu - Menu partage épisode (WhatsApp, Facebook, X, Email, QR Code)
 */

import { Share2, Copy, Download, QrCode, Check } from 'lucide-react'
import { useState } from 'react'
import type { Episode } from '@/hooks/useAudioPlayer'

interface ShareMenuProps {
  episode: Episode
  currentTime?: number
  className?: string
}

export function ShareMenu({ episode, currentTime = 0, className = '' }: ShareMenuProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [showQR, setShowQR] = useState(false)
  
  const episodeUrl = `${window.location.origin}/podcast?episode=${episode.id}${currentTime > 0 ? `&t=${Math.floor(currentTime)}` : ''}`
  const shareText = `🎧 ${episode.title}\n\n${episode.description}\n\nÉcouter sur Ocean Sentinel :`
  
  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(episodeUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }
  
  const shareWhatsApp = () => {
    const url = `https://wa.me/?text=${encodeURIComponent(shareText + ' ' + episodeUrl)}`
    window.open(url, '_blank')
    setIsOpen(false)
  }
  
  const shareFacebook = () => {
    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(episodeUrl)}`
    window.open(url, '_blank', 'width=600,height=400')
    setIsOpen(false)
  }
  
  const shareX = () => {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(episodeUrl)}`
    window.open(url, '_blank', 'width=600,height=400')
    setIsOpen(false)
  }
  
  const shareEmail = () => {
    const subject = encodeURIComponent(episode.title)
    const body = encodeURIComponent(`${shareText}\n\n${episodeUrl}`)
    window.location.href = `mailto:?subject=${subject}&body=${body}`
    setIsOpen(false)
  }
  
  const downloadAudio = () => {
    const link = document.createElement('a')
    link.href = episode.audioUrl
    link.download = `${episode.title}.mp3`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setIsOpen(false)
  }
  
  const generateQRCode = () => {
    setShowQR(true)
  }
  
  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg hover:bg-primary/10 transition-colors"
        aria-label="Partager l'épisode"
        aria-expanded={isOpen}
      >
        <Share2 className="w-5 h-5 text-foreground" />
      </button>
      
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute bottom-full right-0 mb-2 bg-card border-2 border-primary/40 rounded-lg shadow-xl z-50 overflow-hidden min-w-[200px]">
            <div className="p-2 space-y-1">
              <button
                onClick={copyLink}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm rounded-lg hover:bg-primary/10 transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 text-success" />
                    <span className="text-success">Lien copié !</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    <span>Copier le lien</span>
                  </>
                )}
              </button>
              
              <button
                onClick={shareWhatsApp}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm rounded-lg hover:bg-primary/10 transition-colors"
              >
                <span className="text-lg">💬</span>
                <span>WhatsApp</span>
              </button>
              
              <button
                onClick={shareFacebook}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm rounded-lg hover:bg-primary/10 transition-colors"
              >
                <span className="text-lg">📘</span>
                <span>Facebook</span>
              </button>
              
              <button
                onClick={shareX}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm rounded-lg hover:bg-primary/10 transition-colors"
              >
                <span className="text-lg">✖️</span>
                <span>X (Twitter)</span>
              </button>
              
              <button
                onClick={shareEmail}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm rounded-lg hover:bg-primary/10 transition-colors"
              >
                <span className="text-lg">📧</span>
                <span>Email</span>
              </button>
              
              <div className="border-t border-border my-1" />
              
              <button
                onClick={generateQRCode}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm rounded-lg hover:bg-primary/10 transition-colors"
              >
                <QrCode className="w-4 h-4" />
                <span>QR Code</span>
              </button>
              
              <button
                onClick={downloadAudio}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm rounded-lg hover:bg-primary/10 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Télécharger MP3</span>
              </button>
            </div>
          </div>
        </>
      )}
      
      {showQR && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border-2 border-primary rounded-2xl p-6 max-w-sm w-full">
            <h3 className="text-xl font-bold mb-4 text-center">QR Code de partage</h3>
            <div className="bg-white p-4 rounded-lg mb-4">
              <img
                src={`https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(episodeUrl)}`}
                alt="QR Code"
                className="w-full h-auto"
              />
            </div>
            <p className="text-sm text-muted-foreground text-center mb-4">
              Scannez ce code pour accéder à l'épisode
            </p>
            <button
              onClick={() => setShowQR(false)}
              className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
