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
      _hasHydrated: false,
      
      // Actions
      setProject: (project) => set({ project }),
      setLatestRun: (run) => set({ latestRun: run }),
      setActiveStage: (activeStage) => set({ activeStage }),
      setActiveNode: (activeNode) => set({ activeNode }),
      setUiMode: (uiMode) => set({ uiMode }),
      setIsSimulating: (isSimulating) => set({ isSimulating }),
      setHasHydrated: (state) => set({ _hasHydrated: state }),
      
      // Reset
      resetStore: () => set({ project: null, latestRun: null, activeStage: 'identity', activeNode: null, _hasHydrated: true }),
      
      resetMission: () => set({ latestRun: null, activeStage: 'identity', activeNode: null }),
      
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
      }),
    }
  )
)

export default useStore
