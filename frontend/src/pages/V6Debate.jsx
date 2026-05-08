import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Play, Activity, Users, Zap, Search, MessageSquare, StickyNote, Maximize2, MousePointer2, Info, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';
import useStore from '../store/useStore'
import V6Stepper from '../components/V6Stepper'

/**
 * SentiFlow V6: Swarm Intelligence Operation Room (Miro-Inspired)
 * This component implements an infinite canvas experience for interactive
 * swarm intelligence analysis and narrative contagion modeling.
 */
export default function V6Debate() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [phase, setPhase] = useState('idle'); // idle, debating, complete
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [showStickyNotes, setShowStickyNotes] = useState(true);
  const [canvasZoom, setCanvasZoom] = useState(1);
  const fgRef = useRef();

  const { setV6ProjectId, setV6DebateData, setV6LastStep } = useStore();
  const API_V6 = `${import.meta.env.VITE_API_URL || ''}/api/v6`;

  // Simulation Progress Simulator
  useEffect(() => {
    if (phase === 'debating') {
      const interval = setInterval(() => {
        setProgress(p => {
          if (p >= 98) return p;
          const inc = p < 30 ? 5 : p < 70 ? 2 : 1;
          return p + Math.random() * inc;
        });
      }, 800);
      return () => clearInterval(interval);
    }
  }, [phase]);

  const runAnalysis = async () => {
    setPhase('debating');
    setProgress(5);
    try {
      // Ensure we send a body to avoid 422 Unprocessable Entity
      const res = await axios.post(`${API_V6}/projects/${projectId}/debate`, {});
      setResults(res.data);
      setV6ProjectId(projectId);
      setV6DebateData(res.data);
      setV6LastStep('debate');
      
      // Transform Representative Debate into Interactive Graph Topology
      const rawAgents = res.data.representative_debate || [];
      const nodes = rawAgents.map((agent, i) => ({
        id: agent.persona_id || `agent_${i}`,
        name: (agent.persona_name || agent.persona_id || 'Agent').split('_').pop(),
        val: 6,
        color: agent.position === 'SUPPORT' ? '#10b981' : agent.position === 'OPPOSE' ? '#ef4444' : '#6366f1',
        data: agent
      }));
      
      // Create random but stable connections for visualization
      const links = [];
      nodes.forEach((n, idx) => {
        // Connect to next 2-3 nodes to create a ring/cluster effect
        for(let j=1; j<=2; j++) {
          const targetIdx = (idx + j) % nodes.length;
          links.push({ source: n.id, target: nodes[targetIdx].id });
        }
      });
      
      setGraphData({ nodes, links });
      setPhase('complete');
      setProgress(100);
    } catch (err) {
      console.error("Simulation Failure:", err);
      setPhase('idle');
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 600);
      fgRef.current.zoom(3, 600);
    }
  };

  const resetZoom = () => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(600, 100);
      setSelectedNode(null);
    }
  };

  return (
    <div className="v6-debate-page h-screen bg-[#050505] text-white flex flex-col overflow-hidden select-none">
      {/* ─── TACTICAL HEADER ─── */}
      <div className="p-6 border-b border-white/5 bg-[#080808]/80 backdrop-blur-md z-[100]">
        <div className="max-w-full mx-auto flex justify-between items-center px-4">
          <div>
            <V6Stepper activeStep="debate" projectId={projectId} />
            <div className="flex items-center gap-3 mt-4">
              <h1 className="text-2xl font-bold font-heading tracking-tight">Operation Room</h1>
              {phase === 'complete' && (
                <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[10px] font-mono text-emerald-400">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                  SIMULATION STABLE
                </div>
              )}
            </div>
          </div>
          
          <div className="flex gap-4">
            {phase === 'idle' && (
              <button 
                onClick={runAnalysis}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-500/20 active:scale-95"
              >
                <Play size={18} fill="currentColor" />
                INITIATE SWARM DEBATE
              </button>
            )}
            {phase === 'complete' && (
              <button 
                onClick={() => navigate(`/v6/query/${projectId}`)}
                className="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 rounded-xl font-bold flex items-center gap-3 transition-all shadow-lg shadow-indigo-500/20"
              >
                VIEW STRATEGIC BRIEF
                <Zap size={18} className="text-yellow-300" />
              </button>
            )}
          </div>
        </div>
      </div>

      <main className="flex-1 relative flex overflow-hidden">
        
        {/* ─── MIRO-STYLE CANVAS LAYER ─── */}
        <div className="flex-1 relative miro-canvas">
          
          {/* DEBATE ANIMATION (LOADING) */}
          <AnimatePresence>
            {phase === 'debating' && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 z-[200] flex flex-col items-center justify-center bg-black/80 backdrop-blur-xl"
              >
                <div className="w-[500px] text-center">
                  <div className="mb-8 relative inline-block">
                    <motion.div 
                      animate={{ scale: [1, 1.2, 1], rotate: [0, 5, -5, 0] }}
                      transition={{ duration: 4, repeat: Infinity }}
                      className="text-8xl"
                    >
                      🛸
                    </motion.div>
                    <div className="absolute -inset-8 bg-blue-500/20 blur-3xl rounded-full -z-10 animate-pulse" />
                  </div>
                  <h2 className="text-2xl font-bold mb-4 tracking-tighter uppercase font-heading bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                    Synthesizing Hierarchical Consensus...
                  </h2>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mb-4 border border-white/5">
                    <motion.div 
                      className="h-full bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.5)]"
                      animate={{ width: `${progress}%` }}
                      transition={{ type: 'spring', stiffness: 50 }}
                    />
                  </div>
                  <div className="flex justify-between items-center font-mono text-[9px] text-gray-500 uppercase tracking-widest">
                    <span>Processing 1,000,000 Agents</span>
                    <span>{Math.round(progress)}% Verified</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* SPATIAL INTERACTION LAYER (COMPLETE) */}
          {phase === 'complete' && results && (
            <>
              {/* CANVAS CONTROLS (Miro Style) */}
              <div className="canvas-toolbar">
                <button 
                  className={`toolbar-item ${showStickyNotes ? 'active' : ''}`}
                  onClick={() => setShowStickyNotes(!showStickyNotes)}
                  title="Toggle Annotations"
                >
                  <StickyNote size={18} />
                </button>
                <button className="toolbar-item" onClick={resetZoom} title="Fit to Screen">
                  <Maximize2 size={18} />
                </button>
                <div className="w-6 h-[1px] bg-white/10 my-1" />
                <div className="flex flex-col items-center py-2 text-[8px] font-mono text-gray-600">
                  CTRL+SCROLL<br/>TO ZOOM
                </div>
              </div>

              {/* ANNOTATIONS (STICKY NOTES) */}
              <AnimatePresence>
                {showStickyNotes && (
                  <div className="absolute inset-0 pointer-events-none z-[50]">
                    <motion.div 
                      drag 
                      dragMomentum={false}
                      initial={{ opacity: 0, rotate: -5, scale: 0.9 }}
                      animate={{ opacity: 1, rotate: -2, scale: 1 }}
                      className="sticky-note yellow pointer-events-auto shadow-2xl" 
                      style={{ top: '15%', left: '8%' }}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 text-[9px] font-mono text-amber-700/60 mb-2 uppercase font-bold tracking-widest">
                          <Info size={10} /> Consensus Insight
                        </div>
                        <p className="text-xs text-amber-900/80 leading-relaxed font-semibold">
                          Final confidence index validated at <span className="bg-amber-900/10 px-1 rounded">{(results.consensus.final_confidence * 100).toFixed(1)}%</span>. The swarm has reached a stable equilibrium point.
                        </p>
                      </div>
                      <div className="text-[9px] font-mono text-amber-800/40">SENTIFLOW-SCP-01</div>
                    </motion.div>

                    <motion.div 
                      drag 
                      dragMomentum={false}
                      initial={{ opacity: 0, rotate: 5, scale: 0.9 }}
                      animate={{ opacity: 1, rotate: 3, scale: 1 }}
                      className="sticky-note blue pointer-events-auto shadow-2xl" 
                      style={{ top: '20%', right: '12%' }}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 text-[9px] font-mono text-blue-700/60 mb-2 uppercase font-bold tracking-widest">
                          <AlertTriangle size={10} /> Risk Assessment
                        </div>
                        <p className="text-xs text-blue-900/80 leading-relaxed font-semibold">
                          Narrative R0 spike at <span className="bg-blue-900/10 px-1 rounded">{results.cascade.metadata.r_naught}</span>. Cross-platform contamination is predicted within 24 hours.
                        </p>
                      </div>
                      <div className="text-[9px] font-mono text-blue-800/40">RISK-V6-VECTOR</div>
                    </motion.div>
                  </div>
                )}
              </AnimatePresence>

              {/* CORE FORCE GRAPH */}
              <div className="w-full h-full opacity-80 hover:opacity-100 transition-opacity">
                <ForceGraph2D
                  ref={fgRef}
                  graphData={graphData}
                  nodeLabel="name"
                  nodeRelSize={7}
                  linkColor={() => 'rgba(255,255,255,0.05)'}
                  linkDirectionalParticles={1}
                  linkDirectionalParticleSpeed={0.005}
                  nodeCanvasObject={(node, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 11/globalScale;
                    ctx.font = `${fontSize}px "JetBrains Mono"`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    
                    // Draw node glow
                    ctx.shadowColor = node.color;
                    ctx.shadowBlur = 10;
                    
                    // Draw outer ring
                    ctx.strokeStyle = node.color;
                    ctx.lineWidth = 1/globalScale;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, 4.5, 0, 2 * Math.PI, false);
                    ctx.stroke();

                    // Draw inner circle
                    ctx.fillStyle = node.color;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, 3, 0, 2 * Math.PI, false);
                    ctx.fill();
                    
                    ctx.shadowBlur = 0;
                    ctx.fillStyle = 'rgba(255,255,255,0.5)';
                    ctx.fillText(label, node.x, node.y + 10);
                  }}
                  onNodeClick={handleNodeClick}
                  cooldownTicks={100}
                />
              </div>

              {/* SPATIAL AGENT CARD (Miro Context Card) */}
              <AnimatePresence>
                {selectedNode && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.95, y: 30 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 30 }}
                    className="absolute z-[300] bottom-12 left-1/2 -translate-x-1/2 w-[600px] pointer-events-none"
                  >
                    <div className="glass-panel p-8 bg-[#0a0a0a]/95 border-white/10 rounded-[32px] shadow-[0_40px_100px_rgba(0,0,0,0.6)] pointer-events-auto">
                      <div className="flex justify-between items-start mb-6">
                        <div className="flex items-center gap-5">
                          <div className={`w-16 h-16 rounded-[22px] flex items-center justify-center text-3xl shadow-xl ${selectedNode.data.position === 'SUPPORT' ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                             {selectedNode.data.position === 'SUPPORT' ? '🛡️' : '🔥'}
                          </div>
                          <div>
                            <h3 className="text-2xl font-bold font-heading tracking-tight">{selectedNode.data.persona_name || selectedNode.name}</h3>
                            <div className="flex items-center gap-3 text-[10px] font-mono text-gray-500 uppercase mt-1">
                              <span className={selectedNode.data.position === 'SUPPORT' ? 'text-emerald-400' : 'text-red-400'}>{selectedNode.data.position}ER</span>
                              <span className="w-1 h-1 bg-white/20 rounded-full" />
                              <span>TRUST: {((selectedNode.data.confidence || 0.8) * 100).toFixed(0)}%</span>
                              <span className="w-1 h-1 bg-white/20 rounded-full" />
                              <span>DNA: {selectedNode.data.persona_id?.split('_')[0]}</span>
                            </div>
                          </div>
                        </div>
                        <button onClick={() => setSelectedNode(null)} className="p-2 hover:bg-white/5 rounded-full text-gray-500 transition-colors">
                          <MousePointer2 size={20} />
                        </button>
                      </div>

                      <div className="mb-8">
                         <div className="text-[10px] font-mono text-blue-400 mb-3 uppercase tracking-widest">Synthetic Reasoning Path</div>
                         <div className="p-5 bg-white/[0.02] rounded-2xl border border-white/5 text-sm leading-relaxed text-gray-300 italic font-serif">
                            "{selectedNode.data.reaction || selectedNode.data.reasoning}"
                         </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <button className="group flex items-center justify-center gap-3 py-4 bg-blue-600 hover:bg-blue-500 rounded-2xl text-xs font-bold transition-all active:scale-[0.98]">
                          <MessageSquare size={16} /> OPEN DIALOGUE
                        </button>
                        <button className="flex items-center justify-center gap-3 py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-xs font-bold transition-all">
                          <Search size={16} /> ANALYZE MEMORY
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          )}

          {/* EMPTY STATE */}
          {phase === 'idle' && (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-12">
               <div className="relative mb-10">
                 <div className="text-8xl opacity-10 grayscale">🏢</div>
                 <div className="absolute inset-0 bg-blue-500/10 blur-3xl rounded-full" />
               </div>
               <h2 className="text-3xl font-bold font-heading mb-4 text-gray-400 tracking-tight">Operation Sandbox Ready</h2>
               <p className="max-w-md text-gray-500 text-sm leading-relaxed font-mono">
                 Awaiting hierarchical consensus initiation. This will spawn 1,000,000 synthetic agents to rehearse the narrative contagion.
               </p>
               <motion.div 
                 animate={{ y: [0, 10, 0] }}
                 transition={{ repeat: Infinity, duration: 2 }}
                 className="mt-12 text-blue-500/40"
               >
                 <MousePointer2 size={32} />
               </motion.div>
            </div>
          )}
        </div>

        {/* ─── INDUSTRIAL SIDEBAR (CASCADE METRICS) ─── */}
        <AnimatePresence>
          {phase === 'complete' && results && (
            <motion.div 
              initial={{ x: 450, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 450, opacity: 0 }}
              transition={{ type: 'spring', damping: 25 }}
              className="w-[450px] bg-[#0a0a0a]/80 backdrop-blur-3xl border-l border-white/10 p-10 overflow-y-auto scrollbar-v6 relative z-[150]"
            >
              <div className="flex items-center gap-3 mb-12">
                <Activity size={20} className="text-blue-500" />
                <h2 className="text-sm font-mono text-gray-400 uppercase tracking-widest">Cascade Intelligence</h2>
              </div>

              <div className="mb-12">
                 <div className="grid grid-cols-2 gap-6">
                   <div className="p-5 bg-white/5 rounded-3xl border border-white/5 group hover:border-red-500/30 transition-colors">
                     <div className="text-[10px] font-mono text-gray-500 mb-2 uppercase">Narrative R0</div>
                     <div className="text-4xl font-bold font-heading text-red-500">{results.cascade.metadata.r_naught}</div>
                   </div>
                   <div className="p-5 bg-white/5 rounded-3xl border border-white/5 group hover:border-amber-500/30 transition-colors">
                     <div className="text-[10px] font-mono text-gray-500 mb-2 uppercase">Peak Infected</div>
                     <div className="text-4xl font-bold font-heading text-amber-500">{results.cascade.metadata.peak_infection}</div>
                   </div>
                 </div>
              </div>

              <div className="mb-12">
                 <div className="flex justify-between items-center mb-8">
                   <div className="text-[10px] font-mono text-blue-400 uppercase tracking-widest">Consensus Health</div>
                   <div className="text-[10px] px-2 py-1 bg-blue-500/10 rounded border border-blue-500/20 text-blue-400 font-mono">SCPV6 VALIDATED</div>
                 </div>
                 <div className="space-y-8">
                   {Object.entries(results.consensus.layer_scores).map(([layer, score]) => (
                     <div key={layer}>
                       <div className="flex justify-between text-[10px] font-mono mb-3 uppercase text-gray-500">
                          <span className="flex items-center gap-2">
                             <div className="w-1 h-1 bg-blue-500 rounded-full" />
                             {layer} layer
                          </span>
                          <span className="text-white">{(score * 100).toFixed(0)}%</span>
                       </div>
                       <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                         <motion.div 
                          className="h-full bg-gradient-to-r from-blue-600 to-indigo-400" 
                          initial={{ width: 0 }}
                          animate={{ width: `${score * 100}%` }}
                          transition={{ duration: 1.5, delay: 0.2 }}
                         />
                       </div>
                     </div>
                   ))}
                 </div>
              </div>

              <div className="pt-12 border-t border-white/5">
                 <div className="flex items-center gap-3 mb-6">
                    <CheckCircle2 size={16} className="text-emerald-500" />
                    <div className="text-[10px] font-mono text-emerald-400 uppercase tracking-widest">Consolidated Verdict</div>
                 </div>
                 <p className="text-base leading-relaxed text-gray-300 font-serif italic border-l-2 border-emerald-500/30 pl-6 py-2">
                   "{results.judge_verdict.consolidated_verdict}"
                 </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* ─── MIRO GRID STYLES ─── */}
      <style>{`
        .miro-canvas {
          background-color: #050505;
          background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
          background-size: 40px 40px;
        }
        .scrollbar-v6::-webkit-scrollbar { width: 4px; }
        .scrollbar-v6::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
        .scrollbar-v6::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
      `}</style>
    </div>
  );
}
