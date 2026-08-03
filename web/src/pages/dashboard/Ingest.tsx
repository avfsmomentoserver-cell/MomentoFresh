import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Panel } from '@/components/console/Panel'
import { usePlatform } from '@/state/PlatformProvider'
import { useToast } from '@/components/ui/toast'

export default function Ingest() {
  const { currentSource } = usePlatform()
  const { success, error } = useToast()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<Record<string, any>>({})

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true)

    try {
      for (const file of acceptedFiles) {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: { status: 'uploading', progress: 0 }
        }))

        const formData = new FormData()
        formData.append('file', file)
        formData.append('source', currentSource)

        const response = await fetch('/api/v1/ingest/file', {
          method: 'POST',
          body: formData,
        })

        const result = await response.json()

        setUploadProgress(prev => ({
          ...prev,
          [file.name]: { status: 'completed', result }
        }))

        success(`Ingested ${result.count} rounds from ${file.name}`)
      }
    } catch (err) {
      error('Failed to upload files')
    } finally {
      setIsUploading(false)
    }
  }, [currentSource, success, error])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'text/csv': ['.csv'],
    },
    maxFiles: 10,
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Data Ingest</h2>
        <p className="text-muted-foreground">
          Upload crash game data files for analysis
        </p>
      </div>

      {/* Dropzone */}
      <Panel title="Upload Files">
        <div
          {...getRootProps()}
          className={{
            border: '2px dashed',
            borderColor: isDragActive ? 'var(--primary)' : 'var(--border)',
            rounded: 'lg',
            p: 8,
            textCenter: true,
            cursor: 'pointer',
            transition: 'border-color 0.2s',
          }}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p className="text-lg font-medium">Drop the files here ...</p>
          ) : (
            <div className="space-y-2">
              <p className="text-lg font-medium">Drag & drop files here, or click to select</p>
              <p className="text-sm text-muted-foreground">
                Supports: .json, .csv (Max 10 files)
              </p>
            </div>
          )}
        </div>
      </Panel>

      {/* Upload Progress */}
      {Object.keys(uploadProgress).length > 0 && (
        <Panel title="Upload Progress">
          <div className="space-y-4">
            {Object.entries(uploadProgress).map(([filename, progress]) => (
              <div
                key={filename}
                className="flex items-center justify-between p-3 rounded border bg-card/50"
              >
                <div>
                  <p className="font-medium">{filename}</p>
                  <p className="text-sm text-muted-foreground">
                    {progress.status}
                  </p>
                </div>
                {progress.status === 'completed' && (
                  <div className="text-right">
                    <p className="font-medium">
                      {progress.result?.count || 0} rounds
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Panel>
      )}

      {/* Manual Ingest */}
      <Panel title="Manual Data Entry">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground mb-4">
            Enter round data manually (JSON format)
          </p>
          <textarea
            className="w-full p-3 rounded-md border border-input bg-background text-foreground"
            rows={10}
            placeholder={'[{
  "timestamp": "2024-01-01T00:00:00Z",
  "multiplier": 2.5,
  "source": "aviator"
}]'}
            id="manual-data"
          />
          <Button
            onClick={async () => {
              const textarea = document.getElementById('manual-data') as HTMLTextAreaElement
              try {
                const data = JSON.parse(textarea.value)
                const response = await api.ingest.rounds(data, currentSource)
                success(`Ingested ${response.count} rounds`)
                textarea.value = ''
              } catch (err) {
                error('Invalid JSON format')
              }
            }}
            disabled={isUploading}
          >
            Ingest Data
          </Button>
        </div>
      </Panel>

      {/* Current Source */}
      <Panel title="Current Settings">
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Current Source</span>
            <span className="font-medium">{currentSource}</span>
          </div>
        </div>
      </Panel>
    </div>
  )
}