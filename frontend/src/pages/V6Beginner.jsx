import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import useStore from '../store/useStore'
import V6Stepper from '../components/V6Stepper'

const API_BASE = import.meta.env.VITE_API_URL || ''
const API_V6 = `${API_BASE}/api/v6`

export default function V6Beginner() {
  const navigate = useNavigate()
  const [projectName, setProjectName] = useState('')
  const [question, setQuestion] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const {
    setV6ProjectId,
    setV6DebateData,
    setV6QueryResults,
    setV6LastStep,
    setV6GraphPins,
    setV6GraphEvidence
  } = useStore()

  const buildEvidence = (ragData) => {
    const citations = ragData?.summary?.citations || []
    const nodeFallback = (ragData?.context?.top_nodes || []).map(node => node.label || node.id)
    const pins = Array.from(new Set([...(citations || []), ...nodeFallback].filter(Boolean)))

    const evidenceMap = {}
    const docs = ragData?.context?.documents || []
    const facts = ragData?.context?.facts || []
    const memories = ragData?.context?.memories || []
    const nodes = ragData?.context?.top_nodes || []
    const summary = ragData?.summary?.answer || ''

    pins.forEach((pin) => {
      const lowerPin = String(pin).toLowerCase()
      const lines = []
      docs.forEach((doc) => {
        const snippet = doc?.snippet || ''
        if (snippet.toLowerCase().includes(lowerPin)) {
          lines.push(`${doc.title}: ${snippet}`)
        }
      })
      facts.forEach((fact) => {
        if (String(fact).toLowerCase().includes(lowerPin)) {
          lines.push(String(fact))
        }
      })
      memories.forEach((mem) => {
        const label = mem?.label || mem?.id || ''
        if (String(label).toLowerCase().includes(lowerPin)) {
          lines.push(label)
        }
      })
      nodes.forEach((node) => {
        const label = node?.label || node?.id || ''
        if (String(label).toLowerCase().includes(lowerPin)) {
          lines.push(`Node: ${label}`)
        }
      })
      if (!lines.length && summary) {
        lines.push(summary.slice(0, 180))
      }
      evidenceMap[pin] = lines.slice(0, 3)
    })

    return { pins, evidenceMap }
  }

  const handleRun = async () => {
    setError('')
    if (!file) {
      setError('Please upload a file.')
      return
    }
    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('question', question)
      formData.append('project_name', projectName || 'New V6 Project')
      formData.append('perspective', 'businessman')

      const res = await axios.post(`${API_V6}/simple-run`, formData)
      const data = res.data || {}
      const perspective = data.perspective || 'businessman'

      setV6ProjectId(data.project_id)
      setV6DebateData(data.debate)
      setV6QueryResults({ [perspective]: data.query })
      setV6LastStep('query')

      const { pins, evidenceMap } = buildEvidence(data.rag || {})
      setV6GraphPins(pins)
      setV6GraphEvidence(evidenceMap)

      navigate(`/v6/query/${data.project_id}`, {
        state: {
          debateData: data.debate,
          simpleResult: data.query,
          simpleQuery: data.question,
          simplePerspective: perspective,
          ragData: data.rag
        }
      })
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    }
    setLoading(false)
  }

  return (
    <div className="v6-beginner-page p-8 min-h-screen bg-[#050505] text-white">
      <div className="max-w-4xl mx-auto">
        <V6Stepper activeStep="upload" projectId={null} />
        <header className="mb-10">
          <h1 className="text-4xl font-bold tracking-tighter mb-2 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            Beginner Start
          </h1>
          <p className="text-gray-400 font-mono text-sm">Upload one file and ask one question to get results.</p>
        </header>

        <div className="glass p-8 rounded-2xl border border-white/10">
          <div className="grid grid-cols-1 gap-6">
            <div>
              <label className="text-xs font-mono text-gray-400">PROJECT NAME (OPTIONAL)</label>
              <input
                type="text"
                className="mt-2 w-full bg-white/5 border border-white/10 p-4 rounded-xl focus:outline-none focus:border-blue-500"
                placeholder="My first run"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
              />
            </div>

            <div>
              <label className="text-xs font-mono text-gray-400">UPLOAD FILE</label>
              <label className="mt-2 border-2 border-dashed border-white/10 hover:border-blue-500/50 rounded-2xl p-10 flex flex-col items-center justify-center cursor-pointer transition-all bg-white/[0.02]">
                <input
                  type="file"
                  className="hidden"
                  onChange={(e) => setFile(e.target.files[0])}
                  disabled={loading}
                />
                <span className="text-4xl mb-3">📄</span>
                <span className="font-bold">{file ? file.name : 'DRAG AND DROP OR CLICK'}</span>
                <span className="text-xs text-gray-500 mt-2">PDF, TXT, or MD</span>
              </label>
            </div>

            <div>
              <label className="text-xs font-mono text-gray-400">YOUR QUESTION</label>
              <textarea
                className="mt-2 w-full bg-white/5 border border-white/10 p-4 rounded-xl focus:outline-none focus:border-blue-500"
                rows={3}
                placeholder="What should I do next?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />
            </div>

            {error && (
              <div className="text-sm text-red-400">{error}</div>
            )}

            <button
              onClick={handleRun}
              disabled={loading}
              className="w-full bg-gradient-to-r from-emerald-600 to-blue-600 p-4 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all shadow-xl shadow-blue-500/20 disabled:opacity-50"
            >
              {loading ? 'RUNNING...' : 'RUN ANALYSIS'}
            </button>

            <button
              type="button"
              className="text-xs font-mono text-gray-400 hover:text-gray-200"
              onClick={() => navigate('/v6/upload')}
            >
              Use advanced flow instead
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .glass {
          background: rgba(255, 255, 255, 0.03);
          backdrop-filter: blur(20px);
        }
      `}</style>
    </div>
  )
}
