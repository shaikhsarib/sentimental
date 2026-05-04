import React from 'react'
import { motion } from 'framer-motion'
import { Activity, ShieldAlert, CheckCircle2, AlertCircle, BarChart3, Users, Zap } from 'lucide-react'
import PopulationChart from './PopulationChart'
import ConsensusRefused from './ConsensusRefused'

export default function DebriefReport({ runResult }) {
  if (!runResult) return null

  const shield = runResult.mode === 'shield' ? runResult : runResult.shield
  
  // ─── SILENT CONSENSUS PROTOCOL CHECK ───
  if (shield?.consensus?.should_refuse) {
    return <ConsensusRefused consensus={shield.consensus} />
  }

  const evaluation = shield?.evaluation || {}
  const cascade = shield?.graph_cascade || {}
  
  const riskColor = shield?.risk_level === 'CRITICAL' ? 'var(--danger-glow)' : 
                   shield?.risk_level === 'HIGH' ? 'var(--accent-amber-glow)' : 
                   'var(--accent-glow)'
                   
  const riskBorder = shield?.risk_level === 'CRITICAL' ? 'var(--danger)' : 
                    shield?.risk_level === 'HIGH' ? 'var(--accent-amber)' : 
                    'var(--accent)'

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="debrief-report-v6" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* ─── V6 EXPORT BAR ─── */}
      <div className="print-hide" style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '-12px' }}>
         <button className="tactical-btn secondary" onClick={handlePrint} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '10px' }}>
            <Activity size={12} /> EXPORT_STRATEGIC_BRIEF (PDF)
         </button>
      </div>
      
      {/* ─── V6 INSTITUTIONAL ARBITER VERDICT ─── */}
      <div className="glass-panel" style={{ padding: '24px', borderLeft: `4px solid ${riskBorder}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                    <div style={{ background: 'var(--accent)', color: 'white', padding: '4px 10px', borderRadius: '4px', fontSize: '10px', fontWeight: 800 }}>V6 ARBITER</div>
                    <h3 style={{ fontSize: '12px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>Institutional Synthesis</h3>
                </div>
                <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '16px', lineHeight: 1.4 }}>
                  "{shield?.judge_verdict?.consolidated_verdict || 'Awaiting institutional synthesis...'}"
                </h2>
                
                {shield?.judge_verdict?.dissonance_points && (
                  <div style={{ background: 'rgba(0,0,0,0.03)', padding: '16px', borderRadius: '8px', border: '1px dashed var(--border)' }}>
                     <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '8px', fontWeight: 700 }}>DISSONANCE_POINTS // WHERE AGENTS DISAGREED</div>
                     <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {shield.judge_verdict.dissonance_points.map((p, i) => (
                          <li key={i} style={{ color: 'var(--muted)' }}>{p}</li>
                        ))}
                     </ul>
                  </div>
                )}
            </div>
            
            <div style={{ marginLeft: '24px', textAlign: 'center', minWidth: '120px' }}>
                <div style={{ fontSize: '10px', color: 'var(--muted)', marginBottom: '4px' }}>NARRATIVE_R0</div>
                <div style={{ fontSize: '48px', fontWeight: 900, color: 'var(--accent)', lineHeight: 1 }}>
                  {shield?.judge_verdict?.narrative_r0?.toFixed(1) || '0.0'}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--muted)', marginTop: '4px' }}>CONTAGION_INDEX</div>
                <div style={{ marginTop: '12px', fontSize: '10px', padding: '4px', background: riskColor, borderRadius: '4px', border: `1px solid ${riskBorder}` }}>
                   {shield?.risk_level} IMPACT
                </div>
            </div>
        </div>
      </div>

      {/* 1. Swarm Agreement Summary */}
      <div className="glass-panel" style={{ padding: '20px', background: 'rgba(0,0,0,0.02)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ fontSize: '12px' }}>
                    <span style={{ color: 'var(--muted)' }}>Swarm Agreement:</span> 
                    <span style={{ marginLeft: '8px', fontWeight: 700 }}>{shield?.verification?.agreement_score}%</span>
                </div>
                <div style={{ height: '12px', width: '1px', background: 'var(--border)' }}></div>
                <div style={{ fontSize: '12px' }}>
                    <span style={{ color: 'var(--muted)' }}>Confidence:</span> 
                    <span style={{ marginLeft: '8px', fontWeight: 700 }}>{shield?.confidence >= 0.7 ? 'HIGH' : 'MODERATE'}</span>
                </div>
            </div>
            <div className="mono-text" style={{ fontSize: '10px', color: 'var(--muted)' }}>
                SESSION_HASH: {shield?.analysis_id?.slice(0,12)}
            </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        
        {/* 2. Population Cascade Projection */}
        <div className="glass-panel">
            <div className="workbench-header">
                <Users size={14} /> 10M Population Projection
            </div>
            <div style={{ padding: '20px' }}>
                <div style={{ marginBottom: '16px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 700 }}>{cascade.projected_peak_impressions?.toLocaleString()}</div>
                    <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Estimated Peak Exposure</div>
                </div>
                <PopulationChart data={cascade} />
                <p style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '16px', lineHeight: 1.5 }}>
                   {cascade.summary}
                </p>
            </div>
        </div>

        {/* ─── V6 TECHNICAL AUDIT TRAIL ─── */}
        <div className="glass-panel" style={{ gridColumn: 'span 2' }}>
            <div className="workbench-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Activity size={14} /> INSTITUTIONAL_AUDIT_TRAIL
                </div>
                {shield?.judge_verdict?.evidence_winner && (
                   <div style={{ fontSize: '10px', color: 'var(--accent)', fontWeight: 800 }}>
                      EVIDENCE_WINNER: {shield.judge_verdict.evidence_winner.toUpperCase()}
                   </div>
                )}
            </div>
            <div style={{ padding: '20px' }}>
                <div style={{ background: '#0f172a', color: '#94a3b8', padding: '16px', borderRadius: '4px', fontFamily: 'var(--font-mono)', fontSize: '12px', lineHeight: 1.6 }}>
                    <div style={{ color: 'var(--accent)', marginBottom: '8px' }}>// ARBITER_CHAIN_OF_THOUGHT</div>
                    <p style={{ margin: 0 }}>{shield?.judge_verdict?.chain_of_thought || 'No audit data available for this session.'}</p>
                </div>
                
                {shield?.judge_verdict?.intelligence_gaps?.length > 0 && (
                   <div style={{ marginTop: '16px' }}>
                      <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '8px', fontWeight: 700 }}>REMAINING_INTELLIGENCE_GAPS</div>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                         {shield.judge_verdict.intelligence_gaps.map((gap, i) => (
                           <div key={i} className="pill danger" style={{ fontSize: '10px' }}>{gap}</div>
                         ))}
                      </div>
                   </div>
                )}
            </div>
        </div>

        {/* 3. Agentic Accuracy Scorecard (Self-Correction Loop) */}
        <div className="glass-panel">
            <div className="workbench-header">
                <Zap size={14} /> Agentic Metacognition
            </div>
            <div style={{ padding: '20px' }}>
               <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                  <div>
                    <div style={{ fontSize: '24px', fontWeight: 700 }}>{evaluation.swarm_accuracy}%</div>
                    <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Swarm Cohesion</div>
                  </div>
                  <div style={{ width: '60px', height: '60px', borderRadius: '50%', border: '4px solid var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: 800 }}>
                    V5
                  </div>
               </div>
               
               <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '200px', overflowY: 'auto' }}>
                  {evaluation.agent_grades?.map((grade, i) => (
                    <div key={i} style={{ padding: '8px', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '11px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                       <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: grade.status === 'ACCURATE' ? 'var(--accent)' : (grade.status === 'MISTAKE' ? 'var(--danger)' : 'var(--accent-amber)') }}></span>
                          <span>{grade.persona_id?.capitalize()}</span>
                       </div>
                       <span style={{ color: grade.status === 'ACCURATE' ? 'var(--accent)' : 'var(--danger)', fontWeight: 600 }}>{grade.status.replace('_', ' ')}</span>
                    </div>
                  ))}
               </div>
               
               {/* New Heatmap Indicator */}
               <div style={{ marginTop: '20px', borderTop: '1px solid var(--border)', paddingTop: '16px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '8px' }}>Swarm Consensus Heatmap</div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(10, 1fr)', gap: '4px', height: '12px' }}>
                     {Array.from({length: 10}).map((_, i) => {
                        const scoreThreshold = (i + 1) * 10;
                        const isActive = evaluation.swarm_accuracy >= scoreThreshold;
                        return (
                           <div key={i} style={{ 
                              background: isActive ? 'var(--accent)' : 'rgba(255,255,255,0.05)', 
                              opacity: isActive ? (i + 1) / 10 : 0.2,
                              borderRadius: '2px' 
                           }}></div>
                        )
                     })}
                  </div>
               </div>
            </div>
        </div>
      </div>

      {/* 4. Strategic Mitigation Playbook */}
      <div className="glass-panel">
        <div className="workbench-header">
            <CheckCircle2 size={14} /> Mission Playbook
        </div>
        <div style={{ padding: '20px' }}>
            {runResult.macro?.macro_outcomes?.mitigation_playbook?.map((task, i) => (
                <div key={i} style={{ display: 'flex', gap: '16px', marginBottom: '16px', paddingBottom: '16px', borderBottom: i < 2 ? '1px solid var(--border)' : 'none' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        {i + 1}
                    </div>
                    <div>
                        <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px' }}>{task.step}</div>
                        <div style={{ fontSize: '12px', color: 'var(--muted)', lineHeight: 1.4 }}>{task.action}</div>
                        <div className="pill" style={{ display: 'inline-block', marginTop: '8px', fontSize: '10px', background: task.urgency === 'CRITICAL' ? 'var(--danger-glow)' : 'rgba(255,255,255,0.05)', color: task.urgency === 'CRITICAL' ? 'var(--danger)' : 'var(--muted)' }}>
                            {task.urgency}
                        </div>
                    </div>
                </div>
            )) || <div className="empty-state">No strategic briefing available</div>}
        </div>
      </div>

    </div>
  )
}

// Helper
String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}
