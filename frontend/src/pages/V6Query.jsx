import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { FileText, Download, Share2 } from 'lucide-react';
import axios from 'axios';

const PERSPECTIVES = [
  { id: 'businessman', name: 'Businessman', icon: '💼', desc: 'ROI, Moat, Strategy' },
  { id: 'investor', name: 'Investor', icon: '📈', desc: 'Risk, Upside, TAM' },
  { id: 'engineer', name: 'Engineer', icon: '⚙️', desc: 'Feasibility, Scale' },
  { id: 'policy', name: 'Policy Maker', icon: '🏛️', desc: 'Regulation, Ethics' },
  { id: 'student', name: 'Student', icon: '🎓', desc: 'Learning, Career' },
  { id: 'university', name: 'Academic', icon: '🔬', desc: 'Rigor, Theory' }
];

export default function V6Query() {
  const { projectId } = useParams();
  const location = useLocation();
  const [selectedP, setSelectedP] = useState('businessman');
  const [query, setQuery] = useState("How does this narrative impact long-term brand equity and market positioning?");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [debateData, setDebateData] = useState(location.state?.debateData || null);
  const [queryResults, setQueryResults] = useState({});
  const [exporting, setExporting] = useState(false);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`http://localhost:8000/api/v6/projects/${projectId}/query`, {
        query,
        perspective: selectedP,
        debate_data: debateData
      });
      setResult(res.data);
      setQueryResults(prev => ({ ...prev, [selectedP]: res.data }));
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await axios.post(`http://localhost:8000/api/v6/projects/${projectId}/export`, {
        debate_data: debateData,
        queries: queryResults
      });
      window.open(`http://localhost:8000${res.data.download_url}`, '_blank');
    } catch (err) {
      console.error(err);
    }
    setExporting(false);
  };

  return (
    <div className="v6-query-page p-8 min-h-screen bg-[#050505] text-white">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tighter mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              SWARM INTELLIGENCE GATEWAY
            </h1>
            <p className="text-gray-400 font-mono text-sm">SELECT PERSPECTIVE // QUERY MILLION-AGENT COLLECTIVE</p>
          </div>
          <button 
            onClick={handleExport}
            disabled={exporting}
            className="flex items-center gap-2 px-6 py-2 bg-white/5 border border-white/10 rounded-full text-xs font-mono hover:bg-white/10 transition-all disabled:opacity-50"
          >
            <FileText size={14} className="text-purple-400" />
            {exporting ? "GENERATING PDF..." : "EXPORT STRATEGIC BRIEF"}
          </button>
        </header>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
          {PERSPECTIVES.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedP(p.id)}
              className={`p-6 rounded-2xl border transition-all flex flex-col items-center text-center gap-2 ${
                selectedP === p.id 
                ? 'bg-purple-500/10 border-purple-500 shadow-lg shadow-purple-500/20' 
                : 'bg-white/5 border-white/10 hover:border-white/20'
              }`}
            >
              <span className="text-3xl">{p.icon}</span>
              <span className="font-bold text-sm">{p.name}</span>
              <span className="text-[10px] text-gray-500 font-mono">{p.desc}</span>
            </button>
          ))}
        </div>

        <div className="glass p-8 rounded-3xl border border-white/10 mb-12">
          <textarea 
            className="w-full bg-white/5 border border-white/10 p-6 rounded-2xl focus:outline-none focus:border-purple-500 transition-all text-lg mb-6"
            rows={3}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask the swarm anything..."
          />
          <button 
            onClick={handleQuery}
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 py-4 rounded-2xl font-bold text-xl hover:scale-[1.01] active:scale-[0.99] transition-all shadow-xl shadow-purple-500/20 disabled:opacity-50"
          >
            {loading ? "SYNTHESIZING PERSPECTIVE..." : `QUERY AS ${selectedP.toUpperCase()}`}
          </button>
        </div>

        {result && (
          <div className="result-container animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 glass p-10 rounded-3xl border border-white/10">
                <div className="flex items-center gap-3 mb-8">
                  <span className="text-4xl">{PERSPECTIVES.find(p => p.id === selectedP)?.icon}</span>
                  <div>
                    <h2 className="text-2xl font-bold uppercase tracking-widest">{selectedP} ANALYSIS</h2>
                    <div className="flex items-center gap-2 text-[10px] font-mono text-purple-400">
                      <span>ALIGNMENT INDEX:</span>
                      <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-purple-500" style={{ width: `${result.swarm_alignment * 100}%` }} />
                      </div>
                      <span>{(result.swarm_alignment * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
                
                <div className="prose prose-invert max-w-none">
                  <p className="text-xl leading-relaxed text-gray-200 italic font-serif">
                    "{result.synthesis}"
                  </p>
                </div>
              </div>

              <div className="lg:col-span-1 space-y-6">
                <div className="glass p-8 rounded-2xl border border-white/10">
                  <h3 className="text-xs font-mono text-purple-400 mb-6 tracking-tighter uppercase">Strategic Insights</h3>
                  <div className="space-y-4">
                    {result.strategic_insights.map((insight, i) => (
                      <div key={i} className="flex gap-3 text-sm">
                        <span className="text-purple-500">◆</span>
                        <span className="text-gray-300">{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="glass p-8 rounded-2xl border border-white/10 border-red-500/20 bg-red-500/[0.02]">
                  <h3 className="text-xs font-mono text-red-400 mb-6 tracking-tighter uppercase">Critical Risks</h3>
                  <div className="space-y-4">
                    {result.critical_risks.map((risk, i) => (
                      <div key={i} className="flex gap-3 text-sm">
                        <span className="text-red-500">⚠️</span>
                        <span className="text-gray-300">{risk}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); }
      `}</style>
    </div>
  );
}
