import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { wsClient } from '@/lib/ws'

interface PlatformState {
  sources: any[]
  currentSource: string
  rounds: any[]
  stats: any
  analysis: any
  pressure: any
  isConnected: boolean
  isLoading: boolean
  error: string | null
}

interface PlatformContextType extends PlatformState {
  setCurrentSource: (source: string) => void
  refresh: () => void
  subscribeToSource: (source: string) => void
}

const PlatformContext = createContext<PlatformContextType | undefined>(undefined)

interface PlatformProviderProps {
  children: ReactNode
}

export function PlatformProvider({ children }: PlatformProviderProps) {
  const [currentSource, setCurrentSource] = useState<string>('aviator')
  const [isConnected, setIsConnected] = useState<boolean>(false)

  // Fetch sources
  const { data: sources = [] } = useQuery({
    queryKey: ['sources'],
    queryFn: () => api.sources.list(),
    retry: 3,
  })

  // Fetch rounds for current source
  const { data: rounds = [], isLoading, error, refetch } = useQuery({
    queryKey: ['rounds', currentSource],
    queryFn: () => api.rounds.list({ source: currentSource, limit: 100 }),
    retry: 3,
    refetchInterval: 5000,
  })

  // Fetch stats
  const { data: stats = {} } = useQuery({
    queryKey: ['stats', currentSource],
    queryFn: () => api.rounds.stats(currentSource, 1000),
    retry: 3,
  })

  // Fetch analysis
  const { data: analysis = {} } = useQuery({
    queryKey: ['analysis', currentSource],
    queryFn: () => api.analysis.get(currentSource, { limit: 100, include: 'linguistics' }),
    retry: 3,
    refetchInterval: 10000,
  })

  // Fetch pressure
  const { data: pressure = {} } = useQuery({
    queryKey: ['pressure', currentSource],
    queryFn: () => api.pressure.get(currentSource, 100),
    retry: 3,
    refetchInterval: 5000,
  })

  // WebSocket connection
  useEffect(() => {
    wsClient.connect()
    
    const onConnect = () => setIsConnected(true)
    const onDisconnect = () => setIsConnected(false)
    
    wsClient.on('connected', onConnect)
    wsClient.on('disconnect', onDisconnect)
    
    // Subscribe to round updates
    wsClient.on('round:new', (message) => {
      if (message.data?.source === currentSource) {
        refetch()
      }
    })
    
    return () => {
      wsClient.off('connected', onConnect)
      wsClient.off('disconnect', onDisconnect)
      wsClient.disconnect()
    }
  }, [currentSource, refetch])

  const subscribeToSource = (source: string) => {
    setCurrentSource(source)
  }

  const refresh = () => {
    refetch()
  }

  const value: PlatformContextType = {
    sources,
    currentSource,
    setCurrentSource,
    rounds,
    stats,
    analysis,
    pressure,
    isConnected,
    isLoading,
    error,
    refresh,
    subscribeToSource,
  }

  return (
    <PlatformContext.Provider value={value}>
      {children}
    </PlatformContext.Provider>
  )
}

export function usePlatform() {
  const context = useContext(PlatformContext)
  if (context === undefined) {
    throw new Error('usePlatform must be used within a PlatformProvider')
  }
  return context
}