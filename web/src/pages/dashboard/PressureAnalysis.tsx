import React from 'react'
import { usePlatform } from '@/state/PlatformProvider'
import { Panel } from '@/components/console/Panel'
import { PressureGauge, PressureBar } from '@/components/charts/PressureGauge'
import { formatNumber } from '@/lib/utils'

export default function PressureAnalysis() {
  const { pressure, isLoading } = usePlatform()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading pressure data...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Pressure Analysis</h2>
        <p className="text-muted-foreground">
          Detailed pressure metrics and predictions
        </p>
      </div>

      {/* Overview */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Pressure Gauge">
          <div className="flex flex-col items-center py-8">
            <PressureGauge pressure={pressure.total_pressure || 0} size="lg" showLabel />
            <div className="mt-6 grid gap-4 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Pressure</span>
                <span className="font-medium">
                  {formatNumber(pressure.total_pressure || 0)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Overflow</span>
                <span className="font-medium">
                  {formatNumber(pressure.overflow || 0)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">State</span>
                <span className="font-medium">{pressure.state || 'neutral'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Imminence</span>
                <span className="font-medium">{pressure.imminence || 'low'}</span>
              </div>
            </div>
          </div>
        </Panel>

        <Panel title="Ceiling Analysis">
          <div className="space-y-4">
            {pressure.ceiling_results?.map((ceiling: any, index: number) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-medium">
                    {formatNumber(ceiling.ceiling_value)}x
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {ceiling.arch_type}
                  </span>
                </div>
                <PressureBar pressure={ceiling.pressure_score} />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Hits: {ceiling.hits}</span>
                  <span>Verified: {ceiling.is_verified ? 'Yes' : 'No'}</span>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* Predictions */}
      {pressure.predictions && pressure.predictions.length > 0 && (
        <Panel title="Release Predictions">
          <div className="grid gap-4 md:grid-cols-2">
            {pressure.predictions.map((prediction: any, index: number) => (
              <div key={index} className="p-4 rounded border bg-card/50">
                <h4 className="font-medium mb-2">{prediction.type}</h4>
                {prediction.type === 'release_range' && (
                  <div className="space-y-1">
                    <p>
                      <span className="text-muted-foreground">Min:</span> 
                      {formatNumber(prediction.min)}x
                    </p>
                    <p>
                      <span className="text-muted-foreground">Max:</span> 
                      {formatNumber(prediction.max)}x
                    </p>
                    <p>
                      <span className="text-muted-foreground">Confidence:</span> 
                      {formatNumber(prediction.confidence * 100)}%
                    </p>
                  </div>
                )}
                {prediction.type === 'release_timing' && (
                  <div className="space-y-1">
                    <p>
                      <span className="text-muted-foreground">Timing:</span> 
                      {prediction.timing}
                    </p>
                    <p>
                      <span className="text-muted-foreground">Confidence:</span> 
                      {formatNumber(prediction.confidence * 100)}%
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Panel>
      )}

      {/* Detailed Metrics */}
      <Panel title="Pressure Details">
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Release Probability</p>
            <p className="text-2xl font-bold">
              {(pressure.release_probability || 0).toFixed(1)}%
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Overflow Percent</p>
            <p className="text-2xl font-bold">
              {formatNumber(pressure.overflow_percent || 0)}%
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Ceilings Tracked</p>
            <p className="text-2xl font-bold">
              {pressure.ceiling_results?.length || 0}
            </p>
          </div>
        </div>
      </Panel>
    </div>
  )
}