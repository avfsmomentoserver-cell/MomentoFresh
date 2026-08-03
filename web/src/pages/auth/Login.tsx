import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      // In production, this would call the actual login API
      // For now, just navigate to the dashboard
      if (username && password) {
        localStorage.setItem('isAuthenticated', 'true')
        navigate('/')
      } else {
        setError('Please enter username and password')
      }
    } catch (err) {
      setError('Login failed. Please try again.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 space-y-8 border rounded-lg bg-card">
        <div className="text-center">
          <h1 className="text-3xl font-bold">MomentoFresh</h1>
          <p className="text-muted-foreground mt-2">
            Advanced Analytics & Forecasting Platform
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password"
            />
          </div>

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          <Button type="submit" className="w-full">
            Sign In
          </Button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          Default credentials: admin / momento
        </p>
      </div>
    </div>
  )
}