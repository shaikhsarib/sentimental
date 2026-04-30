import React from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, Fingerprint, Search, Database, MessageSquare, ArrowRight } from 'lucide-react'

export default function ConsensusRefused({ consensus }) {
  if (!consensus) return null

  const { status, agreement_score, intelligence_gaps, metrics, polarization_clusters, is_polarized } = consensus

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* 1. Status Banner */}
      <div className="glass-panel" style={{ 
        background: 'rgba(239, 68, 68, 0.1)', 
        borderColor: 'var(--danger)', 
        padding: '32px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <AlertTriangle size={48} color="var(--danger)" style={{ margin: '0 auto 16px' }} />
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--danger)', marginBottom: '8px' }}>
            {status.replace('_', ' ')}
          </h2>
          <p style={{ fontSize: '14px', color: 'var(--muted)', maxWidth: '500px', margin: '0 auto' }}>
            SentiFlow has detected insufficient swarm agreement to generate a reliable prediction. 
            Outputting a verdict now would risk hallucination.
          </p>
          <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'center', gap: '16px' }}>
            <div className="pill" style={{ background: 'rgba(255,255,255,0.05)', padding: '8px 16px' }}>
              Swarm Agreement: <span style={{ color: 'var(--danger)', fontWeight: 800 }}>{(agreement_score * 100).toFixed(1)}%</span>
            </div>
            <div className="pill" style={{ background: 'rgba(255,255,255,0.05)', padding: '8px 16px' }}>
              Minimum Required: <span style={{ fontWeight: 800 }}>78.0%</span>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '24px' }}>
        
        {/* 2. Intelligence Gaps (The 'Why') */}
        <div className="glass-panel">
          <div className="workbench-header">
            <Search size={14} /> Identified Intelligence Gaps
          </div>
          <div style={{ padding: '20px' }}>
            {intelligence_gaps.map((gap, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                style={{ 
                  padding: '16px', 
                  borderLeft: `4px solid ${gap.severity === 'CRITICAL' ? 'var(--danger)' : 'var(--accent-amber)'}`,
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: '0 8px 8px 0',
                  marginBottom: '16px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '11px', fontWeight: 800, color: gap.severity === 'CRITICAL' ? 'var(--danger)' : 'var(--accent-amber)', textTransform: 'uppercase' }}>
                    {gap.gap_type.replace('_', ' ')}
                  </span>
                  <div className="pill" style={{ fontSize: '10px' }}>{gap.severity}</div>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px' }}>{gap.description}</div>
                <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '12px' }}>{gap.action}</div>
                <button className="btn-secondary" style={{ fontSize: '11px', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Database size={12} /> Fill Gap Now <ArrowRight size={12} />
                </button>
              </motion.div>
            ))}
          </div>
        </div>

        {/* 3. Polarization Analysis */}
        <div className="glass-panel">
          <div className="workbench-header">
             <Fingerprint size={14} /> Swarm Polarization Analysis
          </div>
          <div style={{ padding: '20px' }}>
            {is_polarized ? (
              <div>
                <p style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '20px' }}>
                  The swarm has split into two irreconcilable camps. This indicates fundamental ambiguity in the narrative context.
                </p>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ padding: '12px', border: '1px solid var(--danger)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--danger)', fontWeight: 800, marginBottom: '4px' }}>CAMP A: HIGH RISK</div>
                    <div style={{ fontSize: '12px' }}>{polarization_clusters.high_risk_cluster.agents.join(', ')}</div>
                    <div style={{ fontSize: '10px', color: 'var(--muted)', marginTop: '4px' }}>Mean Risk: {polarization_clusters.high_risk_cluster.mean_risk}</div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'center' }}>
                    <div className="mono-text" style={{ fontSize: '10px', color: 'var(--muted)' }}>VS ({polarization_clusters.cluster_gap} POINT GAP)</div>
                  </div>

                  <div style={{ padding: '12px', border: '1px solid var(--accent)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--accent)', fontWeight: 800, marginBottom: '4px' }}>CAMP B: LOW RISK</div>
                    <div style={{ fontSize: '12px' }}>{polarization_clusters.low_risk_cluster.agents.join(', ')}</div>
                    <div style={{ fontSize: '10px', color: 'var(--muted)', marginTop: '4px' }}>Mean Risk: {polarization_clusters.low_risk_cluster.mean_risk}</div>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <MessageSquare size={32} color="var(--muted)" style={{ margin: '0 auto 16px', opacity: 0.3 }} />
                <div style={{ fontSize: '13px', color: 'var(--muted)' }}>No clear polarization clusters detected. Dissonance is uniform across the swarm.</div>
              </div>
            )}

            <div style={{ marginTop: '32px', borderTop: '1px solid var(--border)', paddingTop: '20px' }}>
              <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '12px' }}>Distribution Spread</div>
              <div style={{ height: '40px', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', position: 'relative', overflow: 'hidden' }}>
                <div style={{ 
                  position: 'absolute', 
                  left: `${(metrics.mean_risk / 10) * 100}%`, 
                  top: 0, bottom: 0, width: '2px', background: 'var(--danger)', zIndex: 2 
                }}></div>
                <div style={{ 
                  position: 'absolute', 
                  left: `${(metrics.min_risk / 10) * 100}%`, 
                  width: `${((metrics.max_risk - metrics.min_risk) / 10) * 100}%`, 
                  top: '10px', bottom: '10px', background: 'var(--danger)', opacity: 0.1 
                }}></div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '10px', color: 'var(--muted)' }}>
                <span>MIN: {metrics.min_risk}</span>
                <span style={{ color: 'var(--danger)' }}>MEAN: {metrics.mean_risk}</span>
                <span>MAX: {metrics.max_risk}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}
