import { useEffect, useState, useRef, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  Terminal,
  Activity,
  ChevronRight
} from 'lucide-react'
import useStore from '../store/useStore'
import ForceGraph2D from 'react-force-graph-2d'
import ForceGraph3D from 'react-force-graph-3d'
import Sidebar from '../components/Sidebar'
import WorkbenchPanel from '../components/WorkbenchPanel'
import { buildClusterGraph, buildSubgraph, DEFAULT_MAX_VISIBLE_NODES } from '../utils/graphLod'

const API = import.meta.env.VITE_API_URL || ''

export default function OperationRoom() {
  const {
    project,
    activeStage,
    setActiveStage,
    activeNode,
    setActiveNode,
    latestRun,
    sidebarOpen,
    workbenchMode,
    setWorkbenchMode
  } = useStore()

  const fgRef = useRef()
  const [dimensions, setDimensions] = useState({ width: window.innerWidth, height: window.innerHeight })
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [clusterMode, setClusterMode] = useState(true)
  const [useWebGL, setUseWebGL] = useState(true)
  const [activeClusterId, setActiveClusterId] = useState(null)
  const [autoExpand, setAutoExpand] = useState(true)
  const autoExpandRef = useRef(false)

  useEffect(() => {
    const handleResize = () => {
      const sidebarWidth = sidebarOpen ? 260 : 0
      const workbenchWidth = 380
      setDimensions({
        width: window.innerWidth - sidebarWidth - workbenchWidth,
        height: window.innerHeight - 56
      })
    }
    window.addEventListener('resize', handleResize)
    handleResize()
    return () => window.removeEventListener('resize', handleResize)
  }, [sidebarOpen])

  // --- Tactical Graph Rendering ---
  const handleNodeClick = useCallback((node) => {
    if (node.isCluster) {
      setActiveClusterId(node.id)
      return
    }
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 1000)
      fgRef.current.zoom(4, 1000)
    }
    setActiveNode(node)
  }, [fgRef, setActiveNode])

  const renderNode = useCallback((node, ctx, globalScale) => {
    if (node.isCluster) {
      const label = node.label || node.id
      const fontSize = 12 / globalScale
      ctx.font = `${fontSize}px var(--font-mono)`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillStyle = 'rgba(15, 23, 42, 0.8)'
      ctx.beginPath()
      ctx.arc(node.x, node.y, node.val * 1.4, 0, 2 * Math.PI, false)
      ctx.fill()
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.4)'
      ctx.lineWidth = 1 / globalScale
      ctx.stroke()
      ctx.fillStyle = 'rgba(226, 232, 240, 0.9)'
      ctx.fillText(label, node.x, node.y + node.val * 2)
      return
    }
    const label = node.id
    const fontSize = 12 / globalScale
    ctx.font = `${fontSize}px var(--font-mono)`
    const textWidth = ctx.measureText(label).width
    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2)

    const isHighRisk = node.risk >= 7 || activeNode?.id === node.id
    if (isHighRisk) {
      const pulseSec = Date.now() / 1000
      const radius = 6 + Math.sin(pulseSec * 4) * 2
      ctx.beginPath()
      ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false)
      ctx.strokeStyle = activeNode?.id === node.id ? 'var(--accent)' : 'rgba(239, 68, 68, 0.4)'
      ctx.lineWidth = 1 / globalScale
      ctx.stroke()
    }

    ctx.beginPath()
    ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false)
    ctx.fillStyle = activeNode?.id === node.id ? 'var(--accent)' : (node.risk >= 7 ? '#ef4444' : '#64748b')
    ctx.fill()

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
    ctx.beginPath()
    ctx.moveTo(link.source.x, link.source.y)
    ctx.lineTo(link.target.x, link.target.y)
    ctx.strokeStyle = 'rgba(203, 213, 225, 0.4)'
    ctx.lineWidth = Math.max(0.5, 2 / globalScale)
    ctx.stroke()

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

  useEffect(() => {
    const loadGraph = async () => {
      const res = await fetch(`${API}/api/projects/${project?.project_id}/graph`)
      if (res.ok) {
        const data = await res.json()
        setGraphData({
          nodes: data.nodes.map(n => ({ id: n.id, ...n })),
          links: data.links || data.edges || []
        })
      }
    }
    if (project?.project_id) loadGraph()
  }, [activeStage, project?.project_id])

  const clusterKey = useMemo(() => (node) => {
    const risk = typeof node.risk === 'number' ? node.risk : 0
    const riskBucket = risk >= 7 ? 'HIGH_RISK' : risk >= 4 ? 'MID_RISK' : 'LOW_RISK'
    const group = node.group || node.type || riskBucket
    return { key: group, label: group, color: '#60a5fa' }
  }, [])

  const clusterGraph = useMemo(() => {
    return buildClusterGraph(graphData.nodes, graphData.links, clusterKey)
  }, [graphData, clusterKey])

  const largestClusterId = useMemo(() => {
    let topId = null
    let maxCount = 0
    Object.values(clusterGraph.clusters).forEach(cluster => {
      if (cluster.memberCount > maxCount) {
        maxCount = cluster.memberCount
        topId = cluster.id
      }
    })
    return topId
  }, [clusterGraph])

  const shouldCluster = clusterMode && graphData.nodes.length > DEFAULT_MAX_VISIBLE_NODES
  const activeCluster = activeClusterId ? clusterGraph.clusters[activeClusterId] : null
  const activeGraph = useMemo(() => {
    if (activeCluster) {
      return buildSubgraph(graphData.nodes, graphData.links, activeCluster.members)
    }
    if (shouldCluster) {
      return clusterGraph.graph
    }
    return graphData
  }, [graphData, shouldCluster, activeCluster, clusterGraph])

  const getZoomLevel = (event) => {
    if (event?.k) return event.k
    if (event?.transform?.k) return event.transform.k
    if (fgRef.current?.zoom) return fgRef.current.zoom()
    const camera = fgRef.current?.camera?.()
    if (camera?.position?.z) {
      return Math.min(4, Math.max(0.4, 200 / camera.position.z))
    }
    return null
  }

  const handleAutoExpand = (zoomLevel) => {
    if (!autoExpand || !shouldCluster || !largestClusterId || zoomLevel === null) return
    if (!activeClusterId && zoomLevel >= 2.2 && !autoExpandRef.current) {
      setActiveClusterId(largestClusterId)
      autoExpandRef.current = true
    } else if (activeClusterId && zoomLevel <= 1.1 && autoExpandRef.current) {
      setActiveClusterId(null)
      autoExpandRef.current = false
    }
  }

  return (
    <div className="workspace-shell">
      <Sidebar />

      <main className="workspace-canvas">
        {/* Navigation Breadcrumbs / Header */}
        <header className="mission-path">
          <div className="mission-step active uppercase">
            <Shield size={14} />
            <span>MISSION // {activeStage}</span>
          </div>
          <ChevronRight size={12} className="text-muted" />
          <div className="mission-step">
            <Activity size={12} />
            <span>{latestRun?.objective || 'OPERATIONAL_SCAN'}</span>
          </div>
        </header>

        {/* Central Intelligence Graph */}
        <div className="graph-container">
          <div className="graph-tools">
            <button
              type="button"
              className={`graph-chip ${clusterMode ? 'active' : ''}`}
              onClick={() => {
                setClusterMode((prev) => !prev)
                setActiveClusterId(null)
                autoExpandRef.current = false
              }}
            >
              CLUSTERS
            </button>
            <button
              type="button"
              className={`graph-chip ${useWebGL ? 'active' : ''}`}
              onClick={() => setUseWebGL((prev) => !prev)}
            >
              WEBGL
            </button>
            <button
              type="button"
              className={`graph-chip ${autoExpand ? 'active' : ''}`}
              onClick={() => {
                setAutoExpand((prev) => !prev)
                autoExpandRef.current = false
              }}
            >
              AUTO
            </button>
            {activeCluster && (
              <button
                type="button"
                className="graph-chip"
                onClick={() => setActiveClusterId(null)}
              >
                BACK
              </button>
            )}
            <span className="graph-chip muted">{activeGraph.nodes.length.toLocaleString()} visible</span>
          </div>
          {useWebGL ? (
            <ForceGraph3D
              ref={fgRef}
              graphData={activeGraph}
              nodeLabel={(node) => node.label || node.id}
              nodeColor={(node) => node.color || (node.isCluster ? '#60a5fa' : '#94a3b8')}
              linkColor={() => 'rgba(203, 213, 225, 0.25)'}
              linkWidth={(link) => Math.max(0.3, (link.value || link.weight || 1) * 0.2)}
              width={dimensions.width}
              height={dimensions.height}
              onNodeClick={handleNodeClick}
              cooldownTicks={60}
              d3AlphaDecay={0.03}
              d3VelocityDecay={0.4}
              onEngineTick={() => handleAutoExpand(getZoomLevel())}
            />
          ) : (
            <ForceGraph2D
              ref={fgRef}
              graphData={activeGraph}
              nodeCanvasObject={renderNode}
              linkCanvasObject={renderLink}
              backgroundColor="#ffffff"
              width={dimensions.width}
              height={dimensions.height}
              onNodeClick={handleNodeClick}
              cooldownTicks={100}
              d3AlphaDecay={0.02}
              d3VelocityDecay={0.3}
              onZoomEnd={(event) => handleAutoExpand(getZoomLevel(event))}
            />
          )}
        </div>

        {/* Floating Simulation Status (Only during swarm) */}
        <AnimatePresence>
          {activeStage === 'swarm' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="tactical-overlay"
              style={{ bottom: '24px', left: '50%', transform: 'translateX(-50%)', width: 'auto' }}
            >
              <div className="glass-panel" style={{ padding: '8px 24px', display: 'flex', alignItems: 'center', gap: '20px', borderTop: '2px solid var(--success)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div className="animate-pulse" style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--success)' }} />
                  <div className="font-mono" style={{ fontSize: '11px' }}>SIMULATION_STREAM_ACTIVE</div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <WorkbenchPanel />
    </div>
  )
}
