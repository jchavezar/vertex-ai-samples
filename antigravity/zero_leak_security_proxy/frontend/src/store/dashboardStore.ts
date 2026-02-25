import { create } from 'zustand';

export interface ProjectCardData {
  title: string;
  industry: string;
  factual_information: string;
  insights: string[];
  key_metrics: string[];
  document_name: string;
  document_url?: string;
  redacted_entities?: string[];
}

interface DashboardState {
  projectCards: ProjectCardData[];
  addProjectCard: (card: ProjectCardData) => void;
  clearCards: () => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  projectCards: [],
  addProjectCard: (card) => set((state) => {
    // Prevent exact duplicates, but allow appending new ones
    const exists = state.projectCards.some(c => c.title === card.title && c.factual_information === card.factual_information);
    if (exists) return state;
    return { projectCards: [card, ...state.projectCards] };
  }),
  clearCards: () => set({ projectCards: [] })
}));
