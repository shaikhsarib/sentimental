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
      setHasHydrated: (state) => set({ _hasHydrated: state }),
      
      // Reset
      resetStore: () => set({ project: null, latestRun: null, activeStage: 'identity', activeNode: null, sidebarOpen: true, workbenchMode: 'actions', selectedRunId: null, _hasHydrated: true }),
      
      resetMission: () => set({ latestRun: null, activeStage: 'identity', activeNode: null, selectedRunId: null, workbenchMode: 'actions' }),
      
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
      }),
    }
  )
)

export default useStore
