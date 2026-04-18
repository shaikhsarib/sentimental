import { Routes, Route } from 'react-router-dom'
import OperationRoom from './pages/OperationRoom'
import Dashboard from './pages/Dashboard'
import useStore from './store/useStore'

export default function App() {
  const { project, _hasHydrated } = useStore()

  // Prevent flicker during hydration
  if (!_hasHydrated) {
    return <div style={{ background: '#020617', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>Initialing Terminal...</div>
  }

  return (
    <div className="app-shell" style={{ display: 'block' }}>
      <Routes>
        {/* If no project, show Dashboard (Home). If project exists, enter Operation Room */}
        <Route path="/" element={project ? <OperationRoom /> : <Dashboard />} />
      </Routes>
    </div>
  )
}
