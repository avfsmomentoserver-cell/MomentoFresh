export interface AppConfig {
  apiBaseUrl: string
  wsUrl: string
  appName: string
  version: string
}

const DEFAULT_CONFIG: AppConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
  appName: 'MomentoFresh',
  version: '4.0.0',
}

export function getConfig(): AppConfig {
  return DEFAULT_CONFIG
}

export const API_BASE_URL = DEFAULT_CONFIG.apiBaseUrl
export const WS_URL = DEFAULT_CONFIG.wsUrl