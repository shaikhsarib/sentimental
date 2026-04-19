import { useState, useEffect } from 'react'
import { 
  Zap, 
  Terminal, 
  Activity, 
  ZapOff, 
  Info,
  Shield,
  FileText
} from 'lucide-react'
import useStore from '../store/useStore'
import PersonaFeed from './PersonaFeed'
import PopulationChart from './PopulationChart'

const API = import.meta.env.VITE_API_URL || ''

export default function WorkbenchPanel() {
  const { 
    project, 
    activeStage, 
    setActiveStage, 
    activeNode, 
    setActiveNode,
    latestRun,
    workbenchMode,
    setWorkbenchMode,
    selectedRunId
  } = useStore()

  const [localRun, setLocalRun] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    if (selectedRunId) {
      fetch(`${API}/api/projects/${project.project_id}/runs/${selectedRunId}`)
         .then(res => res.json())
         .then(setLocalRun)
         .catch(console.error)
    } else {
        setLocalRun(null)
    }
  }, [selectedRunId, project?.project_id])

  // --- Actions --- (Harvested from OperationRoom)
  const handleSynthesizeSummary = async () => {
    if (!localRun) return
    setIsProcessing(true)
    try {
      const res = await fetch(`${API}/api/projects/${project.project_id}/runs/${localRun.run_id}/summarize`, { method: 'POST' })
      if (res.ok) {
        const data = await res.json()
        setLocalRun({ ...localRun, summary: data })
      }
    } catch (e) { console.error(e) }
    finally { setIsProcessing(false) }
  }

  const renderContent = () => {
    if (workbenchMode === 'inspector' && activeNode) {
      return (
        <div className="workbench-view inspector">
           <div className="view-header">
              <Info size={16} /> NODE_INSPECTOR
           </div>
           <div className="view-body scroll-thin">
              <h3 className="font-heading">{activeNode.id}</h3>
              <div className="pill info" style={{ marginTop: '8px', display: 'inline-block' }}>{activeNode.type || 'TERM'}</div>
              <div className="node-stats">
                 <div className="stat"><span>Weight</span> <span>{activeNode.weight || 0}</span></div>
                 {activeNode.risk && <div className="stat"><span>Risk</span> <span className="text-danger">{activeNode.risk}</span></div>}
              </div>
              <p className="description">
                 {activeNode.description || 'Behavioral node detected in neural swarm. Awaiting interactive simulation results.'}
              </p>
              
              {activeNode.response && (
                 <div className="agent-response">
                    <div className="font-mono text-[9px] text-muted mb-2 uppercase">Grounded Response</div>
                    <p>{activeNode.response}</p>
                 </div>
              )}
           </div>
        </div>
      )
    }

    if (workbenchMode === 'report' && localRun) {
      const result = localRun.result || {}
      const summary = localRun.summary || null

      return (
        <div className="workbench-view report">
           <div className="view-header">
              <Activity size={16} /> MISSION_DEBRIEF
           </div>
           <div className="view-body scroll-thin">
              {summary ? (
                 <div className="summary-data">
                    <div className="risk-banner">
                       <span className="label">CONSOLIDATED_RISK</span>
                       <span className="value">{summary.risk_scorecard.total_risk.toFixed(1)}</span>
                    </div>
                    
                    <div className="field">
                       <div className="field-label">EXECUTIVE_SUMMARY</div>
                       <p className="field-text">{summary.executive_summary}</p>
                    </div>

                    <PopulationChart data={summary.risk_scorecard.population_cascade} />

                    <div className="field">
                       <div className="field-label">MITIGATION_PLAYBOOK</div>
                       <div className="playbook-list">
                          {summary.mitigation_playbook.map((m, i) => (
                             <div key={i} className="playbook-item">
                                <div className="item-title">
                                   <span>{m.step}</span>
                                   <span className={`pill ${m.urgency === 'CRITICAL' ? 'danger' : 'warning'}`}>{m.urgency}</span>
                                </div>
                                <div className="item-desc">{m.action}</div>
                             </div>
                          ))}
                       </div>
                    </div>
                 </div>
              ) : (
                 <div className="empty-report">
                    <Terminal size={32} className={isProcessing ? "animate-pulse" : "opacity-20"} />
                    <p>{isProcessing ? 'CALCULATING_STRATEGIC_TRAJECTORY...' : 'AWAITING_SYNTHESIS'}</p>
                    <button className="tactical-btn mt-4" onClick={handleSynthesizeSummary} disabled={isProcessing}>
                       GENERATE_STRATEGIC_INTELLIGENCE
                    </button>
                 </div>
              )}
           </div>
        </div>
      )
    }

    // Default: Actions / Control Center
    return (
      <div className="workbench-view actions">
         <div className="view-header">
            <Shield size={16} /> {activeStage.toUpperCase()}_CONTROLS
         </div>
         <div className="view-body scroll-thin">
            {activeStage === 'identity' && (
               <div className="stage-controls">
                  <p className="text-muted text-xs mb-4">Upload intelligence to bootstrap the mission.</p>
                  <button className="tactical-btn w-full" onClick={() => setWorkbenchMode('identity_form')}>
                     ADD_DOCUMENTS
                  </button>
               </div>
            )}
            
            {(activeStage === 'intelligence' || activeStage === 'world') && (
               <div className="stage-controls">
                  <p className="text-muted text-xs mb-4">Construct the world model via graph extraction.</p>
                  <button className="tactical-btn w-full" onClick={() => setActiveStage('world')}>
                     REFRESH_KNOWLEDGE_GRAPH
                  </button>
               </div>
            )}

            {activeStage === 'swarm' && (
               <div className="stage-controls">
                  <div className="live-status">
                     <span className="pulse-success" /> 
                     <span>SIMULATION_ACTIVE</span>
                  </div>
                  <PersonaFeed runId={latestRun?.run_id} />
               </div>
            )}
         </div>
      </div>
    )
  }

  return (
    <aside className="workspace-workbench">
      <div className="workbench-tabs">
         <button 
           className={`tab ${workbenchMode === 'actions' ? 'active' : ''}`}
           onClick={() => setWorkbenchMode('actions')}
         >
            <Shield size={14} />
         </button>
         <button 
           className={`tab ${workbenchMode === 'inspector' ? 'active' : ''}`}
           onClick={() => setWorkbenchMode('inspector')}
           disabled={!activeNode}
         >
            <Info size={14} />
         </button>
         <button 
           className={`tab ${workbenchMode === 'report' ? 'active' : ''}`}
           onClick={() => setWorkbenchMode('report')}
           disabled={!selectedRunId}
         >
            <Activity size={14} />
         </button>
      </div>
      <div className="workbench-container">
         {renderContent()}
      </div>
    </aside>
  )
}
