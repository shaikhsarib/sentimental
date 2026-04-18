import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ForceGraph2D from 'react-force-graph-2d'
import { FileText, Cpu, Database, Network } from 'lucide-react'
import useStore from '../store/useStore'

const API = import.meta.env.VITE_API_URL || ''

export default function Extraction() {
  const { project } = useStore()
  const [docTitle, setDocTitle] = useState('Seed Document')
  const [content, setContent] = useState('')
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [isProcessing, setIsProcessing] = useState(false)
  const [personas, setPersonas] = useState([])
  
  const handleUpload = async () => {
    if (!project) return alert('No active project. Go to Dashboard first.')
    setIsProcessing(true)
    
    try {
      await fetch(`${API}/api/projects/${project.project_id}/documents/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: docTitle, content, content_type: 'text' })
      })
      
      const res = await fetch(`${API}/api/projects/${project.project_id}/graph/build`, { method: 'POST' })
      const data = await res.json()
      
      const formattedGraph = {
         nodes: (data.nodes || []).map(n => ({ id: n.id, title: n.label, val: n.weight, color: '#0d9488' })),
         links: (data.edges || []).map(e => ({ source: e.source, target: e.target, val: e.weight }))
      }
      setGraphData(formattedGraph)
      setIsProcessing(false)
      
      // Real personas would be generated here in a full run, but for Extraction we mock the discovery
      setPersonas([
        { role: 'Regulator', bias: 'Strict Compliance', traits: ['Risk-Averse', 'Authoritative'] },
        { role: 'Investor', bias: 'Growth Focus', traits: ['Optimistic', 'Data-Driven'] },
        { role: 'Consumer', bias: 'Price Sensitive', traits: ['Skeptical', 'Vocal'] }
      ])
      
    } catch (e) {
      console.error(e)
      setIsProcessing(false)
    }
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="split-view" style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '32px' }}>
      
      {/* Left: Graph Neo4j Engine */}
      <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: 'fit-content' }}>
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Network size={20} color="var(--accent)" /> Entity Knowledge Graph
            </h2>
          </div>
          {graphData.nodes.length > 0 && <span className="pill info">{graphData.nodes.length} Nodes</span>}
        </div>
        
        <div style={{ border: '1px solid var(--border)', borderRadius: '12px', background: 'rgba(0, 0, 0, 0.2)', height: '500px', overflow: 'hidden' }}>
          {graphData.nodes.length > 0 ? (
            <ForceGraph2D
              graphData={graphData}
              nodeAutoColorBy="group"
              nodeLabel="title"
              linkColor={() => 'rgba(255,255,255,0.1)'}
              backgroundColor="transparent"
              width={600}
              height={500}
            />
          ) : (
            <div className="empty-state">
              <Database size={48} opacity={0.2} style={{ marginBottom: '16px' }} />
              <p>Waiting for document seed injection...</p>
            </div>
          )}
        </div>
      </div>

      {/* Right: Upload and Generation Feed */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div className="glass-panel">
          <h2 style={{ fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="var(--accent)" /> Seed Document
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <input className="input" value={docTitle} onChange={e => setDocTitle(e.target.value)} placeholder="Title" />
            <textarea className="textarea" placeholder="Paste intelligence report, news, or manifesto here to generate the world state..." value={content} onChange={e => setContent(e.target.value)} />
            <button className="btn" onClick={handleUpload} disabled={!content || isProcessing}>
              {isProcessing ? 'Processing NLP & Graph...' : 'Extract & Generate Engine'}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {personas.length > 0 && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="glass-panel">
               <h2 style={{ fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                 <Cpu size={18} color="var(--accent)" /> Discovered Demographics
               </h2>
               <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                 {personas.map((p, i) => (
                   <motion.div initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: i * 0.15 }} key={i} style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)', borderRadius: '8px' }}>
                     <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--accent-amber)' }}>{p.role} Profile</div>
                     <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '4px' }}>Bias: {p.bias}</div>
                     <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
                       {p.traits.map(t => <span key={t} className="pill" style={{ background: 'var(--bg-slate-soft)' }}>{t}</span>)}
                     </div>
                   </motion.div>
                 ))}
               </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

    </motion.div>
  )
}
