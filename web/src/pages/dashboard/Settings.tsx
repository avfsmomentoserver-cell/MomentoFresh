import React, { useState, useEffect } from 'react'
import { Panel } from '@/components/console/Panel'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { usePlatform } from '@/state/PlatformProvider'

export default function Settings() {
  const { sources, currentSource, setCurrentSource } = usePlatform()
  const [newSource, setNewSource] = useState({ name: '', displayName: '' })

  const handleCreateSource = async () => {
    if (!newSource.name) return
    
    try {
      // In production, this would call the API
      // For now, just show the new source in the list
      setNewSource({ name: '', displayName: '' })
    } catch (error) {
      console.error('Failed to create source:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Settings</h2>
        <p className="text-muted-foreground">
          Configure MomentoFresh platform
        </p>
      </div>

      {/* Data Sources */}
      <Panel title="Data Sources">
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="source-name">Source Name</Label>
              <Input
                id="source-name"
                value={newSource.name}
                onChange={(e) => 
                  setNewSource({ ...newSource, name: e.target.value })
                }
                placeholder="aviator"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="display-name">Display Name</Label>
              <Input
                id="display-name"
                value={newSource.displayName}
                onChange={(e) => 
                  setNewSource({ ...newSource, displayName: e.target.value })
                }
                placeholder="Aviator"
              />
            </div>
          </div>
          <Button
            onClick={handleCreateSource}
            disabled={!newSource.name}
          >
            Add Source
          </Button>

          <div className="border-t pt-4 mt-6">
            <h4 className="font-semibold mb-2">Existing Sources</h4>
            {sources.length > 0 ? (
              <div className="grid gap-2">
                {sources.map((source: any) => (
                  <div
                    key={source.name}
                    className={{
                      p: 3,
                      rounded: 'md',
                      border: true,
                      bg: currentSource === source.name ? 'var(--accent)' : 'transparent',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s',
                    }}
                    onClick={() => setCurrentSource(source.name)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">{source.display_name || source.name}</p>
                        <p className="text-sm text-muted-foreground">{source.name}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className={{
                            px: 2,
                            py: 1,
                            rounded: 'full',
                            text: 'xs',
                            bg: source.active ? 'var(--green-500)' : 'var(--muted)',
                          }}
                        >
                          {source.active ? 'Active' : 'Inactive'}
                        </span>
                        {currentSource === source.name && (
                          <span className="text-primary">Current</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-4">
                No sources configured
              </p>
            )}
          </div>
        </div>
      </Panel>

      {/* Platform Settings */}
      <Panel title="Platform Settings">
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>Version</Label>
              <p className="p-3 rounded border bg-card/50">4.0.0</p>
            </div>
            <div className="space-y-2">
              <Label>Environment</Label>
              <p className="p-3 rounded border bg-card/50">
                {import.meta.env.MODE || 'development'}
              </p>
            </div>
          </div>
          <div className="space-y-2">
            <Label>API Base URL</Label>
            <p className="p-3 rounded border bg-card/50 font-mono text-sm">
              {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
            </p>
          </div>
          <div className="space-y-2">
            <Label>WebSocket URL</Label>
            <p className="p-3 rounded border bg-card/50 font-mono text-sm">
              {import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}
            </p>
          </div>
        </div>
      </Panel>
    </div>
  )
}