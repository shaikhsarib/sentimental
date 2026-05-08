import { useNavigate } from 'react-router-dom'
import { Activity, Shield, Terminal } from 'lucide-react'
import useStore from '../store/useStore'

export default function FlowHub() {
  const navigate = useNavigate()
  const { project, v6ProjectId, resetV6 } = useStore()

  return (
    <div className="flow-hub">
      <div className="flow-hub-shell">
        <header className="flow-hub-header">
          <div className="flow-hub-title">SENTIFLOW COMMAND HUB</div>
          <p className="flow-hub-subtitle">Start with the guided flow. Upload, run, and review.</p>
        </header>

        <div className="flow-hub-cta">
          <button
            type="button"
            className="flow-start"
            onClick={() => navigate(v6ProjectId ? `/v6/debate/${v6ProjectId}` : '/v6/start')}
          >
            Start Beginner Flow
          </button>
          <div className="flow-start-sub">Step 1 Upload &rarr; Step 2 Run &rarr; Step 3 Results</div>
        </div>

        <div className="flow-hub-grid">
          <button
            type="button"
            className="flow-card primary"
            onClick={() => navigate(v6ProjectId ? `/v6/debate/${v6ProjectId}` : '/v6/start')}
          >
            <div className="flow-card-icon">
              <Activity size={20} />
            </div>
            <div className="flow-card-body">
              <h3>V6 Guided Flow</h3>
              <p>Upload a file, run the analysis, and view results.</p>
              <span className="flow-card-cta">Open guided flow</span>
            </div>
          </button>

          <button
            type="button"
            className="flow-card secondary"
            onClick={() => navigate('/v5')}
          >
            <div className="flow-card-icon">
              <Shield size={20} />
            </div>
            <div className="flow-card-body">
              <h3>V5 Tactical Workspace</h3>
              <p>Live graph operations, manual controls, and run history.</p>
              <span className="flow-card-cta">Open V5</span>
            </div>
          </button>
        </div>

        {v6ProjectId && (
          <div className="flow-hub-footer">
            <button type="button" className="flow-reset" onClick={resetV6}>
              RESET V6 SESSION
            </button>
          </div>
        )}

        {project && (
          <div className="flow-hub-footer">
            <div className="flow-hub-status">
              <Terminal size={14} /> V5 project detected
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
