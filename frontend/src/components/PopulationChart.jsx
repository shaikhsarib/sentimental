import React from 'react'

export default function PopulationChart({ data }) {
  if (!data) return null

  const { hours_to_peak, projected_peak_impressions, r0_score } = data
  const width = 400
  const height = 150
  const padding = 20

  // Generate points for a logistic-style Sigmoid curve
  const points = []
  const steps = 60
  for (let i = 0; i <= steps; i++) {
    const xFraction = i / steps
    const x = padding + xFraction * (width - 2 * padding)
    
    // Logistic growth formula: L / (1 + e^-k(x-x0))
    const L = height - 2 * padding
    const k = Math.max(0.2, r0_score * 0.4)
    const x0 = (hours_to_peak || 72) / 168
    const yValue = L / (1 + Math.exp(-k * (xFraction - x0) * 12))
    
    const y = height - padding - yValue
    points.push(`${x},${y}`)
  }

  return (
    <div style={{ 
      background: 'rgba(2, 6, 23, 0.4)', 
      backdropFilter: 'blur(8px)',
      padding: '24px', 
      border: '1px solid rgba(255,255,255,0.05)', 
      borderRadius: '12px',
      boxShadow: 'inset 0 1px 1px rgba(255,255,255,0.05)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', alignItems: 'center' }}>
         <div style={{ fontSize: '10px', color: 'var(--muted)', letterSpacing: '0.05em', fontWeight: 600 }}>
            MODEL: <span style={{ color: 'var(--accent)' }}>SEIR_CASCADE_V5</span>
         </div>
         <div className="pill" style={{ fontSize: '10px', background: 'var(--accent-glow)', color: 'var(--accent)', border: 'none' }}>
            R&#8320; INDEX: {r0_score}
         </div>
      </div>
      
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.2" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="1" />
          </linearGradient>
          <filter id="glow">
             <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
             <feMerge>
                <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
             </feMerge>
          </filter>
        </defs>

        {/* Grid lines */}
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
        
        {/* The Curve */}
        <polyline
          fill="none"
          stroke="url(#lineGradient)"
          strokeWidth="2.5"
          points={points.join(' ')}
          filter="url(#glow)"
          strokeLinecap="round"
          style={{ transition: 'all 1.5s cubic-bezier(0.4, 0, 0.2, 1)' }}
        />
        
        {/* Peak Intensity Area */}
        <circle 
          cx={padding + ((hours_to_peak || 72) / 168) * (width - 2 * padding)} 
          cy={points[Math.floor(((hours_to_peak || 72) / 168) * steps)]?.split(',')[1] || padding} 
          r="4" 
          fill="var(--accent)"
          filter="url(#glow)"
        />
      </svg>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px' }}>
         <div style={{ fontSize: '10px', color: 'var(--muted)', fontWeight: 500 }}>0h</div>
         <div style={{ fontSize: '10px', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.02em' }}>
            PROJECTED_PEAK: {hours_to_peak}h
         </div>
         <div style={{ fontSize: '10px', color: 'var(--muted)', fontWeight: 500 }}>168h</div>
      </div>
    </div>
  )
}
