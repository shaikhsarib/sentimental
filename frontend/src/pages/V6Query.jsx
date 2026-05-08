import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { FileText, Download, Share2 } from 'lucide-react';
import axios from 'axios';
import useStore from '../store/useStore'
import V6Stepper from '../components/V6Stepper'

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
  const [report, setReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [ragQuery, setRagQuery] = useState('');
  const [ragData, setRagData] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [showPerspectives, setShowPerspectives] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);
  const { v6DebateData, setV6QueryResults, setV6LastStep, setV6GraphPins, setV6GraphEvidence } = useStore();
  const API_BASE = import.meta.env.VITE_API_URL || '';
  const API_V6 = `${API_BASE}/api/v6`;

  useEffect(() => {
    if (!debateData && v6DebateData) {
      setDebateData(v6DebateData);
    }
  }, [debateData, v6DebateData]);

  useEffect(() => {
    if (!location.state?.simpleResult || result) return;
    const initialPerspective = location.state?.simplePerspective || selectedP;
    const initialQuery = location.state?.simpleQuery || query;

    setSelectedP(initialPerspective);
    setQuery(initialQuery);
    setResult(location.state.simpleResult);
    setQueryResults(prev => {
      const next = { ...prev, [initialPerspective]: location.state.simpleResult };
      setV6QueryResults(next);
      return next;
    });
    setV6LastStep('query');

    if (location.state?.ragData) {
      setRagData(location.state.ragData);
      if (!ragQuery) {
        setRagQuery(initialQuery);
      }
    }
  }, [location.state, result, selectedP, query, ragQuery, setV6QueryResults, setV6LastStep]);

  useEffect(() => {
    if (!ragQuery) {
      setRagQuery(query);
    }
  }, [query, ragQuery]);

  const handleRag = async (overrideQuery) => {
    const activeQuery = overrideQuery || ragQuery || query;
    if (!activeQuery) return;
    setRagLoading(true);
    try {
      const res = await axios.get(`${API_V6}/projects/${projectId}/rag`, {
        params: { query: activeQuery }
      });
      setRagData(res.data);
      const citations = res.data?.summary?.citations || [];
      const nodeFallback = (res.data?.context?.top_nodes || []).map(node => node.label || node.id);
      const pins = Array.from(new Set([...(citations || []), ...nodeFallback].filter(Boolean)));
      setV6GraphPins(pins);
      const evidenceMap = {};
      const docs = res.data?.context?.documents || [];
      const facts = res.data?.context?.facts || [];
      const memories = res.data?.context?.memories || [];
      const nodes = res.data?.context?.top_nodes || [];
      const summary = res.data?.summary?.answer || '';
      pins.forEach((pin) => {
        const lowerPin = String(pin).toLowerCase();
        const lines = [];
        docs.forEach((doc) => {
          const snippet = doc?.snippet || '';
          if (snippet.toLowerCase().includes(lowerPin)) {
            lines.push(`${doc.title}: ${snippet}`);
          }
        });
        facts.forEach((fact) => {
          if (String(fact).toLowerCase().includes(lowerPin)) {
            lines.push(String(fact));
          }
        });
        memories.forEach((mem) => {
          const label = mem?.label || mem?.id || '';
          if (String(label).toLowerCase().includes(lowerPin)) {
            lines.push(label);
          }
        });
        nodes.forEach((node) => {
          const label = node?.label || node?.id || '';
          if (String(label).toLowerCase().includes(lowerPin)) {
            lines.push(`Node: ${label}`);
          }
        });
        if (!lines.length && summary) {
          lines.push(summary.slice(0, 180));
        }
        evidenceMap[pin] = lines.slice(0, 3);
      });
      setV6GraphEvidence(evidenceMap);
    } catch (err) {
      console.error(err);
    }
    setRagLoading(false);
  };

  const handleQuery = async () => {
    setLoading(true);
    try {
      handleRag(query);
      const res = await axios.post(`${API_V6}/projects/${projectId}/query`, {
        query,
        perspective: selectedP,
        debate_data: debateData
      });
      setResult(res.data);
      setQueryResults(prev => {
        const next = { ...prev, [selectedP]: res.data };
        setV6QueryResults(next);
        return next;
      });
      setV6LastStep('query');
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await axios.post(`${API_V6}/projects/${projectId}/export`, {
        debate_data: debateData,
        queries: queryResults
      });
      window.open(`${API_BASE}${res.data.download_url}`, '_blank');
    } catch (err) {
      console.error(err);
    }
    setExporting(false);
  };

  const handleReport = async () => {
    setReportLoading(true);
    try {
      const res = await axios.post(`${API_V6}/projects/${projectId}/report`, {
        debate_data: debateData,
        queries: queryResults
      });
      setReport(res.data || null);
      setV6LastStep('report');
    } catch (err) {
      console.error(err);
    }
    setReportLoading(false);
  };

  return (
    <div className="v6-query-page p-8 min-h-screen bg-[#050505] text-white">
      <div className="max-w-6xl mx-auto">
        <V6Stepper activeStep="query" projectId={projectId} />
        <header className="mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tighter mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Step 3: Results
            </h1>
            <p className="text-gray-400 font-mono text-sm">Ask one question to get an answer.</p>
          </div>
          {debateData?.consensus?.should_refuse && (
            <div className="px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-xl text-xs font-mono text-red-400 animate-pulse">
              ⚠️ RELIABILITY WARNING: CONSENSUS REFUSED
            </div>
          )}
          <div className="flex gap-3">
            <button 
              onClick={handleReport}
              disabled={reportLoading}
              className="flex items-center gap-2 px-6 py-2 bg-white/5 border border-white/10 rounded-full text-xs font-mono hover:bg-white/10 transition-all disabled:opacity-50"
            >
              <FileText size={14} className="text-purple-400" />
              {reportLoading ? "DRAFTING REPORT..." : "GENERATE REPORT"}
            </button>
            <button 
              onClick={handleExport}
              disabled={exporting}
              className="flex items-center gap-2 px-6 py-2 bg-white/5 border border-white/10 rounded-full text-xs font-mono hover:bg-white/10 transition-all disabled:opacity-50"
            >
              <FileText size={14} className="text-purple-400" />
              {exporting ? "GENERATING PDF..." : "EXPORT BRIEF"}
            </button>
          </div>
        </header>

        <div className="glass p-6 rounded-2xl border border-white/10 mb-6 flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-gray-200">
            Perspective: <span className="font-bold">{PERSPECTIVES.find(p => p.id === selectedP)?.name}</span>
          </div>
          <button
            type="button"
            className="text-xs font-mono text-gray-400 hover:text-gray-200"
            onClick={() => setShowPerspectives(prev => !prev)}
          >
            {showPerspectives ? 'Hide perspectives' : 'Change perspective (optional)'}
          </button>
        </div>

        {showPerspectives && (
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
        )}

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
            {loading ? "RUNNING..." : "GET ANSWER"}
          </button>
        </div>

        {!result && (
          <div className="glass p-6 rounded-3xl border border-white/10 mb-12 text-center">
            <p className="text-gray-300">No results yet. Ask a question and click Get Answer.</p>
          </div>
        )}

        <div className="glass p-6 rounded-3xl border border-white/10 mb-12">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-mono text-purple-400 uppercase">Evidence (optional)</h3>
            <button
              type="button"
              className="text-[10px] font-mono text-gray-400 hover:text-gray-200"
              onClick={() => setShowEvidence(prev => !prev)}
            >
              {showEvidence ? 'Hide evidence' : 'Show evidence'}
            </button>
          </div>
          {showEvidence && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <button
                  className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono"
                  onClick={() => handleRag()}
                  disabled={ragLoading}
                >
                  {ragLoading ? 'SCANNING...' : 'FETCH EVIDENCE'}
                </button>
              </div>
              <input
                className="w-full bg-white/5 border border-white/10 p-3 rounded-xl text-sm mb-4"
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                placeholder="Evidence query (entities, risks, relationships)"
              />
              {ragData?.summary && (
                <div className="p-4 bg-white/5 rounded-xl border border-white/10 mb-4">
                  <div className="text-[10px] font-mono text-gray-400 mb-2">SYNTHESIS</div>
                  <p className="text-sm text-gray-200">{ragData.summary.answer}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(ragData.summary.citations || []).slice(0, 4).map((c, i) => (
                      <span key={i} className="text-[10px] font-mono bg-white/10 px-2 py-1 rounded-full">{c}</span>
                    ))}
                  </div>
                </div>
              )}
              {ragData?.context && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                  <div className="p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="text-[10px] text-gray-400 mb-2 font-mono">TOP NODES</div>
                    <div className="space-y-2">
                      {ragData.context.top_nodes?.slice(0, 4).map((node) => (
                        <div key={node.id} className="truncate">{node.label || node.id}</div>
                      ))}
                    </div>
                  </div>
                  <div className="p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="text-[10px] text-gray-400 mb-2 font-mono">MEMORIES</div>
                    <div className="space-y-2">
                      {ragData.context.memories?.slice(0, 4).map((mem) => (
                        <div key={mem.id} className="truncate">{mem.label || mem.id}</div>
                      ))}
                    </div>
                  </div>
                  <div className="p-3 bg-white/5 rounded-lg border border-white/5">
                    <div className="text-[10px] text-gray-400 mb-2 font-mono">DOCUMENTS</div>
                    <div className="space-y-2">
                      {ragData.context.documents?.slice(0, 3).map((doc, i) => (
                        <div key={i} className="truncate">{doc.title}</div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
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

        {report && (
          <div id="report" className="glass p-8 rounded-3xl border border-white/10 mt-12">
            <h3 className="text-sm font-mono text-purple-400 mb-6 tracking-tighter uppercase">Strategic Report Draft</h3>
            <div className="space-y-6">
              {report.addendum && (
                <div className="p-8 bg-blue-500/5 border border-blue-500/20 rounded-2xl text-sm">
                  <div className="text-[10px] font-mono text-blue-400 mb-6 uppercase tracking-widest">INDUSTRIAL INTELLIGENCE ADDENDUM</div>
                  
                  <div className="mb-8">
                    <div className="text-[10px] font-mono text-gray-500 mb-2">EXECUTIVE SUMMARY</div>
                    <p className="text-gray-200 leading-relaxed italic">"{report.addendum.executive_summary}"</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div>
                      <div className="text-[10px] font-mono text-gray-500 mb-4">TACTICAL PLAYBOOK</div>
                      <div className="space-y-3">
                        {(report.addendum.tactical_playbook || []).map((item, i) => (
                          <div key={i} className="p-3 bg-white/5 rounded-xl border border-white/5">
                            <div className="flex justify-between items-center mb-1">
                               <span className="text-[10px] font-mono text-blue-400">{item.phase}</span>
                               <span className="text-[10px] text-gray-500">OUTCOME: {item.outcome}</span>
                            </div>
                            <p className="text-xs font-bold text-gray-200">{item.action}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-gray-500 mb-4">RISK SIGNALS</div>
                      <div className="space-y-3">
                        {(report.addendum.risk_signals || []).map((item, i) => (
                          <div key={i} className="flex justify-between items-center p-3 bg-white/5 rounded-xl border border-white/5">
                            <div className="flex-1">
                              <div className="text-xs font-bold text-gray-200">{item.signal}</div>
                              <div className="text-[10px] text-gray-500">{item.description}</div>
                            </div>
                            <div className="text-right ml-4">
                              <div className="text-[10px] font-mono text-blue-400">{item.strength}%</div>
                              <div className="w-12 h-1 bg-white/10 rounded-full overflow-hidden mt-1">
                                <div className="h-full bg-blue-500" style={{ width: `${item.strength}%` }} />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mb-8">
                    <div className="text-[10px] font-mono text-gray-500 mb-4">NARRATIVE TRAJECTORY (72H FORECAST)</div>
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5 border-l-4 border-l-blue-500">
                      <p className="text-sm text-gray-200 font-serif leading-relaxed">{report.addendum.narrative_trajectory}</p>
                    </div>
                  </div>

                  <div>
                    <div className="text-[10px] font-mono text-gray-500 mb-4">KEY ENTITY IMPACT</div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-white/10">
                            <th className="py-2 font-mono text-gray-500">ENTITY</th>
                            <th className="py-2 font-mono text-gray-500">ROLE</th>
                            <th className="py-2 font-mono text-gray-500">RISK_CONTRIBUTION</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(report.addendum.key_entities || []).map((entity, i) => (
                            <tr key={i} className="border-b border-white/5">
                              <td className="py-3 font-bold text-blue-300">{entity.entity}</td>
                              <td className="py-3 text-gray-400">{entity.role}</td>
                              <td className="py-3 text-gray-300">{entity.risk_contribution}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style>{`
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); }
      `}</style>
    </div>
  );
}
