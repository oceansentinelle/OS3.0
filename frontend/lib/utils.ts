import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Merge Tailwind classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format confidence percentage
 */
export function formatConfidence(value: number): string {
  return `${Math.round(value)}%`
}

/**
 * Get confidence level from percentage
 */
export function getConfidenceLevel(value: number): 'high' | 'medium' | 'low' | 'verylow' {
  if (value >= 80) return 'high'
  if (value >= 60) return 'medium'
  if (value >= 40) return 'low'
  return 'verylow'
}

/**
 * Get confidence color class
 */
export function getConfidenceColor(value: number): string {
  const level = getConfidenceLevel(value)
  const colors = {
    high: 'text-confidence-high',
    medium: 'text-confidence-medium',
    low: 'text-confidence-low',
    verylow: 'text-confidence-verylow',
  }
  return colors[level]
}

/**
 * Get risk level color class
 */
export function getRiskColor(level: 'critical' | 'high' | 'attention' | 'normal'): string {
  const colors = {
    critical: 'bg-critical-500 text-white',
    high: 'bg-high-500 text-white',
    attention: 'bg-attention-500 text-neutral-900',
    normal: 'bg-normal-500 text-white',
  }
  return colors[level]
}

/**
 * Get risk icon
 */
export function getRiskIcon(level: 'critical' | 'high' | 'attention' | 'normal'): string {
  const icons = {
    critical: '🔴',
    high: '🟠',
    attention: '🟡',
    normal: '🟢',
  }
  return icons[level]
}

/**
 * Format timestamp
 */
export function formatTimestamp(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

/**
 * Format date
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('fr-FR', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

/**
 * Format datetime
 */
export function formatDatetime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format temperature
 */
export function formatTemperature(value: number, uncertainty?: number): string {
  const temp = value.toFixed(1)
  if (uncertainty) {
    return `${temp}°C ±${uncertainty.toFixed(1)}°C`
  }
  return `${temp}°C`
}

/**
 * Format duration
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} minute${minutes > 1 ? 's' : ''}`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (mins === 0) {
    return `${hours} heure${hours > 1 ? 's' : ''}`
  }
  return `${hours}h${mins.toString().padStart(2, '0')}`
}

/**
 * Truncate text
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * Check if value is within normal range
 */
export function isWithinRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * Calculate deviation percentage
 */
export function calculateDeviation(value: number, reference: number): number {
  return ((value - reference) / reference) * 100
}

/**
 * Format deviation
 */
export function formatDeviation(value: number, reference: number): string {
  const deviation = calculateDeviation(value, reference)
  const sign = deviation > 0 ? '+' : ''
  return `${sign}${deviation.toFixed(1)}%`
}
