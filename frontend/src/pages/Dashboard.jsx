import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, Terminal, Activity, Database, ChevronRight, FileText } from 'lucide-react'
import useStore from '../store/useStore'

const API = import.meta.env.VITE_API_URL || ''

export default function Dashboard() {
  const { setProject, setActiveStage } = useStore()
  const [projectName, setProjectName] = useState('UNNAMED_OP')
  const [projectDesc, setProjectDesc] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [projects, setProjects] = useState([])

  useEffect(() => {
    fetch(`${API}/api/projects`)
      .then(res => res.json())
      .then(setProjects)
      .catch(console.error)
  }, [])

  const createProject = async () => {
    setIsLoading(true)
    try {
      const res = await fetch(`${API}/api/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: projectName, description: projectDesc }),
      })
      if (res.ok) {
        const data = await res.json()
        setProject(data)
        setActiveStage('identity') 
      }
    } catch (e) {
      console.error(e)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', background: 'var(--bg-surface)', padding: '60px 20px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '480px 400px', gap: '40px', alignItems: 'start' }}>
        {/* Initialization Panel */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-panel"
          style={{ padding: '48px' }}
        >
          <div style={{ display: 'inline-flex', padding: '12px', background: 'var(--text-primary)', borderRadius: '8px', color: 'white', marginBottom: '24px' }}>
            <Activity size={24} />
          </div>
          
          <h1 className="font-heading" style={{ fontSize: '24px', letterSpacing: '-0.04em', marginBottom: '8px' }}>
            SENTIMENTAL // MISSION_INIT
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '40px' }}>
            Initialize a new intelligence swarm operation.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', textAlign: 'left' }}>
            <div>
              <label style={{ display: 'block', fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: '6px' }}>
                MISSION_IDENTIFIER
              </label>
              <input 
                className="input font-mono" 
                style={{ padding: '14px', fontSize: '14px', background: 'white', width: '100%' }}
                value={projectName} 
                onChange={e => setProjectName(e.target.value)} 
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: '6px' }}>
                MISSION_OBJECTIVE
              </label>
              <textarea 
                className="input" 
                style={{ padding: '14px', fontSize: '14px', background: 'white', width: '100%', minHeight: '100px' }}
                value={projectDesc} 
                onChange={e => setProjectDesc(e.target.value)} 
                placeholder="Describe the target simulation context..."
              />
            </div>

            <button 
              className="tactical-btn" 
              style={{ padding: '16px', justifyContent: 'center', fontSize: '14px' }}
              onClick={createProject}
              disabled={isLoading}
            >
              {isLoading ? <Terminal className="animate-pulse" size={18} /> : <><Plus size={18} /> INITIALIZE_SWARM</>}
            </button>
          </div>
        </motion.div>

        {/* Mission Vault */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          style={{ background: 'white', border: '1px solid var(--border)', borderRadius: '8px', alignSelf: 'stretch' }}
        >
           <div style={{ padding: '24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="font-mono" style={{ fontSize: '12px' }}>MISSION_VAULT</div>
              <div className="pill info" style={{ fontSize: '10px' }}>{projects.length} TOTAL</div>
           </div>
           <div className="scroll-thin" style={{ maxHeight: '550px', overflowY: 'auto' }}>
              {projects.length > 0 ? projects.map(p => (
                <div 
                  key={p.project_id} 
                  style={{ padding: '20px', borderBottom: '1px solid var(--border)', cursor: 'pointer', transition: 'background 0.2s' }}
                  onClick={() => {
                    setProject(p)
                    setActiveStage('identity')
                  }}
                  className="hover-bg"
                >
                   <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <div className="font-heading" style={{ fontSize: '14px' }}>{p.name}</div>
                      <ChevronRight size={14} style={{ color: 'var(--text-muted)' }} />
                   </div>
                   <div style={{ fontSize: '11px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FileText size={10} /> {new Date(p.created_at * 1000).toLocaleDateString()}
                   </div>
                </div>
              )) : (
                <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
                   NO_MISSIONS_DETECTED
                </div>
              )}
           </div>
        </motion.div>
      </div>

      <div style={{ marginTop: '40px', display: 'flex', justifyContent: 'center', gap: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '11px' }}>
          <Database size={14} /> NEO4J_ACTIVE
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '11px' }}>
          <Activity size={14} /> SWARM_READY
        </div>
      </div>
    </div>
  )
}
