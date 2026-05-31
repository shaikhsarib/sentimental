import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import useStore from '../store/useStore'

export default function V6Stepper({ activeStep, projectId }) {
  const navigate = useNavigate()
  const { v6LastStep, setV6LastStep } = useStore()

  const steps = useMemo(() => ([
    { key: 'upload', label: 'Upload', hint: 'Add a document', path: '/v6/upload' },
    { key: 'workbench', label: 'Swarm', hint: 'Taxonomy & workspace', path: projectId ? `/v6/workbench/${projectId}` : null },
    { key: 'debate', label: 'Run', hint: 'Generate analysis', path: projectId ? `/v6/debate/${projectId}` : null },
    { key: 'query', label: 'Results', hint: 'Ask and review', path: projectId ? `/v6/query/${projectId}` : null }
  ]), [projectId])

  const normalizeStep = (stepKey) => (stepKey === 'report' ? 'query' : stepKey)
  const activeKey = normalizeStep(activeStep)
  const resumeKey = normalizeStep(v6LastStep)
  const activeIndex = Math.max(0, steps.findIndex(step => step.key === activeKey))
  const resumeLabel = steps.find(step => step.key === resumeKey)?.label || 'Upload'

  const goToStep = (step) => {
    if (!step.path) return
    setV6LastStep(step.key)
    navigate(step.path)
  }

  return (
    <div className="v6-stepper">
      <div className="v6-stepper-track" />
      {steps.map((step, index) => {
        const state = index < activeIndex ? 'done' : index === activeIndex ? 'active' : 'todo'
        const isDisabled = !step.path

        return (
          <button
            key={step.key}
            type="button"
            className={`v6-step ${state}`}
            onClick={() => goToStep(step)}
            disabled={isDisabled}
          >
            <span className="v6-step-index">{String(index + 1).padStart(2, '0')}</span>
            <span className="v6-step-label">{step.label}</span>
            <span className="v6-step-hint">{step.hint}</span>
          </button>
        )
      })}
      <div className="v6-stepper-progress">Step {activeIndex + 1} of {steps.length}</div>
      <div className="v6-stepper-note">Resume: {resumeLabel}</div>
    </div>
  )
}
