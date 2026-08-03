import React from 'react'
import { usePlatform } from '@/state/PlatformProvider'
import { StatTile } from '@/components/console/StatTile'
import { Panel } from '@/components/console/Panel'
import { PressureGauge } from '@/components/charts/PressureGauge'
import { formatMultiplier, formatNumber } from '@/lib/utils'

export default function CommandCenter() {
  const { rounds, stats, pressure, isLoading } = usePlatform()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    )
  }

  const latestRound = rounds[0]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Command Center</h2>
        <p className="text-muted-foreground">
          Real-time overview of crash game analytics
        </p>
      </div>

      {/* Stats Row */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatTile
          title="Latest Multiplier"
          value={latestRound ? formatMultiplier(latestRound.multiplier) : 'N/A'}
          subtitle={latestRound ? new Date(latestRound.timestamp).toLocaleTimeString() : ''}
        />
        <StatTile
          title="Average Multiplier"
          value={formatNumber(stats.avg_multiplier || 0)}
          subtitle="Last 1000 rounds"
        />
        <StatTile
          title="Total Rounds"
          value={stats.count || 0}
          subtitle="In database"
        />
        <StatTile
          title="Current Pressure"
          value={formatNumber(pressure.total_pressure || 0) + '%'}
          subtitle={pressure.state || 'neutral'}
        />
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Pressure Analysis */}
        <Panel title="Pressure Analysis">
          <div className="flex items-center justify-center py-8">
            <PressureGauge pressure={pressure.total_pressure || 0} size="lg" />
          </div>
          <div className="mt-6 space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">State</span>
              <span className="font-medium">{pressure.state || 'neutral'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Imminence</span>
              <span className="font-medium">{pressure.imminence || 'low'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Release Probability</span>
              <span className="font-medium">
                {(pressure.release_probability || 0).toFixed(1)}%
              </span>
            </div>
          </div>
        </Panel>

        {/* Recent Rounds */}
        <Panel title="Recent Rounds">
          <div className="space-y-3">
            {rounds.slice(0, 10).map((round, index) => (
              <div
                key={round.id || index}
                className="flex items-center justify-between p-3 rounded border bg-card/50"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground">
                    {new Date(round.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-medium">
                    {formatMultiplier(round.multiplier)}
                  </span>
                  <span
                    className="px-2 py-1 rounded text-xs"
                    style={{ backgroundColor: 'var(--band-neutral)' }}
                  >
                    {round.band || 'neutral'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* Statistics */}
      <Panel title="Statistics">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Min Multiplier</p>
            <p className="text-xl font-bold">{formatMultiplier(stats.min_multiplier || 0)}</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Max Multiplier</p>
            <p className="text-xl font-bold">{formatMultiplier(stats.max_multiplier || 0)}</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Range</p>
            <p className="text-xl font-bold">
              {formatMultiplier((stats.max_multiplier || 0) - (stats.min_multiplier || 0))}
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Std Dev</p>
            <p className="text-xl font-bold">{formatNumber(stats.std_dev || 0)}</p>
          </div>
        </div>
      </Panel>
    </div>
  )
}