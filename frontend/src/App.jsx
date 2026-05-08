import { Routes, Route } from 'react-router-dom'
import OperationRoom from './pages/OperationRoom'
import Dashboard from './pages/Dashboard'
import V6Upload from './pages/V6Upload'
import V6Beginner from './pages/V6Beginner'
import V6Debate from './pages/V6Debate'
import V6Query from './pages/V6Query'
import AgentExplorer from './pages/AgentExplorer'
import FlowHub from './pages/FlowHub'
import useStore from './store/useStore'

export default function App() {
  const { project, _hasHydrated } = useStore()

  // Prevent flicker during hydration
  if (!_hasHydrated) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#020617] text-gray-500 font-mono">
        INITIALIZING TERMINAL...
      </div>
    )
  }

  return (
    <div className="app-shell" style={{ display: 'block' }}>
      <Routes>
        <Route path="/" element={project ? <OperationRoom /> : <FlowHub />} />
        <Route path="/v5" element={project ? <OperationRoom /> : <Dashboard />} />
        
        {/* V6 Institutional Intelligence Routes */}
        <Route path="/v6/start" element={<V6Beginner />} />
        <Route path="/v6/upload" element={<V6Upload />} />
        <Route path="/v6/debate/:projectId" element={<V6Debate />} />
        <Route path="/v6/query/:projectId" element={<V6Query />} />
        <Route path="/v6/explorer" element={<AgentExplorer />} />
      </Routes>
    </div>
  )
}
