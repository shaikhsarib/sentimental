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

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* 1. Executive Risk Summary */}
      <div className="glass-panel" style={{ background: riskColor, borderColor: riskBorder, padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
                <h3 style={{ fontSize: '13px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>Consensus Verdict</h3>
                <h2 style={{ fontSize: '32px', fontWeight: 800, margin: '8px 0' }}>{shield?.risk_level} RISK</h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
                    <ShieldAlert size={16} color={riskBorder} />
                    <span>Agreement Score: {shield?.verification?.agreement_score}%</span>
                </div>
            </div>
            <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '11px', color: 'var(--muted)' }}>MISSION_ID</div>
                <div className="mono-text" style={{ fontSize: '12px' }}>{shield?.analysis_id?.slice(0,8)}</div>
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
