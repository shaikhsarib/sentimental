import React from 'react'

export default function PopulationChart({ data }) {
  if (!data) return null

  const { hours_to_peak, projected_peak_impressions, r0_score } = data
  const width = 400
  const height = 150
  const padding = 20

  // Generate points for a logistic-style Sigmoid curve
  const points = []
  const steps = 50
  for (let i = 0; i <= steps; i++) {
    const xFraction = i / steps
    const x = padding + xFraction * (width - 2 * padding)
    
    // Logistic growth formula: L / (1 + e^-k(x-x0))
    const L = height - 2 * padding
    const k = r0_score * 0.5
    const x0 = hours_to_peak / 168
    const yValue = L / (1 + Math.exp(-k * (xFraction - x0) * 10))
    
    const y = height - padding - yValue
    points.push(`${x},${y}`)
  }

  return (
    <div style={{ background: '#fff', padding: '20px', border: '1px solid var(--border)', borderRadius: '4px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
         <div className="font-mono" style={{ fontSize: '9px', color: 'var(--text-muted)' }}>PROJECTION_MODEL: SEIR_CASCADE</div>
         <div className="font-mono" style={{ fontSize: '9px', color: 'var(--success)' }}>R0: {r0_score}</div>
      </div>
      
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
        {/* Grid lines */}
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="var(--border)" strokeWidth="1" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="var(--border)" strokeWidth="1" />
        
        {/* The Curve */}
        <polyline
          fill="none"
          stroke="var(--text-primary)"
          strokeWidth="2"
          points={points.join(' ')}
          style={{ transition: 'all 1s ease-in-out' }}
        />
        
        {/* Peak Marker */}
        <circle 
          cx={padding + (hours_to_peak / 168) * (width - 2 * padding)} 
          cy={padding} 
          r="3" 
          fill="var(--danger)" 
          className="animate-pulse"
        />
      </svg>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
         <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>0h</div>
         <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>TE_PEAK: {hours_to_peak}h</div>
         <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>168h</div>
      </div>
    </div>
  )
}
