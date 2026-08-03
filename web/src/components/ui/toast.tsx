import * as React from 'react'
import { cn } from '@/lib/utils'

interface ToastProps {
  message: string
  type?: 'success' | 'error' | 'warning' | 'info'
  onDismiss?: () => void
}

export function Toast({ message, type = 'info', onDismiss }: ToastProps) {
  const bgColor = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500',
  }[type]

  return (
    <div 
      className={cn(
        'fixed bottom-4 right-4 rounded-md p-4 text-white shadow-lg transition-all',
        bgColor,
        'animate-in slide-in-from-bottom-4 fade-in-80'
      )}
    >
      <div className="flex items-center gap-3">
        <span>{message}</span>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-white/70 hover:text-white transition-colors"
          >
            X
          </button>
        )}
      </div>
    </div>
  )
}

interface UseToastProps {
  duration?: number
}

export function useToast({ duration = 3000 }: UseToastProps = {}) {
  const [toasts, setToasts] = React.useState<ToastProps[]>([])

  const addToast = React.useCallback((props: Omit<ToastProps, 'onDismiss'>) => {
    const id = Date.now()
    setToasts(prev => [...prev, { ...props, onDismiss: () => removeToast(id) }])
    
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }
  }, [duration])

  const removeToast = React.useCallback((id: number) => {
    setToasts(prev => prev.filter((_, i) => i !== id))
  }, [])

  const success = React.useCallback((message: string) => {
    addToast({ message, type: 'success' })
  }, [addToast])

  const error = React.useCallback((message: string) => {
    addToast({ message, type: 'error' })
  }, [addToast])

  const warning = React.useCallback((message: string) => {
    addToast({ message, type: 'warning' })
  }, [addToast])

  const info = React.useCallback((message: string) => {
    addToast({ message, type: 'info' })
  }, [addToast])

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
  }
}