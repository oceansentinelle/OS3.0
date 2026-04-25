/**
 * Configuration application Ocean Sentinelle V3.1
 */

export const config = {
  app: {
    name: import.meta.env.VITE_APP_NAME || 'Ocean Sentinelle',
    version: import.meta.env.VITE_APP_VERSION || '3.1.0',
    domain: import.meta.env.VITE_APP_DOMAIN || 'oceansentinelle.fr',
  },
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'https://api.oceansentinelle.fr',
    version: import.meta.env.VITE_API_VERSION || 'v1',
    get url() {
      return `${this.baseUrl}/api/${this.version}`
    },
  },
  features: {
    agenticUx: import.meta.env.VITE_ENABLE_AGENTIC_UX === 'true',
    intentPreview: import.meta.env.VITE_ENABLE_INTENT_PREVIEW === 'true',
  },
} as const

export default config
