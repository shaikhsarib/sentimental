import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = "http://localhost:8000/api/v6";

export default function V6Upload() {
  const [file, setFile] = useState(null);
  const [projectName, setProjectName] = useState("");
  const [projectId, setProjectId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extraction, setExtraction] = useState(null);
  const navigate = useNavigate();

  const handleCreateProject = async () => {
    if (!projectName) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/projects`, { name: projectName });
      setProjectId(res.data.project_id);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleUpload = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile || !projectId) return;
    
    setLoading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);
    
    try {
      const res = await axios.post(`${API_BASE}/upload?project_id=${projectId}`, formData);
      setExtraction(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="v6-upload-page p-8 min-h-screen bg-[#050505] text-white">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold tracking-tighter mb-2 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            INSTITUTIONAL INTELLIGENCE UPLOAD
          </h1>
          <p className="text-gray-400 font-mono text-sm">SENTIFLOW V6 // ENTITY EXTRACTION GATEWAY</p>
        </header>

        {!projectId ? (
          <div className="project-creation glass p-8 rounded-2xl border border-white/10">
            <h2 className="text-xl font-bold mb-6">Initialize Strategic Project</h2>
            <div className="flex gap-4">
              <input 
                type="text" 
                placeholder="Project Name (e.g. Q3 Market Volatility Analysis)"
                className="flex-1 bg-white/5 border border-white/10 p-4 rounded-xl focus:outline-none focus:border-blue-500 transition-all"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
              />
              <button 
                onClick={handleCreateProject}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-500 px-8 rounded-xl font-bold transition-all disabled:opacity-50"
              >
                {loading ? "INITIALIZING..." : "CREATE PROJECT"}
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Zone */}
            <div className="upload-zone glass p-8 rounded-2xl border border-white/10 h-fit">
              <h2 className="text-xl font-bold mb-4">Strategic Document</h2>
              <p className="text-gray-400 mb-8 text-sm">Upload PDF, TXT, or MD. Our V6 engine will extract the entity DNA for swarm generation.</p>
              
              <label className="border-2 border-dashed border-white/10 hover:border-blue-500/50 rounded-2xl p-12 flex flex-col items-center justify-center cursor-pointer transition-all bg-white/[0.02]">
                <input type="file" className="hidden" onChange={handleUpload} disabled={loading} />
                <span className="text-4xl mb-4">📄</span>
                <span className="font-bold">{loading ? "PROCESSING..." : "DRAG & DROP OR CLICK"}</span>
                <span className="text-xs text-gray-500 mt-2">MAX 50MB // AUTOMATIC NER PIPELINE</span>
              </label>
            </div>

            {/* Extraction Preview */}
            <div className="extraction-preview glass p-8 rounded-2xl border border-white/10 min-h-[500px]">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold">Entity DNA Preview</h2>
                {extraction && (
                  <span className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-xs font-bold border border-emerald-500/30">
                    {extraction.domain.domain}
                  </span>
                )}
              </div>

              {!extraction ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-600 font-mono text-sm py-20">
                  <p>WAITING FOR DOCUMENT DATA...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="sentiment-bar mb-8 p-4 bg-white/5 rounded-xl border border-white/5">
                    <div className="flex justify-between text-xs font-mono mb-2">
                      <span>SENTIMENT SCORE</span>
                      <span>{(extraction.domain.score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500" 
                        style={{ width: `${(extraction.domain.score + 1) * 50}%` }}
                      />
                    </div>
                  </div>

                  <div className="entity-list grid grid-cols-2 gap-3">
                    {extraction.entities.map((entity, i) => (
                      <div key={i} className="entity-card p-3 bg-white/5 rounded-lg border border-white/5 hover:border-white/20 transition-all">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded text-gray-400 font-mono">
                            {entity.type}
                          </span>
                        </div>
                        <p className="text-sm font-bold truncate">{entity.name}</p>
                      </div>
                    ))}
                  </div>

                  <button 
                    onClick={() => navigate(`/v6/debate/${projectId}`)}
                    className="w-full mt-8 bg-gradient-to-r from-emerald-600 to-blue-600 p-4 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all shadow-xl shadow-blue-500/20"
                  >
                    GENERATE MILLION-AGENT SWARM
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .glass {
          background: rgba(255, 255, 255, 0.03);
          backdrop-filter: blur(20px);
        }
      `}</style>
    </div>
  );
}
