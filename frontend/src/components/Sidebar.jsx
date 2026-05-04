import { useState, useEffect } from 'react'
import { 
  Folder, 
  FileText, 
  History, 
  LayoutGrid, 
  ChevronLeft, 
  ChevronRight,
  Plus,
  Compass
} from 'lucide-react'
import useStore from '../store/useStore'

const API = import.meta.env.VITE_API_URL || ''

export default function Sidebar() {
  const { 
    project, 
    setProject, 
    sidebarOpen, 
    setSidebarOpen, 
    selectedRunId, 
    setSelectedRunId,
    activeStage,
    setActiveStage 
  } = useStore()

  const [runs, setRuns] = useState([])
  const [docs, setDocs] = useState([])

  useEffect(() => {
    if (project?.project_id) {
       fetch(`${API}/api/projects/${project.project_id}/runs`)
         .then(res => res.json())
         .then(setRuns)
         .catch(console.error)
       
       // Documents are usually in the project object, but we could fetch list
       setDocs(project.documents || [])
    }
  }, [project, selectedRunId])

  if (!sidebarOpen) {
    return (
      <button 
        className="sidebar-toggle-closed"
        onClick={() => setSidebarOpen(true)}
      >
        <ChevronRight size={16} />
      </button>
    )
  }

  return (
    <aside className="workspace-sidebar">
      <div className="sidebar-header">
        <div className="project-brand">
          <Compass size={18} className="text-accent" />
          <div className="project-name">{project?.name || 'SENTIMENTAL'}</div>
        </div>
        <button className="icon-btn" onClick={() => setSidebarOpen(false)}>
          <ChevronLeft size={16} />
        </button>
      </div>

      <div className="sidebar-content scroll-thin">
        {/* V6 Institutional Section */}
        <section className="sidebar-section">
          <div className="section-header text-blue-400">V6 INSTITUTIONAL</div>
          <div className="nav-list">
             <a 
               href="/v6/upload"
               className="nav-item no-underline"
               style={{ color: 'inherit', textDecoration: 'none' }}
             >
                <LayoutGrid size={14} className="text-blue-500" /> Million-Agent Swarm
             </a>
          </div>
        </section>

        {/* Navigation Section */}
        <section className="sidebar-section">
          <div className="section-header">WORKSPACE</div>
          <div className="nav-list">
             <button 
               className={`nav-item ${activeStage === 'identity' ? 'active' : ''}`}
               onClick={() => setActiveStage('identity')}
             >
                <LayoutGrid size={14} /> Intelligence Hub
             </button>
             <button 
               className={`nav-item ${['intelligence', 'world'].includes(activeStage) ? 'active' : ''}`}
               onClick={() => setActiveStage('intelligence')}
             >
                <Folder size={14} /> Knowledge Graph
             </button>
             <button 
               className={`nav-item ${activeStage === 'swarm' ? 'active' : ''}`}
               onClick={() => setActiveStage('swarm')}
             >
                <Compass size={14} /> Swarm Simulation
             </button>
          </div>
        </section>

        {/* Documents Section */}
        <section className="sidebar-section">
          <div className="section-header">
            <span>DOCUMENTS</span>
            <Plus size={12} className="cursor-pointer hover:text-white" />
          </div>
          <div className="item-list">
            {docs.map((doc, i) => (
              <div key={i} className="list-item">
                <FileText size={12} />
                <span className="truncate">{doc.title}</span>
              </div>
            ))}
            {docs.length === 0 && <div className="empty-state">No docs uploaded</div>}
          </div>
        </section>

        {/* History Section */}
        <section className="sidebar-section">
          <div className="section-header">RUN HISTORY</div>
          <div className="item-list">
            {runs.map((run) => (
              <div 
                key={run.run_id} 
                className={`list-item run-item ${selectedRunId === run.run_id ? 'active' : ''}`}
                onClick={() => setSelectedRunId(run.run_id)}
              >
                <History size={12} />
                <div className="run-info">
                   <div className="run-title truncate">{run.objective || 'General Scan'}</div>
                   <div className="run-meta">{new Date(run.created_at * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
              </div>
            ))}
            {runs.length === 0 && <div className="empty-state">No previous runs</div>}
          </div>
        </section>
      </div>

      <div className="sidebar-footer">
        <button className="ghost-btn" onClick={() => setProject(null)}>Exit Workspace</button>
      </div>
    </aside>
  )
}
