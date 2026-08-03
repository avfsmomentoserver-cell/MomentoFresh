import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number, decimals: number = 2): string {
  return num.toFixed(decimals)
}

export function formatPercentage(num: number, decimals: number = 2): string {
  return (num * 100).toFixed(decimals) + '%'
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString()
}

export function formatMultiplier(multiplier: number): string {
  return multiplier.toFixed(2) + 'x'
}

export function getBandColor(band: string): string {
  const colors: Record<string, string> = {
    'ultra-crash': '#ef4444',
    'crash': '#f87171',
    'deep-low': '#fca5a5',
    'low': '#fbbf24',
    'neutral': '#64748b',
    'mid': '#86efac',
    'high': '#4ade80',
    'ignition': '#22c55e',
    'moonshot': '#16a34a',
    'stratospheric': '#15803d',
  }
  return colors[band] || '#64748b'
}

export function getPressureColor(pressure: number): string {
  if (pressure >= 90) return '#ef4444'
  if (pressure >= 70) return '#f87171'
  if (pressure >= 50) return '#fbbf24'
  if (pressure >= 30) return '#86efac'
  return '#22c55e'
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}