import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Activity, ShieldAlert, BarChart3, Terminal, MessageSquare, Globe, ArrowRight } from 'lucide-react'
import ForceGraph2D from 'react-force-graph-2d'
import useStore from '../store/useStore'
import PersonaFeed from '../components/PersonaFeed'
import DebriefReport from '../components/DebriefReport'

const API = import.meta.env.VITE_API_URL || ''

export default function Sandbox() {
  const { project, latestRun, setLatestRun, isSimulating, setIsSimulating } = useStore()
  const [objective, setObjective] = useState('')
  const [mode, setMode] = useState('full')
  const [logs, setLogs] = useState([])
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })

  useEffect(() => {
    if (!project) return
    const fetchGraph = async () => {
      try {
        const res = await fetch(`${API}/api/projects/${project.project_id}/graph`)
        if (res.ok) {
           const data = await res.json()
           const formattedGraph = {
             nodes: (data.nodes || []).map(n => ({ 
               id: n.id, 
               title: n.label, 
               val: (n.betweenness * 50) + 5, 
               color: n.betweenness > 0.1 ? 'var(--danger)' : '#0d9488' 
             })),
             links: (data.edges || []).map(e => ({ source: e.source, target: e.target, val: e.weight }))
           }
           setGraphData(formattedGraph)
        }
      } catch (e) {}
    }
    fetchGraph()
  }, [project])

  useEffect(() => {
    if (!project || !latestRun || !isSimulating) return
    
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/api/projects/${project.project_id}/runs/${latestRun.run_id}`)
        if (res.ok) {
          const data = await res.json()
          setLatestRun(data)
          
          const dt = new Date().toISOString().split('T')[1].slice(0,8)
          setLogs(prev => [...prev, `${dt} [Engine] State: ${data.status.toUpperCase()}`].slice(-20))
          
          if (data.status !== 'running') {
            setIsSimulating(false)
            setLogs(prev => [...prev, `${dt} ✓ Simulation lifecycle complete.`].slice(-20))
            clearInterval(interval)
          }
        }
      } catch (e) {
        console.error("Polling error:", e)
      }
    }, 3000)
    
    return () => clearInterval(interval)
  }, [project, latestRun?.run_id, isSimulating])

  const startRun = async () => {
    if (!project) return alert('No project active')
    setIsSimulating(true)
    setLogs([`${new Date().toISOString().split('T')[1].slice(0,8)} Initializing Swarm Protocol...`])
    
    try {
      const res = await fetch(`${API}/api/projects/${project.project_id}/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, objective, content_type: 'social_post', industry: 'all' })
      })
      const data = await res.json()
      setLatestRun(data)
    } catch (e) {
      console.error(e)
      setIsSimulating(false)
    }
  }

  const result = latestRun?.result
  const shield = result?.mode === 'shield' ? result : result?.shield
  const macro = result?.mode === 'macro' ? result : result?.macro

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="split-view" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 500px) 1fr', gap: '24px' }}>
      
      {/* Left Column: Context & Input */}
      <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: 'fit-content' }}>
          <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={20} color="var(--accent)" /> Context Monitor
            </h2>
            <select className="select" value={mode} onChange={e => setMode(e.target.value)} style={{ width: 'auto', fontSize: '12px', padding: '4px 8px' }}>
             <option value="full">Full Swarm</option>
             <option value="shield">Shield Only</option>
             <option value="macro">Macro Only</option>
            </select>
          </div>
          
          <input className="input" value={objective} onChange={e => setObjective(e.target.value)} placeholder="Enter simulation objective..." style={{ marginBottom: '16px' }} />
          
          <div style={{ border: '1px solid var(--border)', borderRadius: '12px', background: 'rgba(0,0,0,0.2)', height: '400px', overflow: 'hidden' }}>
            {graphData.nodes.length > 0 ? (
              <ForceGraph2D
                graphData={graphData}
                nodeAutoColorBy="group"
                nodeLabel="title"
                linkColor={() => 'rgba(255,255,255,0.1)'}
                backgroundColor="transparent"
                width={500}
                height={400}
              />
            ) : (
                <div className="empty-state">No graph metrics loaded</div>
            )}
          </div>
      </div>

      {/* Right Column: Results & Live Feed */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
         {/* Status Header */}
         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="pill" style={{ background: isSimulating ? 'var(--accent-glow)' : 'rgba(255,255,255,0.05)', color: isSimulating ? 'var(--accent)' : 'var(--muted)' }}>
                {isSimulating ? '• SIMULATING SWARM' : latestRun?.status === 'completed' ? '✓ SIMULATION COMPLETE' : 'SYSTEM READY'}
            </div>
            {!isSimulating && (
              <button className="btn" onClick={startRun} disabled={!project}>
                <Play size={14} /> Ignite Simulation
              </button>
            )}
         </div>

         {/* Metric Grid */}
         <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="glass-panel" style={{ padding: '16px' }}>
               <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent)', fontSize: '12px', fontWeight: 600, marginBottom: '12px' }}>
                 <Globe size={14} /> VIRALITY DEPTH
               </div>
               <div style={{ fontSize: '24px', fontWeight: 700 }}>
                 {shield ? shield.graph_cascade?.peak_outreach.toLocaleString() : '0'}
               </div>
               <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '4px' }}>Peak Projected Outreach</div>
            </div>
            <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column' }}>
               <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-amber)', fontSize: '12px', fontWeight: 600, marginBottom: '12px' }}>
                 <Activity size={14} /> LIVE AGENTS
               </div>
               <div style={{ flex: 1, overflowY: 'auto', minHeight: '100px' }}>
                  {latestRun && <PersonaFeed runId={latestRun.run_id} />}
                  {!latestRun && <div style={{ fontSize: '11px', color: 'var(--muted)', textAlign: 'center', marginTop: '20px' }}>Standing by...</div>}
               </div>
            </div>
         </div>

         {/* Middle: Results Canvas */}
         <div className="glass-panel" style={{ flex: 1, minHeight: '300px', padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div className="workbench-header">
               <BarChart3 size={14} /> Analytical Outcomes
            </div>
            <div style={{ padding: '24px', overflowY: 'auto', flex: 1 }}>
               {!latestRun && <div className="empty-state">No simulation data available</div>}
               {latestRun && latestRun.status === 'running' && (
                 <div className="empty-state" style={{ animation: 'pulse-glow 2s infinite' }}>
                   Analyzing world-state dynamics...
                 </div>
               )}
               {latestRun && latestRun.status === 'completed' && (
                  <DebriefReport runResult={latestRun.result} />
               )}
            </div>
         </div>

         {/* Bottom: Logs */}
         <div style={{ height: '150px', background: '#020617', border: '1px solid var(--border)', borderRadius: '12px', padding: '12px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
           <div style={{ display: 'flex', gap: '8px', color: 'var(--muted)', fontSize: '11px', marginBottom: '8px', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
             <Terminal size={14} /> LIVE MONITOR
           </div>
           <div className="mono-text" style={{ fontSize: '12px', color: 'var(--muted)', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {logs.map((log, i) => <div key={i}>&gt; {log}</div>)}
              {logs.length === 0 && <div style={{ opacity: 0.3 }}>&gt; Awaiting ignition...</div>}
           </div>
         </div>
      </div>

    </motion.div>
  )
}
