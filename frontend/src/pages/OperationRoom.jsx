import { useEffect, useState, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Shield, 
  Search, 
  Users, 
  Activity, 
  FileText, 
  ChevronRight, 
  AlertCircle,
  Terminal,
  Database,
  Zap
} from 'lucide-react'
import useStore from '../store/useStore'
import ForceGraph2D from 'react-force-graph-2d'
import PersonaFeed from '../components/PersonaFeed'
import PopulationChart from '../components/PopulationChart'

const API = import.meta.env.VITE_API_URL || ''

export default function OperationRoom() {
  const { project, activeStage, setActiveStage, activeNode, setActiveNode, latestRun } = useStore()
  const fgRef = useRef()
  
  const [dimensions, setDimensions] = useState({ width: window.innerWidth, height: window.innerHeight })

  useEffect(() => {
    const handleResize = () => setDimensions({ width: window.innerWidth, height: window.innerHeight })
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])
  const stages = [
    { id: 'identity', label: 'IDENTITY', icon: FileText },
    { id: 'intelligence', label: 'INTELLIGENCE', icon: Database },
    { id: 'world', label: 'WORLD', icon: Users },
    { id: 'swarm', label: 'SWARM', icon: Activity },
    { id: 'interaction', label: 'DEBRIEF', icon: Search }
  ]

  // State for mission initialization
  const [content, setContent] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [ontology, setOntology] = useState(null)
  const [narrativeSpark, setNarrativeSpark] = useState('')
  const [missionSummary, setMissionSummary] = useState(null)
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [personaWeights, setPersonaWeights] = useState({})

  const templates = [
    { label: 'MARKET_VOLATILITY', text: 'A sudden liquidity crisis strikes the sector. Risk perception is at an all-time high.' },
    { label: 'POLICY_LEAK', text: 'Confidential regulatory documents have been leaked. Public trust is fracturing.' },
    { label: 'CULTURAL_DRIFT', text: 'A viral grassroots movement is emerging that challenges existing authority nodes.' }
  ]

  // --- Tactical Graph Rendering ---
  const handleNodeClick = useCallback((node) => {
    const distance = 40
    const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z)
    if (fgRef.current) {
        fgRef.current.centerAt(node.x, node.y, 1000)
        fgRef.current.zoom(4, 1000)
    }
    setActiveNode(node)
  }, [fgRef, setActiveNode])

  const renderNode = useCallback((node, ctx, globalScale) => {
    const label = node.id
    const fontSize = 12 / globalScale
    ctx.font = `${fontSize}px var(--font-mono)`
    const textWidth = ctx.measureText(label).width
    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2)
    
    // Draw Pulse for active/high-risk nodes
    const isHighRisk = node.risk >= 7 || activeNode?.id === node.id
    if (isHighRisk) {
      const pulseSec = Date.now() / 1000
      const radius = 6 + Math.sin(pulseSec * 4) * 2
      ctx.beginPath()
      ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false)
      ctx.strokeStyle = activeNode?.id === node.id ? '#000' : 'rgba(239, 68, 68, 0.4)'
      ctx.lineWidth = 1 / globalScale
      ctx.stroke()
    }

    // Node core
    ctx.beginPath()
    ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false)
    ctx.fillStyle = activeNode?.id === node.id ? '#000' : (node.risk >= 7 ? '#ef4444' : '#64748b')
    ctx.fill()

    // Label logic (Selective Clarity)
    if (globalScale > 2 || isHighRisk) {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
      ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2 - 8, ...bckgDimensions)
      ctx.fillStyle = '#000'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(label, node.x, node.y - 8)
    }
  }, [activeNode])

  const renderLink = useCallback((link, ctx, globalScale) => {
    const MAX_WIDTH = 2
    const width = Math.max(0.5, MAX_WIDTH / globalScale)
    
    ctx.beginPath()
    ctx.moveTo(link.source.x, link.source.y)
    ctx.lineTo(link.target.x, link.target.y)
    ctx.strokeStyle = 'rgba(203, 213, 225, 0.4)'
    ctx.lineWidth = width
    ctx.stroke()

    // Signal Pulse (Swarm Mode)
    if (activeStage === 'swarm') {
      const t = (Date.now() / 2000) % 1
      const x = link.source.x + (link.target.x - link.source.x) * t
      const y = link.source.y + (link.target.y - link.source.y) * t
      
      ctx.beginPath()
      ctx.arc(x, y, 1.5, 0, 2 * Math.PI)
      ctx.fillStyle = 'var(--success)'
      ctx.fill()
    }
  }, [activeStage])

  const handleSynthesize = async () => {
    if (!latestRun) return
    setIsProcessing(true)
    try {
      const res = await fetch(`${API}/api/projects/${project.project_id}/runs/${latestRun.run_id}/summarize`, { method: 'POST' })
      if (res.ok) {
        const data = await res.json()
        setMissionSummary(data)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleInitialize = async () => {
    if (!content && !project?.documents?.length) return
    setIsProcessing(true)
    
    try {
      if (content) {
        await fetch(`${API}/api/projects/${project.project_id}/documents/text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: 'MISSION_SEED', content })
        })
      }
      
      const res = await fetch(`${API}/api/projects/${project.project_id}/ontology`, { method: 'POST' })
      if (res.ok) {
        const data = await res.json()
        setOntology(data)
        setActiveStage('intelligence')
      }
    } catch (e) {
      console.error(e)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleLaunchSwarm = async () => {
    setIsProcessing(true)
    try {
      const res = await fetch(`${API}/api/projects/${project.project_id}/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: 'shield',
          objective: narrativeSpark || 'General behavioral scan',
          content_type: 'NARRATIVE_INJECTION',
          industry: 'GENERAL',
          calibration_overrides: personaWeights
        })
      })
      if (res.ok) {
        const run = await res.json()
        useStore.getState().setLatestRun(run)
        setActiveStage('swarm')
      }
    } catch (e) { console.error(e) }
    finally { setIsProcessing(false) }
  }

  useEffect(() => {
    const loadGraph = async () => {
      if (activeStage === 'intelligence' || activeStage === 'swarm') {
         const res = await fetch(`${API}/api/projects/${project.project_id}/graph`)
         if (res.ok) {
           const data = await res.json()
           // Graph data formatting (nodes/edges)
           setGraphData({
             nodes: data.nodes.map(n => ({ id: n.id, ...n })),
             links: data.links || data.edges || []
           })
         }
      }
    }
    loadGraph()
  }, [activeStage, project?.project_id])

  return (
    <div className="operation-room">
      {/* 1. Tactical Mission Path */}
      <nav className="mission-path">
        <div style={{ marginRight: 'auto', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Shield size={18} />
          <div className="font-heading" style={{ fontSize: '14px', fontWeight: 700 }}>
            SENTIMENT // {project?.name || 'INITIALIZING'}
          </div>
        </div>
        
        {stages.map((stage, idx) => {
          const Icon = stage.icon
          const isActive = activeStage === stage.id
          
          return (
            <div 
              key={stage.id} 
              className={`mission-step ${isActive ? 'active' : ''}`}
            >
              <div className="step-num">{idx + 1}</div>
              <Icon size={14} />
              <span>{stage.label}</span>
              {idx < stages.length - 1 && <ChevronRight size={12} style={{ marginLeft: '8px' }} />}
            </div>
          )
        })}
      </nav>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* 2. Central Intelligence Canvas */}
        <div className="graph-container" style={{ position: 'relative' }}>
          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            nodeCanvasObject={renderNode}
            linkCanvasObject={renderLink}
            backgroundColor="#ffffff"
            width={dimensions.width - (activeStage === 'swarm' ? 380 : 0)}
            height={dimensions.height - 56}
            onNodeClick={handleNodeClick}
            cooldownTicks={100}
            d3AlphaDecay={0.02}
            d3VelocityDecay={0.3}
          />

          {/* Tactical Overlays */}
          <AnimatePresence>
            {activeStage === 'identity' && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="tactical-overlay"
                style={{ top: '60px' }}
              >
                <div className="glass-panel" style={{ padding: '32px', borderLeft: '4px solid var(--text-primary)' }}>
                  <h2 className="font-heading" style={{ fontSize: '20px', marginBottom: '8px' }}>IDENTITY_SEED</h2>
                  <div style={{ borderLfet: '1px solid var(--border)', paddingLeft: '12px', marginBottom: '20px' }}>
                     <p style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
                        Bootstrap the mission context with raw intelligence data.
                     </p>
                  </div>
                  
                  <textarea 
                    className="input font-mono scroll-thin"
                    placeholder="Enter mission raw intelligence or paste dataset content..."
                    style={{ width: '100%', minHeight: '160px', padding: '16px', fontSize: '13px', border: '1px solid var(--border)', borderRadius: '4px', background: '#fafafa', marginBottom: '24px', position: 'relative', outline: 'none' }}
                    value={content}
                    onChange={e => setContent(e.target.value)}
                  />

                  <button 
                    className="tactical-btn" 
                    style={{ width: '100%', padding: '14px', justifyContent: 'center' }} 
                    onClick={handleInitialize}
                    disabled={isProcessing}
                  >
                    {isProcessing ? <Terminal className="animate-pulse" size={18} /> : 'GENERATE_SWARM_ONTOLOGY'}
                  </button>
                </div>
              </motion.div>
            )}

            {activeStage === 'intelligence' && ontology && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="tactical-overlay"
                style={{ top: '60px' }}
              >
                <div className="glass-panel" style={{ padding: '32px', borderLeft: '4px solid var(--accent-secondary)' }}>
                  <h2 className="font-heading" style={{ fontSize: '20px', marginBottom: '8px' }}>INTELLIGENCE_ONTOLOGY</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '24px' }}>
                    Verify the extracted semantic schema for this mission.
                  </p>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
                    <div>
                      <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '8px' }}>ENTITY_TYPES</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {ontology.entity_types.map(t => <span key={t} className="pill info">{t}</span>)}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '8px' }}>RELATION_TYPES</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {ontology.relation_types.map(t => <span key={t} className="pill success">{t}</span>)}
                      </div>
                    </div>
                  </div>

                  <button 
                    className="tactical-btn" 
                    style={{ width: '100%', padding: '14px', justifyContent: 'center', background: 'var(--accent-secondary)' }} 
                    onClick={async () => {
                      setIsProcessing(true)
                      try {
                        const res = await fetch(`${API}/api/projects/${project.project_id}/graph/extract`, { method: 'POST' })
                        if (res.ok) {
                          setActiveStage('world')
                        }
                      } catch(e) { console.error(e) }
                      finally { setIsProcessing(false) }
                    }}
                    disabled={isProcessing}
                  >
                    {isProcessing ? <Terminal className="animate-pulse" size={18} /> : 'BUILD_KNOWLEDGE_GRAPH'}
                  </button>
                </div>
              </motion.div>
            )}

            {activeStage === 'world' && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="tactical-overlay"
                style={{ top: '60px', width: '400px' }}
              >
                <div className="glass-panel" style={{ padding: '32px', borderLeft: '4px solid var(--success)' }}>
                  <h2 className="font-heading" style={{ fontSize: '20px', marginBottom: '8px' }}>WORLD_SYNTHESIS</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginBottom: '24px' }}>
                    Agent personas have been generated from knowledge graph nodes.
                  </p>
                  
                  <div className="scroll-thin" style={{ maxHeight: '200px', overflowY: 'auto', marginBottom: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {project?.personas?.map(p => (
                      <div key={p.persona_id} style={{ padding: '12px', background: '#f8fafc', border: '1px solid var(--border)', borderRadius: '4px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                          <div className="font-heading" style={{ fontSize: '13px' }}>{p.name}</div>
                          <div className="pill info" style={{ fontSize: '9px' }}>{p.role || 'AGENT'}</div>
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', lineClamp: 2 }}>{p.background}</div>
                      </div>
                    ))}
                    {!project?.personas && (
                       <div style={{ padding: '20px', textAlign: 'center', border: '1px dashed var(--border)', fontSize: '12px', color: 'var(--text-muted)' }}>
                          AWAITING_SYNTHESIS...
                       </div>
                    )}
                  </div>

                  {project?.personas && (
                    <div style={{ marginBottom: '24px' }}>
                       <div className="font-mono" style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '8px' }}>NARRATIVE_SPARK_INJECTION</div>
                       <textarea 
                         className="input scroll-thin"
                         placeholder="Describe a rumor, event, or trigger to simulate..."
                         style={{ width: '100%', minHeight: '80px', padding: '12px', fontSize: '12px', background: '#fafafa' }}
                         value={narrativeSpark}
                         onChange={e => setNarrativeSpark(e.target.value)}
                       />
                    </div>
                  )}

                  {!project?.personas ? (
                    <button 
                      className="tactical-btn" 
                      style={{ width: '100%', padding: '14px', justifyContent: 'center', background: 'var(--text-primary)' }} 
                      onClick={async () => {
                        setIsProcessing(true)
                        try {
                          const res = await fetch(`${API}/api/projects/${project.project_id}/personas/synthesize`, { method: 'POST' })
                          if (res.ok) {
                             const pRes = await fetch(`${API}/api/projects/${project.project_id}`)
                             if (pRes.ok) useStore.getState().setProject(await pRes.json())
                          }
                        } catch(e) { console.error(e) }
                        finally { setIsProcessing(false) }
                      }}
                      disabled={isProcessing}
                    >
                      {isProcessing ? <Terminal className="animate-pulse" size={18} /> : 'SYNTHESIZE_PERSONA_SWARM'}
                    </button>
                  ) : (
                    <button 
                      className="tactical-btn" 
                      style={{ width: '100%', padding: '14px', justifyContent: 'center', background: 'var(--success)' }} 
                      onClick={handleLaunchSwarm}
                      disabled={isProcessing}
                    >
                      {isProcessing ? <Terminal className="animate-pulse" size={18} /> : 'LAUNCH_LIVE_SWARM'}
                    </button>
                  )}
                </div>
              </motion.div>
            )}

            {activeStage === 'swarm' && (
               <motion.div 
                 initial={{ opacity: 0 }}
                 animate={{ opacity: 1 }}
                 className="tactical-overlay"
                 style={{ bottom: '24px', top: 'auto', width: 'calc(100% - 404px)', maxWidth: 'none', left: '24px' }}
               >
                 <div className="glass-panel" style={{ padding: '12px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '2px solid var(--success)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                       <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div className="animate-pulse" style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--success)' }} />
                          <div className="font-mono" style={{ fontSize: '11px' }}>SWARM_ACTIVE</div>
                       </div>
                       <div className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                          INJECTION: {latestRun?.objective || 'GENERAL_SCAN'}
                       </div>
                    </div>
                    <button 
                      className="tactical-btn secondary" 
                      style={{ border: 'none', background: 'none', color: 'var(--danger)' }}
                      onClick={() => setActiveStage('interaction')}
                    >
                       HALT_SIMULATION
                    </button>
                 </div>
               </motion.div>
            )}

            {activeStage === 'interaction' && (
               <motion.div 
                 initial={{ opacity: 0, scale: 0.98 }}
                 animate={{ opacity: 1, scale: 1 }}
                 className="tactical-overlay"
                 style={{ top: '60px', width: '900px', left: '50%', transform: 'translateX(-50%)' }}
               >
                 <div className="glass-panel" style={{ padding: '32px', borderTop: '4px solid var(--text-primary)' }}>
                   <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                      <div>
                        <h2 className="font-heading" style={{ fontSize: '24px', letterSpacing: '-0.02em' }}>MISSION_DEBRIEF</h2>
                        <div className="font-mono" style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>
                          ID: {latestRun?.run_id?.slice(0, 8)} // {new Date().toLocaleDateString()}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '12px' }}>
                        {!missionSummary && (
                          <button className="tactical-btn" onClick={handleSynthesize} disabled={isProcessing}>
                            {isProcessing ? <Terminal className="animate-pulse" size={16} /> : 'GENERATE_STRATEGIC_SUMMARY'}
                          </button>
                        )}
                        <button className="tactical-btn secondary" onClick={() => { setActiveStage('identity'); setOntology(null); setMissionSummary(null); }}>NEW_MISSION</button>
                      </div>
                   </div>

                    {missionSummary ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.5fr', gap: '40px' }}>
                           {/* 1. Intelligence Scorecard */}
                           <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                 <div 
                                   style={{ background: '#f8fafc', padding: '20px', borderRadius: '4px', border: '1px solid var(--border)', cursor: 'pointer' }}
                                   onClick={() => {
                                     const frictionNode = graphData.nodes.find(n => n.id === missionSummary.risk_scorecard.primary_friction)
                                     if (frictionNode) handleNodeClick(frictionNode)
                                   }}
                                 >
                                    <div className="font-mono" style={{ fontSize: '9px', color: 'var(--text-muted)', marginBottom: '8px' }}>PRIMARY_FRICTION</div>
                                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--danger)' }}>{missionSummary.risk_scorecard.primary_friction}</div>
                                    <div style={{ fontSize: '9px', color: 'var(--text-muted)', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                       <Zap size={10} /> CLICK_TO_FOCUS_NODE
                                    </div>
                                 </div>
                                 <div style={{ background: 'var(--text-primary)', color: 'white', padding: '20px', borderRadius: '4px' }}>
                                    <div className="font-mono" style={{ fontSize: '9px', color: 'var(--accent)', marginBottom: '8px' }}>AGGREGATED_RISK</div>
                                    <div style={{ fontSize: '28px', fontWeight: 800 }}>{missionSummary.risk_scorecard.total_risk.toFixed(1)}<span style={{ fontSize: '14px', opacity: 0.5 }}>/10</span></div>
                                    <div style={{ fontSize: '8px', marginTop: '4px', opacity: 0.7 }}>DEBATED_SWARM_CONSENSUS</div>
                                 </div>
                              </div>
  
                              <div style={{ padding: '24px', background: '#f8fafc', border: '1px solid var(--border)', borderRadius: '4px' }}>
                                 <h3 className="font-heading" style={{ fontSize: '14px', marginBottom: '12px' }}>EXECUTIVE_SUMMARY</h3>
                                 <p style={{ fontSize: '13px', lineHeight: 1.6 }}>{missionSummary.executive_summary}</p>
                              </div>
  
                              <PopulationChart data={missionSummary.risk_scorecard.population_cascade} />
                           </div>
  
                           {/* 2. Massive Projection & Playbook */}
                           <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                              <div style={{ padding: '24px', background: '#000', color: 'white', borderRadius: '4px', position: 'relative', overflow: 'hidden' }}>
                                 <div className="font-mono" style={{ fontSize: '9px', color: 'var(--success)', marginBottom: '12px' }}>PROJECTED_NARRATIVE_REACH</div>
                                 <div style={{ fontSize: '42px', fontWeight: 900, letterSpacing: '-0.03em' }} className="font-mono">
                                    {missionSummary.risk_scorecard.population_cascade?.projected_peak_impressions.toLocaleString()}
                                    <span style={{ fontSize: '16px', color: 'var(--success)', marginLeft: '8px' }}>NODES</span>
                                  </div>
                                  <div style={{ fontSize: '10px', marginTop: '12px', opacity: 0.6 }}>CRITICAL_MASS_HOURS: {missionSummary.risk_scorecard.population_cascade?.hours_to_peak}h</div>
                                  
                                  <div style={{ position: 'absolute', right: '-10px', top: '20px', opacity: 0.1, transform: 'rotate(10deg)' }}>
                                     <Activity size={120} />
                                  </div>
                              </div>
                              
                              <div>
                                 <div className="font-mono" style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '12px' }}>MITIGATION_PLAYBOOK</div>
                                 <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                    {missionSummary.mitigation_playbook.slice(0, 3).map((m, i) => (
                                       <div key={i} style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: '4px', background: '#fff' }}>
                                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                             <div className="font-heading" style={{ fontSize: '13px' }}>{m.step}</div>
                                             <div className={`pill ${m.urgency === 'CRITICAL' ? 'danger' : 'warning'}`} style={{ fontSize: '8px' }}>{m.urgency}</div>
                                        </div>
                                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{m.action}</div>
                                     </div>
                                  ))}
                               </div>
                            </div>
                         </div>
                        </div>

                        {/* Agent Deep Dive Section */}
                        <div style={{ borderTop: '1px solid var(--border)', paddingTop: '32px' }}>
                           <div className="font-mono" style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '16px' }}>AGENT_DEEP_DIVE</div>
                           <div style={{ display: 'flex', gap: '24px', height: '300px' }}>
                              <div className="scroll-thin" style={{ width: '200px', display: 'flex', flexDirection: 'column', gap: '4px', overflowY: 'auto' }}>
                                 {project?.personas?.map(p => (
                                    <div 
                                      key={p.persona_id} 
                                      onClick={() => setActiveNode(p)}
                                      className={`pill ${activeNode?.persona_id === p.persona_id ? 'info' : ''}`}
                                      style={{ cursor: 'pointer', whiteSpace: 'nowrap', border: '1px solid var(--border)', textAlign: 'center' }}
                                    >
                                      {p.name}
                                    </div>
                                 ))}
                              </div>
                              <div style={{ flex: 1, border: '1px solid var(--border)', borderRadius: '4px', background: '#fafafa', display: 'flex', flexDirection: 'column' }}>
                                 {activeNode?.persona_id ? (
                                    <>
                                       <div className="scroll-thin" style={{ flex: 1, padding: '20px', fontSize: '12px' }}>
                                          <div className="font-mono" style={{ color: 'var(--text-muted)', marginBottom: '12px', fontSize: '10px' }}>
                                             CONNECTED_TO_{activeNode.name.toUpperCase()}
                                          </div>
                                          <div style={{ lineHeight: 1.6 }}>{activeNode.response || "Agent linked. Awaiting tactical query."}</div>
                                       </div>
                                       <div style={{ padding: '16px', borderTop: '1px solid var(--border)' }}>
                                          <input 
                                            className="input" 
                                            placeholder="Ask agent for specific logic..." 
                                            style={{ width: '100%', padding: '10px', fontSize: '12px' }}
                                            onKeyDown={async (e) => {
                                              if (e.key === 'Enter') {
                                                const msg = e.target.value
                                                e.target.value = ''
                                                setIsProcessing(true)
                                                try {
                                                  const res = await fetch(`${API}/api/projects/${project.project_id}/personas/${activeNode.persona_id}/chat`, {
                                                    method: 'POST',
                                                    headers: { 'Content-Type': 'application/json' },
                                                    body: JSON.stringify({ question: msg })
                                                  })
                                                  if (res.ok) {
                                                    const data = await res.json()
                                                    setActiveNode({ ...activeNode, response: data.response })
                                                  }
                                                } catch(err) {} finally { setIsProcessing(false) }
                                              }
                                            }}
                                          />
                                       </div>
                                    </>
                                 ) : (
                                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', color: 'var(--text-muted)' }}>
                                       SELECT AGENT FOR GRANULAR BRIEFING
                                    </div>
                                 )}
                              </div>
                           </div>
                        </div>
                      </div>
                    ) : (
                      <div style={{ height: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px', border: '1px dashed var(--border)', borderRadius: '8px' }}>
                         <Terminal size={48} className={isProcessing ? "animate-pulse" : ""} style={{ color: 'var(--text-muted)', opacity: 0.3 }} />
                         <div style={{ textAlign: 'center' }}>
                            <h3 className="font-heading" style={{ fontSize: '18px' }}>{isProcessing ? 'CALCULATING_STRATEGIC_TRAJECTORY...' : 'AWAITING_SYNTHESIS'}</h3>
                            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
                               {isProcessing ? 'Neural swarms are being aggregated into tactical reports.' : 'Mission run complete. Click above to generate strategic intelligence.'}
                            </p>
                         </div>
                      </div>
                    )}
                 </div>
               </motion.div>
            )}
            
            {/* Original Active Node briefing (moved down to avoid overlap if needed, though AnimatePresence handles overlays) */}
            {activeNode && activeStage !== 'interaction' && (
               <motion.div 
                 initial={{ opacity: 0, x: -20 }}
                 animate={{ opacity: 1, x: 0 }}
                 className="tactical-overlay"
                 style={{ top: '80px' }}
               >
                 <div className="glass-panel node-briefing" style={{ borderLeft: '4px solid var(--accent)' }}>
                   <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                     <div className="pill amber">ENTITY_SUMMARY</div>
                     <button style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '18px' }} onClick={() => setActiveNode(null)}>×</button>
                   </div>
                   <h3 className="font-heading" style={{ fontSize: '18px' }}>{activeNode.id}</h3>
                   <div className="pill info" style={{ marginTop: '8px', display: 'inline-block' }}>{activeNode.type || 'TERM'}</div>
                   <div style={{ marginTop: '16px', fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                     {activeNode.description || 'Behavioral node detected in neural swarm. Awaiting interactive simulation results.'}
                   </div>
                 </div>
               </motion.div>
             )}
          </AnimatePresence>
        </div>

        {/* 3. Operational Workbench (Stage Dependent) */}
        {activeStage === 'swarm' && (
          <aside className="side-workbench">
            <div className="workbench-header">
              <Terminal size={14} /> LIVE TACTICAL LOGS
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
              <PersonaFeed runId={latestRun?.run_id} />
            </div>
          </aside>
        )}
      </div>
    </div>
  )
}
