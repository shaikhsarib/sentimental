import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { User, Zap, AlertTriangle } from 'lucide-react'
import useStore from '../store/useStore'

const API = import.meta.env.VITE_API_URL || ''

export default function PersonaFeed({ runId }) {
  const { project } = useStore()
  const [events, setEvents] = useState([])
  const scrollRef = useRef(null)

  useEffect(() => {
    if (!project || !runId) return

    const eventSource = new EventSource(`${API}/api/projects/${project.project_id}/runs/${runId}/stream`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setEvents((prev) => [...prev, { id: Date.now(), ...data }])
      } catch (e) {
        console.error("SSE parse error", e)
      }
    }

    eventSource.addEventListener('persona_reaction', (event) => {
      try {
        const data = JSON.parse(event.data)
        setEvents((prev) => [...prev, { id: Date.now(), type: 'reaction', ...data }])
      } catch (e) {}
    })

    eventSource.addEventListener('status', (event) => {
       const status = JSON.parse(event.data)
       if (status === 'completed') {
         eventSource.close()
       }
    })

    return () => eventSource.close()
  }, [project, runId])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [events])

  return (
    <div className="persona-feed" style={{ display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto', maxHeight: '100%' }} ref={scrollRef}>
      <AnimatePresence initial={false}>
        {events.map((ev) => (
          <motion.div
            key={ev.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-panel"
            style={{ padding: '12px', fontSize: '13px', borderLeft: ev.virality_risk > 7 ? '3px solid #ef4444' : '3px solid var(--accent)' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                <User size={14} /> {ev.persona_name || 'Agent'}
              </div>
              <div className={`pill ${ev.virality_risk > 7 ? 'danger' : 'info'}`}>
                Risk: {ev.virality_risk}/10
              </div>
            </div>
            <p style={{ fontStyle: 'italic', color: 'var(--muted)', marginBottom: '8px' }}>"{ev.reaction}"</p>
            <div style={{ display: 'flex', gap: '8px', fontSize: '11px' }}>
               <span style={{ color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                 <Zap size={10} /> {ev.trigger_phrase}
               </span>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
      {events.length === 0 && (
        <div style={{ padding: '20px', textAlign: 'center', color: 'var(--muted)', fontSize: '12px opacity: 0.5' }}>
          No agent activity detected yet...
        </div>
      )}
    </div>
  )
}
