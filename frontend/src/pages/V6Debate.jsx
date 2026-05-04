import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = "http://localhost:8000/api/v6";

export default function V6Debate() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [intent, setIntent] = useState("Analyze potential contagion risk and adversarial narratives.");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [phase, setPhase] = useState("idle"); // idle, generating, mass, representative, arbitration, complete
  const [progress, setProgress] = useState(0);

  const startDebate = async () => {
    setLoading(true);
    setPhase("generating");
    
    // Simulate progress while waiting for backend
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 95) return p;
        return p + Math.random() * 5;
      });
    }, 1000);

    try {
      const res = await axios.post(`${API_BASE}/projects/${projectId}/debate`, { 
        intent,
        target_count: 1000 // In V6 this would be 1,000,000 but for demo we use 1K
      });
      setResults(res.data);
      setPhase("complete");
      setProgress(100);
    } catch (err) {
      console.error(err);
      setPhase("error");
    }
    clearInterval(interval);
    setLoading(false);
  };

  return (
    <div className="v6-debate-page p-8 min-h-screen bg-[#050505] text-white">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tighter mb-2">OPERATION ROOM // SWARM DEBATE</h1>
            <p className="text-gray-400 font-mono text-sm uppercase">PROJECT: {projectId} // V6 HIERARCHICAL CONSENSUS</p>
          </div>
          {phase === "complete" && (
            <button 
              onClick={() => navigate(`/v6/query/${projectId}`, { state: { debateData: results } })}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-500 rounded-full font-bold text-sm tracking-widest transition-all shadow-lg shadow-blue-500/20"
            >
              PROCEED TO PERSPECTIVE ANALYSIS →
            </button>
          )}
          {phase === "complete" && (
            <div className="text-right">
              <span className="text-[10px] text-gray-500 font-mono">CONFIDENCE INDEX</span>
              <p className="text-3xl font-bold text-blue-400">{(results.consensus.final_confidence * 100).toFixed(1)}%</p>
            </div>
          )}
        </header>

        {phase === "idle" && (
          <div className="glass p-12 rounded-3xl border border-white/10 text-center">
            <h2 className="text-2xl font-bold mb-4">Set Simulation Intent</h2>
            <textarea 
              className="w-full max-w-2xl bg-white/5 border border-white/10 p-6 rounded-2xl focus:outline-none focus:border-blue-500 transition-all text-center text-lg mb-8"
              rows={3}
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
            />
            <button 
              onClick={startDebate}
              className="bg-blue-600 hover:bg-blue-500 px-12 py-4 rounded-2xl font-bold text-xl transition-all shadow-xl shadow-blue-500/20"
            >
              LAUNCH MILLION-AGENT SWARM
            </button>
          </div>
        )}

        {(phase === "generating" || phase === "mass") && (
          <div className="space-y-8">
            <div className="glass p-8 rounded-2xl border border-white/10">
              <div className="flex justify-between mb-4">
                <span className="font-mono text-sm text-blue-400 animate-pulse">
                  {phase === "generating" ? ">>> GENERATING SYNTHETIC PERSONAS" : ">>> LAYER 1: MASS CONSENSUS IN PROGRESS"}
                </span>
                <span className="font-mono text-sm">{Math.round(progress)}%</span>
              </div>
              <div className="h-4 bg-white/5 rounded-full overflow-hidden border border-white/10 p-1">
                <div 
                  className="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="grid grid-cols-3 gap-4 mt-6 text-[10px] font-mono text-gray-500">
                <div className="p-3 bg-white/5 rounded-lg border border-white/5">SHARD_SIZE: 50</div>
                <div className="p-3 bg-white/5 rounded-lg border border-white/5">CONCURRENCY: 10_WORKERS</div>
                <div className="p-3 bg-white/5 rounded-lg border border-white/5">TPS: ~120_AGENTS/SEC</div>
              </div>
            </div>
          </div>
        )}

        {phase === "complete" && results && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left: Consensus & Cascade Stats */}
            <div className="lg:col-span-1 space-y-8">
              <div className="glass p-8 rounded-2xl border border-white/10">
                <h3 className="text-sm font-mono text-gray-500 mb-6">HIERARCHICAL CONSENSUS</h3>
                <div className="space-y-6">
                  {Object.entries(results.consensus.layer_scores).map(([layer, score]) => (
                    <div key={layer}>
                      <div className="flex justify-between text-xs font-mono mb-2">
                        <span className="uppercase">{layer}</span>
                        <span>{(score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{ width: `${score * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass p-8 rounded-2xl border border-white/10">
                <h3 className="text-sm font-mono text-gray-500 mb-4">CASCADE METRICS (PHASE 4)</h3>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="p-3 bg-white/5 rounded-lg border border-white/5">
                    <span className="text-[10px] text-gray-500">R0 INDEX</span>
                    <p className="text-xl font-bold text-red-400">{results.cascade.metadata.r_naught}</p>
                  </div>
                  <div className="p-3 bg-white/5 rounded-lg border border-white/5">
                    <span className="text-[10px] text-gray-500">PEAK INF.</span>
                    <p className="text-xl font-bold text-amber-400">{results.cascade.metadata.peak_infection}</p>
                  </div>
                </div>
                <div className="space-y-2">
                   <div className="flex justify-between text-[10px] font-mono">
                      <span>AFFECTED POPULATION</span>
                      <span>{results.cascade.metadata.total_affected} / {results.total_processed}</span>
                   </div>
                   <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-red-500" style={{ width: `${(results.cascade.metadata.total_affected / results.total_processed) * 100}%` }} />
                   </div>
                </div>
              </div>
            </div>

            {/* Right: Detailed Debate & Judge */}
            <div className="lg:col-span-2 space-y-8">
              <div className="glass p-8 rounded-2xl border border-white/10">
                <h3 className="text-sm font-mono text-gray-500 mb-6">INSTITUTIONAL ARBITER VERDICT</h3>
                <div className="p-6 bg-blue-500/5 border border-blue-500/20 rounded-xl mb-6">
                  <p className="text-blue-200 leading-relaxed italic">"{results.judge_verdict.consolidated_verdict}"</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                    <span className="text-[10px] font-mono text-gray-500">NARRATIVE R0 (OFFICIAL)</span>
                    <p className="text-2xl font-bold text-red-400">{results.judge_verdict.narrative_r0}</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                    <span className="text-[10px] font-mono text-gray-500">WINNING EVIDENCE</span>
                    <p className="text-sm font-bold truncate">{results.judge_verdict.evidence_winner || "Decentralized"}</p>
                  </div>
                </div>
              </div>

              {/* New: SEIR Propagation Visualization */}
              <div className="glass p-8 rounded-2xl border border-white/10">
                <h3 className="text-sm font-mono text-gray-500 mb-6">SENTIMENT PROPAGATION (SEIR)</h3>
                <div className="h-[200px] flex items-end gap-1">
                  {results.cascade.history.map((step, i) => (
                    <div key={i} className="flex-1 flex flex-col gap-0.5">
                       <div className="bg-red-500/80 w-full" style={{ height: `${(step.I / results.total_processed) * 100}%` }} />
                       <div className="bg-amber-500/40 w-full" style={{ height: `${(step.E / results.total_processed) * 100}%` }} />
                    </div>
                  ))}
                </div>
                <div className="flex justify-between mt-2 text-[10px] font-mono text-gray-600">
                   <span>STEP 0</span>
                   <span>T-PROJECTED</span>
                </div>
              </div>

              <div className="glass p-8 rounded-2xl border border-white/10">
                <h3 className="text-sm font-mono text-gray-500 mb-6">REPRESENTATIVE VOICES</h3>
                <div className="space-y-4 max-h-[300px] overflow-y-auto pr-4 scrollbar-v6">
                  {results.representative_debate.map((agent, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-all">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-bold text-sm">{agent.persona_name}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${agent.position === 'SUPPORT' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                          {agent.position}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 italic line-clamp-2">"{agent.reaction}"</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); }
        .scrollbar-v6::-webkit-scrollbar { width: 4px; }
        .scrollbar-v6::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
        .scrollbar-v6::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
      `}</style>
    </div>
  );
}
