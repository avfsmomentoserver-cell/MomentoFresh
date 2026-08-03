import { getConfig } from './config'

const config = getConfig()

interface ApiResponse<T> {
  data: T
  message?: string
}

interface ApiError {
  message: string
  detail?: string
}

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = new URL(endpoint, config.apiBaseUrl)
  
  const response = await fetch(url.toString(), {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({ message: 'Request failed' }))
    throw new Error(error.message || 'Request failed')
  }

  const data: ApiResponse<T> = await response.json()
  return data.data
}

// API client with methods
export const api = {
  // Health
  health: () => apiRequest<{ status: string; version: string }>('/api/v1/health'),
  
  // Platform
  platform: () => apiRequest<any>('/api/v1/platform'),
  
  // Sources
  sources: {
    list: () => apiRequest<any[]>('/api/v1/sources'),
    create: (name: string, displayName?: string) => 
      apiRequest<any>('/api/v1/core/sources', {
        method: 'POST',
        body: JSON.stringify({ name, display_name: displayName }),
      }),
  },
  
  // Rounds
  rounds: {
    list: (params?: { source?: string; limit?: number; offset?: number }) => {
      const query = new URLSearchParams(params).toString()
      return apiRequest<any[]>('/api/v1/rounds?' + query)
    },
    latest: (source?: string) => {
      const query = source ? new URLSearchParams({ source }).toString() : ''
      return apiRequest<any>('/api/v1/rounds/latest?' + query)
    },
    stats: (source?: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/rounds/stats?' + query)
    },
  },
  
  // Analysis
  analysis: {
    get: (source: string, params?: { limit?: number; include?: string }) => {
      const query = new URLSearchParams({ source, ...params }).toString()
      return apiRequest<any>('/api/v1/analysis?' + query)
    },
    state: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/analysis/state?' + query)
    },
    signals: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/analysis/signals?' + query)
    },
  },
  
  // Pressure
  pressure: {
    get: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/pressure?' + query)
    },
    state: (source: string) => 
      apiRequest<any>('/api/v1/pressure/state?' + new URLSearchParams({ source }).toString()),
    predictions: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/pressure/predictions?' + query)
    },
  },
  
  // Backtest
  backtest: {
    run: (config: any) => 
      apiRequest<any>('/api/v1/backtest', {
        method: 'POST',
        body: JSON.stringify(config),
      }),
    simple: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/backtest/simple?' + query)
    },
    signals: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/backtest/signals?' + query)
    },
    metrics: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/backtest/metrics?' + query)
    },
  },
  
  // Linguistics
  linguistics: {
    get: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/linguistics?' + query)
    },
    bands: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/linguistics/bands?' + query)
    },
    states: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/linguistics/states?' + query)
    },
    pressure: (source: string, limit?: number) => {
      const query = new URLSearchParams({ source, limit: limit?.toString() }).toString()
      return apiRequest<any>('/api/v1/linguistics/pressure?' + query)
    },
  },
  
  // Ingest
  ingest: {
    rounds: (rounds: any[], source?: string) => 
      apiRequest<any>('/api/v1/ingest', {
        method: 'POST',
        body: JSON.stringify({ rounds, source }),
      }),
    file: (file: File, source?: string) => {
      const formData = new FormData()
      formData.append('file', file)
      if (source) formData.append('source', source)
      return fetch('/api/v1/ingest/file', {
        method: 'POST',
        body: formData,
      }).then(res => res.json())
    },
  },
}