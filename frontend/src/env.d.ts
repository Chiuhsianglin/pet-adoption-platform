/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_API_VERSION?: string
  readonly VITE_V2_ENABLED?: string
  readonly VITE_API_TIMEOUT?: string
  readonly VITE_APP_TITLE: string
  readonly VITE_UPLOAD_MAX_SIZE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
