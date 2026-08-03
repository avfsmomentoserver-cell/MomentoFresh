import { getConfig } from './config'

const config = getConfig()

interface WebSocketMessage {
  type: string
  data: any
  source?: string
  timestamp?: string
}

interface WebSocketListener {
  (message: WebSocketMessage): void
}

class WebSocketClient {
  private socket: WebSocket | null = null
  private listeners: Map<string, Set<WebSocketListener>> = new Map()
  private reconnectInterval: number = 5000
  private maxReconnectInterval: number = 30000
  private reconnectTimeout: NodeJS.Timeout | null = null

  connect(): void {
    this.disconnect()
    
    try {
      this.socket = new WebSocket(config.wsUrl)
      
      this.socket.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectInterval = 5000
      }
      
      this.socket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.notifyListeners(message.type, message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      this.socket.onclose = () => {
        console.log('WebSocket disconnected, attempting to reconnect...')
        this.scheduleReconnect()
      }
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      this.scheduleReconnect()
    }
  }

  disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout) return
    
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectInterval = Math.min(
        this.reconnectInterval * 2,
        this.maxReconnectInterval
      )
      this.connect()
    }, this.reconnectInterval)
  }

  send(message: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    }
  }

  on(eventType: string, listener: WebSocketListener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    this.listeners.get(eventType)!.add(listener)
    
    return () => {
      this.listeners.get(eventType)?.delete(listener)
    }
  }

  off(eventType: string, listener: WebSocketListener): void {
    this.listeners.get(eventType)?.delete(listener)
  }

  private notifyListeners(eventType: string, message: WebSocketMessage): void {
    const listeners = this.listeners.get(eventType)
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(message)
        } catch (error) {
          console.error('Error in WebSocket listener:', error)
        }
      })
    }
    
    // Also notify wildcard listeners
    const wildcardListeners = this.listeners.get('*')
    if (wildcardListeners) {
      wildcardListeners.forEach(listener => {
        try {
          listener(message)
        } catch (error) {
          console.error('Error in wildcard WebSocket listener:', error)
        }
      })
    }
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN
  }
}

export const wsClient = new WebSocketClient()

export function useWebSocket() {
  return wsClient
}