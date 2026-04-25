/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_APP_DOMAIN: string
  readonly VITE_API_URL: string
  readonly VITE_API_VERSION: string
  readonly VITE_ENABLE_AGENTIC_UX: string
  readonly VITE_ENABLE_INTENT_PREVIEW: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
