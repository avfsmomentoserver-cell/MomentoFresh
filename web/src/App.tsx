import { Routes, Route } from 'react-router-dom'
import { PlatformProvider } from './state/PlatformProvider'
import AppLayout from './components/layout/AppLayout'
import CommandCenter from './pages/dashboard/CommandCenter'
import PressureAnalysis from './pages/dashboard/PressureAnalysis'
import BacktestStudio from './pages/dashboard/BacktestStudio'
import Settings from './pages/dashboard/Settings'
import Ingest from './pages/dashboard/Ingest'
import Login from './pages/auth/Login'

function App() {
  return (
    <PlatformProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<AppLayout />}>
          <Route index element={<CommandCenter />} />
          <Route path="pressure" element={<PressureAnalysis />} />
          <Route path="backtest" element={<BacktestStudio />} />
          <Route path="ingest" element={<Ingest />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </PlatformProvider>
  )
}

export default App