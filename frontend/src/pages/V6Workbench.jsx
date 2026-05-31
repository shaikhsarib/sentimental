import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Terminal, ShieldAlert, Cpu, Award, Users, Play, RefreshCw, 
  BookOpen, FolderOpen, UserCheck, HardDrive, Key, Brain, LayoutGrid, CheckCircle2 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import useStore from '../store/useStore';
import V6Stepper from '../components/V6Stepper';

export default function V6Workbench() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  // State for active domain (tech, finance, agriculture)
  const [activeDomain, setActiveDomain] = useState('tech');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentsList, setAgentsList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [learningStatus, setLearningStatus] = useState(null);
  const [calibrationStatus, setCalibrationStatus] = useState(null);

  const API_V6 = `${import.meta.env.VITE_API_URL || ''}/api/v6`;

  // Fetch synthesized agents on load or domain change
  useEffect(() => {
    fetchSwarmAgents();
  }, [projectId, activeDomain]);

  const fetchSwarmAgents = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_V6}/projects/${projectId}/agents?limit=100`);
      // Filter agents by active domain (tech, finance, agriculture)
      const domainAgents = res.data.filter(agent => 
        agent.domain?.toLowerCase() === activeDomain || 
        (activeDomain === 'tech' && !agent.domain) // fallback for legacy general
      );
      setAgentsList(domainAgents);
      if (domainAgents.length > 0) {
        setSelectedAgent(domainAgents[0]);
      } else {
        setSelectedAgent(null);
      }
    } catch (err) {
      console.error("Failed to load swarm agents:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLearn = async (agentId) => {
    setLearningStatus('loading');
    try {
      const res = await axios.post(`${API_V6}/projects/${projectId}/agents/${agentId}/learn`);
      setLearningStatus('success');
      // Reload agent data
      if (selectedAgent && selectedAgent.agent_id === agentId) {
        // Mock dynamic updates for visual polish
        setSelectedAgent(prev => ({
          ...prev,
          short_term_context: "continuous training logs updated. OSINT files processed.",
        }));
      }
      setTimeout(() => setLearningStatus(null), 3000);
    } catch (err) {
      console.error("Ingestion failed:", err);
      setLearningStatus('error');
    }
  };

  const handleCalibrate = async (agentId) => {
    setCalibrationStatus('loading');
    try {
      const payload = {
        debate_transcript: "Agent expressed mild uncertainty during the consensus debate. Needs optimization.",
        final_outcome: "Highly critical operational vulnerability resolved with non-sugarcoated verdict."
      };
      const res = await axios.post(`${API_V6}/projects/${projectId}/agents/${agentId}/calibrate`, payload);
      setCalibrationStatus('success');
      if (selectedAgent && selectedAgent.agent_id === agentId) {
        setSelectedAgent(prev => ({
          ...prev,
          system_prefix: res.data.calibrated_system_prefix || prev.system_prefix
        }));
      }
      setTimeout(() => setCalibrationStatus(null), 3000);
    } catch (err) {
      console.error("Self-reflection calibration failed:", err);
      setCalibrationStatus('error');
    }
  };

  const domains = [
    { id: 'tech', label: 'Tech Workspace', icon: Cpu, color: 'text-blue-400', border: 'border-blue-500/20' },
    { id: 'finance', label: 'Finance Hub', icon: ShieldAlert, color: 'text-emerald-400', border: 'border-emerald-500/20' },
    { id: 'agriculture', label: 'Agriculture Field', icon: Award, color: 'text-amber-400', border: 'border-amber-500/20' }
  ];

  return (
    <div className="v6-workbench-page h-screen bg-[#050505] text-white flex flex-col overflow-hidden select-none">
      {/* ─── TERMINAL HEADER ─── */}
      <div className="p-6 border-b border-white/5 bg-[#080808]/80 backdrop-blur-md z-[100]">
        <div className="max-w-full mx-auto flex justify-between items-center px-4">
          <div>
            <V6Stepper activeStep="workbench" projectId={projectId} />
            <div className="flex items-center gap-3 mt-4">
              <Terminal className="text-blue-500" size={24} />
              <h1 className="text-2xl font-bold font-heading tracking-tight">Swarm Workbench</h1>
              <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-[10px] font-mono text-blue-400">
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                MILLION-AGENT SWARM ACTIVE
              </div>
            </div>
          </div>
          
          <button 
            onClick={() => navigate(`/v6/debate/${projectId}`)}
            className="px-8 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-500/20 active:scale-95"
          >
            <Play size={18} fill="currentColor" />
            INITIATE PREDICT RUN
          </button>
        </div>
      </div>

      <main className="flex-1 flex overflow-hidden">
        {/* ─── DOMAINS SIDE PANEL (Tech, Finance, Ag) ─── */}
        <div className="w-80 border-r border-white/5 bg-[#070707]/90 flex flex-col p-6 overflow-y-auto scrollbar-v6 gap-6">
          <div className="text-[10px] font-mono text-gray-500 uppercase tracking-widest mb-2">Workspace Domains</div>
          
          <div className="flex flex-col gap-3">
            {domains.map((dom) => {
              const Icon = dom.icon;
              const isSelected = activeDomain === dom.id;
              return (
                <button
                  key={dom.id}
                  onClick={() => setActiveDomain(dom.id)}
                  className={`w-full p-4 rounded-2xl flex items-center justify-between text-left transition-all ${
                    isSelected 
                      ? 'bg-white/5 border border-white/10 shadow-lg' 
                      : 'hover:bg-white/[0.02] border border-transparent text-gray-400'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={dom.color} size={20} />
                    <span className="text-sm font-bold">{dom.label}</span>
                  </div>
                  {isSelected && <div className="w-2 h-2 bg-blue-500 rounded-full" />}
                </button>
              );
            })}
          </div>

          <div className="mt-8 border-t border-white/5 pt-6">
            <div className="text-[10px] font-mono text-gray-500 uppercase tracking-widest mb-4">Autonomous Agents</div>
            <div className="flex flex-col gap-2">
              {loading ? (
                <div className="flex items-center gap-2 p-3 text-xs text-gray-500">
                  <RefreshCw className="animate-spin" size={14} /> Loading swarm topology...
                </div>
              ) : agentsList.length === 0 ? (
                <div className="p-3 text-xs text-gray-500 italic bg-white/[0.01] border border-white/5 rounded-xl">
                  No generated personas found. Upload documents to synthesize a swarm.
                </div>
              ) : (
                agentsList.map(agent => (
                  <button
                    key={agent.agent_id}
                    onClick={() => setSelectedAgent(agent)}
                    className={`w-full p-3 rounded-xl text-left text-xs font-mono transition-all border ${
                      selectedAgent?.agent_id === agent.agent_id
                        ? 'bg-blue-500/10 border-blue-500/30 text-blue-400 font-bold'
                        : 'border-transparent hover:bg-white/[0.02] text-gray-400'
                    }`}
                  >
                    🚀 {agent.name?.split('(')[0].trim()}
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* ─── HIERARCHICAL Swarm Workbench Canvas (Page 1) ─── */}
        <div className="flex-1 relative flex flex-col bg-[#050505] p-8 overflow-y-auto scrollbar-v6 border-r border-white/5">
          <div className="text-[10px] font-mono text-blue-400 uppercase tracking-widest mb-6">Swarm Hierarchical Taxonomy Tree</div>
          
          <div className="flex-1 flex flex-col items-center justify-center min-h-[500px]">
            {activeDomain === 'tech' ? (
              <div className="flex flex-col items-center w-full max-w-2xl gap-8">
                {/* FIRST GEN BASE */}
                <div className="px-6 py-3 bg-[#0d0d0d] border border-blue-500/30 rounded-2xl flex items-center gap-3 text-xs font-mono text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.15)]">
                  <Cpu size={14} /> First Gen (Skills & Brain)
                </div>
                
                {/* CONNECTOR LINE */}
                <div className="w-[1px] h-6 bg-blue-500/30" />

                {/* LEADERSHIP ROW */}
                <div className="flex gap-6 items-center">
                  <div className="px-5 py-3 bg-white/5 border border-white/10 rounded-xl text-xs font-bold text-center">
                    👑 CEO
                  </div>
                  <div className="px-5 py-3 bg-white/5 border border-white/10 rounded-xl text-xs font-bold text-center">
                    💡 Co-Founder
                  </div>
                  <div className="px-5 py-3 bg-white/5 border border-white/10 rounded-xl text-xs font-bold text-center">
                    🛠️ CTO
                  </div>
                </div>

                <div className="w-[1px] h-6 bg-blue-500/30" />

                {/* CREATIVE AND DEV ROW */}
                <div className="flex gap-6 items-start">
                  {/* DESIGNER */}
                  <div className="flex flex-col items-center gap-3">
                    <div className="px-4 py-2.5 bg-purple-500/10 border border-purple-500/20 rounded-xl text-xs font-bold text-purple-400">
                      🎨 Designer (UI/UX)
                    </div>
                    <span className="text-[9px] font-mono text-gray-500">Design Infra</span>
                  </div>

                  {/* ENGINEERS BLOCK */}
                  <div className="flex flex-col items-center border border-white/5 p-4 rounded-2xl bg-white/[0.01]">
                    <div className="text-[9px] font-mono text-gray-400 mb-3 uppercase tracking-wider font-bold">Engineering Swarm</div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="px-3 py-1.5 bg-white/5 rounded-lg text-[10px] font-mono text-center">Web Dev</div>
                      <div className="px-3 py-1.5 bg-white/5 rounded-lg text-[10px] font-mono text-center">Software Eng</div>
                      <div className="px-3 py-1.5 bg-white/5 rounded-lg text-[10px] font-mono text-center">AI Engineer</div>
                      <div className="px-3 py-1.5 bg-white/5 rounded-lg text-[10px] font-mono text-center">ML Specialist</div>
                      <div className="px-3 py-1.5 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-[10px] font-mono text-center">Ethical Hacker</div>
                      <div className="px-3 py-1.5 bg-red-950/20 border border-red-900/30 text-red-500 rounded-lg text-[10px] font-mono text-center">Black Hat</div>
                    </div>
                  </div>

                  {/* MARKETING */}
                  <div className="px-4 py-2.5 bg-blue-500/10 border border-blue-500/20 rounded-xl text-xs font-bold text-blue-400">
                    📈 Marketer
                  </div>
                </div>

                <div className="w-[1px] h-6 bg-blue-500/30" />

                {/* ADVISORY & MARKET ROW */}
                <div className="flex gap-6 items-center">
                  <div className="px-4 py-2 bg-white/5 rounded-lg text-xs font-mono text-gray-400">💼 Investor</div>
                  <div className="px-4 py-2 bg-white/5 rounded-lg text-xs font-mono text-gray-400">⚖️ Advisor</div>
                  <div className="px-4 py-2 bg-white/5 rounded-lg text-xs font-mono text-gray-400">🚀 Hackathon Host</div>
                  <div className="px-4 py-2 bg-white/5 rounded-lg text-xs font-mono text-gray-400">👥 End User</div>
                </div>

              </div>
            ) : (
              <div className="text-center p-12 max-w-sm">
                <LayoutGrid className="mx-auto text-gray-600 mb-6" size={48} />
                <h3 className="text-lg font-bold mb-2">Hierarchical Graph Unlocked</h3>
                <p className="text-xs text-gray-500 leading-relaxed">
                  The {activeDomain} structural model is loaded in the background database and prepared for predictive runs. Use the predictor to trigger live consensus debates.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ─── DYNAMIC AGENT DIRECTORY INSPECTOR (Page 2) ─── */}
        <div className="w-[450px] bg-[#0a0a0a]/80 backdrop-blur-3xl p-8 overflow-y-auto scrollbar-v6 flex flex-col gap-8 relative z-[150]">
          {selectedAgent ? (
            <>
              {/* Identity Section */}
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-[10px] font-mono text-blue-400 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                    <UserCheck size={12} /> Active Agent Profile
                  </div>
                  <h2 className="text-2xl font-bold tracking-tight">{selectedAgent.name?.split('(')[0].trim()}</h2>
                  <div className="text-[10px] font-mono text-gray-500 mt-1 uppercase">
                    ROLE: {selectedAgent.role}
                  </div>
                </div>
                <div className="px-3 py-1 bg-white/5 rounded-full text-[10px] font-mono border border-white/5">
                  {selectedAgent.emotion_profile?.toUpperCase()}
                </div>
              </div>

              {/* Dynamic Agent Directory Inspector (The 5 Folders) */}
              <div className="border-t border-white/5 pt-6 flex flex-col gap-5">
                <div className="text-[10px] font-mono text-gray-500 uppercase tracking-widest flex items-center gap-2">
                  <FolderOpen size={12} className="text-gray-400" /> Filesystem Directory Inspector
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-4 bg-white/[0.01] border border-white/5 rounded-2xl flex items-center gap-3">
                    <HardDrive className="text-blue-500" size={16} />
                    <div>
                      <div className="text-[10px] font-mono text-gray-400">/data</div>
                      <span className="text-[9px] font-mono text-gray-500 font-bold">identity.json</span>
                    </div>
                  </div>

                  <div className="p-4 bg-white/[0.01] border border-white/5 rounded-2xl flex items-center gap-3">
                    <Brain className="text-purple-500" size={16} />
                    <div>
                      <div className="text-[10px] font-mono text-gray-400">/brain</div>
                      <span className="text-[9px] font-mono text-gray-500 font-bold">memory_log.json</span>
                    </div>
                  </div>

                  <div className="p-4 bg-white/[0.01] border border-white/5 rounded-2xl flex items-center gap-3">
                    <Key className="text-emerald-500" size={16} />
                    <div>
                      <div className="text-[10px] font-mono text-gray-400">/skills</div>
                      <span className="text-[9px] font-mono text-gray-500 font-bold">skills.json</span>
                    </div>
                  </div>

                  <div className="p-4 bg-white/[0.01] border border-white/5 rounded-2xl flex items-center gap-3">
                    <BookOpen className="text-amber-500" size={16} />
                    <div>
                      <div className="text-[10px] font-mono text-gray-400">/training</div>
                      <span className="text-[9px] font-mono text-gray-500 font-bold">history.json</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Brain Memories */}
              <div className="border-t border-white/5 pt-6 flex flex-col gap-3">
                <div className="text-[10px] font-mono text-blue-400 uppercase tracking-widest">Cognitive State (/brain)</div>
                <div className="p-5 bg-white/[0.02] border border-white/5 rounded-2xl text-xs leading-relaxed text-gray-400 italic font-serif">
                  "{selectedAgent.short_term_context || 'Awaiting continuous training documents...'}"
                </div>
              </div>

              {/* System Prefix Calibration */}
              <div className="border-t border-white/5 pt-6 flex flex-col gap-3">
                <div className="text-[10px] font-mono text-blue-400 uppercase tracking-widest">Debate Rules (/self_trained)</div>
                <div className="p-5 bg-[#080808] border border-white/5 rounded-2xl text-[10px] font-mono text-gray-500 max-h-40 overflow-y-auto scrollbar-v6 leading-normal">
                  {selectedAgent.system_prefix || 'No adversarial calibration recorded. Trigger self-training to optimize.'}
                </div>
              </div>

              {/* Direct Executable Actions (Continuous Ingestion & Self-Training) */}
              <div className="border-t border-white/5 pt-6 grid grid-cols-2 gap-4">
                <button 
                  onClick={() => handleLearn(selectedAgent.agent_id)}
                  disabled={learningStatus === 'loading'}
                  className="flex items-center justify-center gap-2 py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/30 rounded-2xl text-xs font-bold transition-all active:scale-[0.98]"
                >
                  <RefreshCw size={14} className={learningStatus === 'loading' ? 'animate-spin' : ''} />
                  {learningStatus === 'success' ? 'LEARNED ✓' : 'INGEST DATA'}
                </button>

                <button 
                  onClick={() => handleCalibrate(selectedAgent.agent_id)}
                  disabled={calibrationStatus === 'loading'}
                  className="flex items-center justify-center gap-2 py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-xs font-bold transition-all disabled:opacity-50"
                >
                  <Brain size={14} className={calibrationStatus === 'loading' ? 'animate-pulse' : ''} />
                  {calibrationStatus === 'success' ? 'CALIBRATED ✓' : 'SELF-REFLECT'}
                </button>
              </div>

              {/* Success Notification Banners */}
              <AnimatePresence>
                {learningStatus === 'success' && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs font-mono flex items-center gap-2"
                  >
                    <CheckCircle2 size={14} /> Continuous training ingested! Memory updated in /brain/
                  </motion.div>
                )}
                {calibrationStatus === 'success' && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="p-4 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-xl text-xs font-mono flex items-center gap-2"
                  >
                    <CheckCircle2 size={14} /> Adversarial rules calibrated in /self_trained/
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-gray-500">
               <Cpu className="mb-4 text-gray-600" size={32} />
               <p className="text-xs font-mono">Select an agent to inspect directory modules.</p>
            </div>
          )}
        </div>
      </main>

      {/* ─── MIRO GRID STYLES ─── */}
      <style>{`
        .scrollbar-v6::-webkit-scrollbar { width: 4px; }
        .scrollbar-v6::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
        .scrollbar-v6::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
      `}</style>
    </div>
  );
}
