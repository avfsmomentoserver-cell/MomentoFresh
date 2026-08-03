import React from 'react'
import { cn, getPressureColor } from '@/lib/utils'

interface PressureGaugeProps {
  pressure: number
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export function PressureGauge({
  pressure,
  size = 'md',
  showLabel = true,
}: PressureGaugeProps) {
  const sizeClasses = {
    sm: 'w-20 h-20',
    md: 'w-32 h-32',
    lg: 'w-48 h-48',
  }

  const gaugeSize = sizeClasses[size]
  const strokeWidth = size === 'sm' ? 6 : size === 'md' ? 8 : 10
  const radius = size === 'sm' ? 30 : size === 'md' ? 50 : 75
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (pressure / 100) * circumference

  const pressureColor = getPressureColor(pressure)

  return (
    <div className="flex flex-col items-center">
      <div className="relative inline-flex items-center justify-center">
        <svg className={cn('absolute', gaugeSize)} viewBox="0 0 120 120">
          <circle
            className="text-muted-foreground/20"
            strokeWidth={strokeWidth}
            stroke="currentColor"
            fill="none"
            r={radius}
            cx="60"
            cy="60"
          />
          <circle
            className="text-primary"
            strokeWidth={strokeWidth}
            stroke={pressureColor}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            r={radius}
            cx="60"
            cy="60"
            style={{ transition: 'stroke-dashoffset 0.35s' }}
          />
        </svg>
        <div className="absolute text-2xl font-bold" style={{ color: pressureColor }}>
          {pressure.toFixed(0)}%
        </div>
      </div>
      {showLabel && (
        <div className="mt-2 text-sm text-muted-foreground">
          Pressure
        </div>
      )}
    </div>
  )
}

export function PressureBar({ pressure, className }: { pressure: number; className?: string }) {
  const pressureColor = getPressureColor(pressure)

  return (
    <div className={cn('h-4 w-full rounded-full bg-muted overflow-hidden', className)}>
      <div
        className="h-full rounded-full transition-all"
        style={{ width: pressure + '%', backgroundColor: pressureColor }}
      />
    </div>
  )
}