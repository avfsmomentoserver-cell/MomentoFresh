import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Panel } from '@/components/console/Panel'
import { usePlatform } from '@/state/PlatformProvider'
import { formatNumber } from '@/lib/utils'

export default function BacktestStudio() {
  const { currentSource } = usePlatform()
  const [config, setConfig] = useState({
    name: 'Quick Test',
    source: currentSource,
    rounds_limit: 1000,
  })
  const [result, setResult] = useState<any>(null)
  const [isRunning, setIsRunning] = useState(false)

  const handleRunBacktest = async () => {
    setIsRunning(true)
    setResult(null)

    try {
      const response = await api.backtest.run(config)
      setResult(response)
    } catch (error) {
      console.error('Backtest failed:', error)
    } finally {
      setIsRunning(false)
    }
  }

  const handleSimpleTest = async () => {
    setIsRunning(true)
    try {
      const response = await api.backtest.simple(currentSource, 1000)
      setResult(response)
    } catch (error) {
      console.error('Simple backtest failed:', error)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Backtest Studio</h2>
        <p className="text-muted-foreground">
          Test strategies and analyze performance
        </p>
      </div>

      {/* Configuration */}
      <Panel title="Backtest Configuration">
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="name">Backtest Name</Label>
              <Input
                id="name"
                value={config.name}
                onChange={(e) => setConfig({ ...config, name: e.target.value })}
                placeholder="My Backtest"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="source">Data Source</Label>
              <Input
                id="source"
                value={config.source}
                onChange={(e) => setConfig({ ...config, source: e.target.value })}
                placeholder="aviator"
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="rounds_limit">Rounds Limit</Label>
            <Input
              id="rounds_limit"
              type="number"
              value={config.rounds_limit}
              onChange={(e) => 
                setConfig({ ...config, rounds_limit: parseInt(e.target.value) || 0 })
              }
              placeholder="1000"
            />
          </div>
          <Button
            onClick={handleRunBacktest}
            disabled={isRunning}
            className="w-full md:w-auto"
          >
            {isRunning ? 'Running...' : 'Run Backtest'}
          </Button>
          <Button
            onClick={handleSimpleTest}
            disabled={isRunning}
            variant="outline"
            className="w-full md:w-auto"
          >
            Run Simple Test
          </Button>
        </div>
      </Panel>

      {/* Results */}
      {result && (
        <Panel title="Backtest Results">
          <div className="space-y-6">
            {/* Summary */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="font-medium">{result.status}</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Duration</p>
                <p className="font-medium">
                  {formatNumber(result.duration_seconds || 0)}s
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Signals Detected</p>
                <p className="font-medium">{result.signal_results?.length || 0}</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Metrics Calculated</p>
                <p className="font-medium">{result.metric_results?.length || 0}</p>
              </div>
            </div>

            {/* Metrics */}
            {result.metric_results && result.metric_results.length > 0 && (
              <div>
                <h4 className="font-semibold mb-4">Performance Metrics</h4>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {result.metric_results.map((metric: any, index: number) => (
                    <div key={index} className="p-4 rounded border bg-card/50">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium">{metric.name}</span>
                        <span className="text-sm text-muted-foreground">
                          {metric.unit}
                        </span>
                      </div>
                      <p className="text-2xl font-bold">
                        {formatNumber(metric.value)}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {metric.better_is_higher ? 'Higher is better' : 'Lower is better'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Signals */}
            {result.signal_results && result.signal_results.length > 0 && (
              <div>
                <h4 className="font-semibold mb-4">Detected Signals</h4>
                <div className="grid gap-2">
                  {result.signal_results.map((signal: any, index: number) => (
                    <div
                      key={index}
                      className="p-3 rounded border bg-card/50 flex justify-between items-center"
                    >
                      <div>
                        <p className="font-medium">{signal.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {signal.signal_type}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">
                          {formatNumber(signal.confidence * 100)}%
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Confidence
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Summary */}
            {result.summary && (
              <div>
                <h4 className="font-semibold mb-4">Summary</h4>
                <pre className="p-4 rounded bg-muted/50 text-sm overflow-auto">
                  {JSON.stringify(result.summary, null, 2)}
                </pre>
              </div>
            )}

            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <div>
                <h4 className="font-semibold mb-4">Recommendations</h4>
                <ul className="list-disc list-inside space-y-2 p-4 rounded bg-muted/50">
                  {result.recommendations.map((rec: string, index: number) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Panel>
      )}
    </div>
  )
}