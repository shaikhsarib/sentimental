import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useStore = create(
  persist(
    (set, get) => ({
      // State
      project: null,
      latestRun: null,
      activeStage: 'identity', // 'identity', 'intelligence', 'world', 'swarm', 'interaction'
      activeNode: null,
      uiMode: 'shield',
      isSimulating: false,
      sidebarOpen: true,
      workbenchMode: 'actions', // 'actions', 'inspector', 'report'
      selectedRunId: null,
      v6ProjectId: null,
      v6DebateData: null,
      v6QueryResults: {},
      v6LastStep: 'upload',
      v6GraphPins: [],
      v6GraphEvidence: {},
      _hasHydrated: false,
      
      // Actions
      setProject: (project) => set({ project }),
      setLatestRun: (run) => set({ latestRun: run, selectedRunId: run?.run_id }),
      setActiveStage: (activeStage) => set({ activeStage }),
      setActiveNode: (activeNode) => set({ activeNode, workbenchMode: activeNode ? 'inspector' : get().workbenchMode }),
      setUiMode: (uiMode) => set({ uiMode }),
      setIsSimulating: (isSimulating) => set({ isSimulating }),
      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      setWorkbenchMode: (workbenchMode) => set({ workbenchMode }),
      setSelectedRunId: (selectedRunId) => set({ selectedRunId, workbenchMode: selectedRunId ? 'report' : get().workbenchMode }),
      setV6ProjectId: (v6ProjectId) => set({ v6ProjectId }),
      setV6DebateData: (v6DebateData) => set({ v6DebateData }),
      setV6QueryResults: (v6QueryResults) => set({ v6QueryResults }),
      setV6LastStep: (v6LastStep) => set({ v6LastStep }),
      setV6GraphPins: (v6GraphPins) => set({ v6GraphPins }),
      setV6GraphEvidence: (v6GraphEvidence) => set({ v6GraphEvidence }),
      setHasHydrated: (state) => set({ _hasHydrated: state }),
      
      // Reset
      resetStore: () => set({ project: null, latestRun: null, activeStage: 'identity', activeNode: null, sidebarOpen: true, workbenchMode: 'actions', selectedRunId: null, v6ProjectId: null, v6DebateData: null, v6QueryResults: {}, v6LastStep: 'upload', v6GraphPins: [], v6GraphEvidence: {}, _hasHydrated: true }),
      
      resetMission: () => set({ latestRun: null, activeStage: 'identity', activeNode: null, selectedRunId: null, workbenchMode: 'actions' }),
      resetV6: () => set({ v6ProjectId: null, v6DebateData: null, v6QueryResults: {}, v6LastStep: 'upload', v6GraphPins: [], v6GraphEvidence: {} }),
      
      // Computed-like logic
      getActiveProjectId: () => get().project?.project_id || null,
    }),
    {
      name: 'sentimental-storage',
      onRehydrateStorage: () => (state) => {
        state.setHasHydrated(true)
      },
      partialize: (state) => ({ 
        project: state.project,
        latestRun: state.latestRun,
        activeStage: state.activeStage,
        uiMode: state.uiMode,
        sidebarOpen: state.sidebarOpen,
        workbenchMode: state.workbenchMode,
        selectedRunId: state.selectedRunId,
        v6ProjectId: state.v6ProjectId,
        v6DebateData: state.v6DebateData,
        v6QueryResults: state.v6QueryResults,
        v6LastStep: state.v6LastStep,
        v6GraphPins: state.v6GraphPins,
        v6GraphEvidence: state.v6GraphEvidence,
      }),
    }
  )
)

export default useStore
