import React from 'react'

export default function PopulationChart({ data }) {
  if (!data) return null

  const { time_series, narrative_r0, peak_hour } = data
  if (!time_series) return <div className="empty-state">No simulation trajectory available</div>

  const { hours, susceptible, exposed, infected, recovered } = time_series
  const width = 400
  const height = 150
  const padding = 20

  const maxVal = Math.max(...susceptible, ...exposed, ...infected, ...recovered, 1)
  const maxHours = Math.max(...hours, 1)

  const getPoints = (series) => {
    return series.map((val, i) => {
      const x = padding + (hours[i] / maxHours) * (width - 2 * padding)
      const y = height - padding - (val / maxVal) * (height - 2 * padding)
      return `${x},${y}`
    }).join(' ')
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
            MODEL: <span style={{ color: 'var(--accent)' }}>SEIR_KINETICS_V5</span>
         </div>
         <div className="pill" style={{ fontSize: '10px', background: 'var(--accent-glow)', color: 'var(--accent)', border: 'none' }}>
            NARRATIVE R&#8320;: {narrative_r0?.toFixed(2)}
         </div>
      </div>
      
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
        <defs>
          <filter id="glow">
             <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
             <feMerge>
                <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
             </feMerge>
          </filter>
        </defs>

        {/* Grid lines */}
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
        
        {/* Susceptible (Background) */}
        <polyline
          fill="none"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth="1"
          points={getPoints(susceptible)}
        />

        {/* Exposed (Yellow) */}
        <polyline
          fill="none"
          stroke="var(--accent-amber)"
          strokeWidth="1.5"
          strokeDasharray="4 2"
          opacity="0.5"
          points={getPoints(exposed)}
        />
        
        {/* Recovered (Dimmed) */}
        <polyline
          fill="none"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth="1.5"
          points={getPoints(recovered)}
        />

        {/* Infected (The Crisis Spike - Glow) */}
        <polyline
          fill="none"
          stroke="var(--accent)"
          strokeWidth="3"
          points={getPoints(infected)}
          filter="url(#glow)"
          strokeLinecap="round"
        />
        
        {/* Peak Indicator */}
        <line 
          x1={padding + (peak_hour / maxHours) * (width - 2 * padding)}
          y1={padding}
          x2={padding + (peak_hour / maxHours) * (width - 2 * padding)}
          y2={height - padding}
          stroke="var(--accent)"
          strokeWidth="1"
          strokeDasharray="4 4"
          opacity="0.3"
        />
      </svg>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px' }}>
         <div style={{ fontSize: '10px', color: 'var(--muted)', fontWeight: 500 }}>0h</div>
         <div style={{ fontSize: '10px', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.02em' }}>
            PROJECTED_PEAK: {peak_hour}h
         </div>
         <div style={{ fontSize: '10px', color: 'var(--muted)', fontWeight: 500 }}>{maxHours}h</div>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginTop: '16px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '12px' }}>
        <LegendItem color="var(--accent)" label="Active Spread" />
        <LegendItem color="var(--accent-amber)" label="Exposed" dotted />
        <LegendItem color="rgba(255,255,255,0.2)" label="Desensitized" />
      </div>
    </div>
  )
}

function LegendItem({ color, label, dotted }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
      <div style={{ 
        width: '12px', 
        height: '2px', 
        background: color, 
        borderStyle: dotted ? 'dashed' : 'solid',
        opacity: 0.8
      }}></div>
      <span style={{ fontSize: '9px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</span>
    </div>
  )
}
