import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_BASE = "http://localhost:8000/api/v6";

export default function AgentExplorer() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await axios.get(`${API_BASE}/agents`);
      setAgents(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const fetchAgentDetails = async (agentId) => {
    try {
      const res = await axios.get(`${API_BASE}/agents/${agentId}`);
      setSelectedAgent(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 1: return "text-purple-400 bg-purple-500/10 border-purple-500/20";
      case 2: return "text-blue-400 bg-blue-500/10 border-blue-500/20";
      case 3: return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      default: return "text-gray-400 bg-gray-500/10 border-gray-500/20";
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tighter mb-2">SWARM EXPLORER // POPULATION</h1>
            <p className="text-gray-400 font-mono text-sm uppercase">BROWSE SYNTHESIZED AGENT DNA</p>
          </div>
          <button 
            onClick={() => navigate('/')}
            className="px-6 py-2 border border-white/10 hover:bg-white/5 rounded transition-all font-mono text-xs"
          >
            ← BACK TO TERMINAL
          </button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Agent List */}
          <div className="lg:col-span-1 glass p-6 rounded-2xl border border-white/10 h-[80vh] flex flex-col">
            <h3 className="text-sm font-mono text-gray-500 mb-4 uppercase tracking-widest flex justify-between">
              <span>Agent Directory</span>
              <span className="text-blue-400">TOTAL: {agents.length}+</span>
            </h3>
            
            {loading ? (
              <div className="flex-1 flex items-center justify-center font-mono text-blue-400 animate-pulse">
                INITIALIZING POPULATION INDEX...
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto pr-2 space-y-2 scrollbar-v6">
                {agents.map(agent => (
                  <div 
                    key={agent.agent_id}
                    onClick={() => fetchAgentDetails(agent.agent_id)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer ${
                      selectedAgent?.agent_id === agent.agent_id 
                        ? 'bg-blue-500/20 border-blue-500/50' 
                        : 'bg-white/5 border-white/5 hover:border-white/20'
                    }`}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm truncate pr-2">{agent.name}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-mono border ${getTierColor(agent.tier)}`}>
                        T{agent.tier}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 truncate">{agent.role}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right: Agent Details */}
          <div className="lg:col-span-2">
            {selectedAgent ? (
              <div className="glass p-8 rounded-2xl border border-white/10 space-y-8 animate-fade-in">
                {/* Header Profile */}
                <div className="flex items-start justify-between border-b border-white/10 pb-8">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-3xl font-bold">{selectedAgent.name}</h2>
                      <span className={`text-xs px-3 py-1 rounded-full font-mono border ${getTierColor(selectedAgent.tier)}`}>
                        TIER {selectedAgent.tier} {selectedAgent.is_synthetic ? 'SYNTHETIC' : 'GROUNDED'}
                      </span>
                    </div>
                    <p className="text-gray-400 font-mono">{selectedAgent.role} // {selectedAgent.domain}</p>
                    <div className="mt-4 inline-block px-3 py-1 bg-red-500/10 border border-red-500/20 rounded text-red-400 font-mono text-xs">
                      PROFILE: {selectedAgent.emotion_profile.toUpperCase()}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-gray-500 font-mono block mb-1">UUID</span>
                    <span className="text-xs text-gray-600 font-mono">{selectedAgent.agent_id.split('-')[0]}...</span>
                  </div>
                </div>

                {/* Skills DNA */}
                <div>
                  <h3 className="text-sm font-mono text-gray-500 mb-4 uppercase tracking-widest">Cognitive DNA (Skills)</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedAgent.skills?.map((skill, i) => (
                      <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/5">
                        <div className="flex justify-between items-center mb-2">
                          <span className="font-bold text-sm">{skill.skill_name}</span>
                          <span className="text-[10px] font-mono text-blue-400">LVL {skill.skill_level}/10</span>
                        </div>
                        <div className="flex gap-2 flex-wrap">
                          {skill.activation_triggers?.map((t, j) => (
                            <span key={j} className="text-[10px] bg-white/10 px-2 py-0.5 rounded text-gray-300">
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Training Scenarios */}
                <div>
                  <h3 className="text-sm font-mono text-gray-500 mb-4 uppercase tracking-widest">Training History</h3>
                  <div className="space-y-4">
                    {selectedAgent.training?.map((t, i) => (
                      <div key={i} className="p-4 bg-blue-500/5 rounded-xl border border-blue-500/20">
                        <p className="text-sm text-gray-300 italic mb-3">"{t.scenario}"</p>
                        <div className="grid grid-cols-2 gap-4 mb-3">
                          <div>
                            <span className="text-[10px] text-gray-500 font-mono block">OUTCOME</span>
                            <span className="text-xs text-emerald-400">{t.outcome}</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-gray-500 font-mono block">VIRALITY RISK</span>
                            <span className="text-xs text-red-400">{t.virality_risk}/10</span>
                          </div>
                        </div>
                        <div className="pt-3 border-t border-white/5">
                          <span className="text-[10px] text-gray-500 font-mono block mb-1">LESSON LEARNED</span>
                          <span className="text-xs text-blue-200">{t.lesson}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full min-h-[500px] flex items-center justify-center border border-dashed border-white/10 rounded-2xl">
                <span className="font-mono text-gray-600">SELECT AN AGENT TO VIEW DNA</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        .glass { background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(20px); }
        .scrollbar-v6::-webkit-scrollbar { width: 4px; }
        .scrollbar-v6::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
        .scrollbar-v6::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        .animate-fade-in { animation: fadeIn 0.3s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}
