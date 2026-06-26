import { Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { Dashboard } from './pages/Dashboard'
import { OperationPage } from './pages/OperationPage'
import { SetupManager } from './pages/SetupManager'
import { PatternAnalysis } from './pages/PatternAnalysis'
import { Calculator } from './pages/Calculator'
import { Settings } from './pages/Settings'
import { Login } from './pages/Login'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="trade" element={<OperationPage />} />
        <Route path="setups" element={<SetupManager />} />
        <Route path="patterns" element={<PatternAnalysis />} />
        <Route path="calculator" element={<Calculator />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
