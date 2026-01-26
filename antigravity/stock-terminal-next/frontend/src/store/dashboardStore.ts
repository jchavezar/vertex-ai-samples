import { create } from 'zustand';

export interface DataPoint {
  label: string;
  value: number;
  tooltip?: string;
  date?: string;
  close?: number;
}

export interface ChartWidgetData {
  type: 'chart';
  title: string;
  chart_type: 'line' | 'bar' | 'pie' | 'area';
  data: DataPoint[];
  ticker?: string;
  series?: any[];
  chartType?: string;
}

export interface StatsWidgetData {
  type: 'stats';
  title: string;
  items: { label: string; value: string; trend?: 'up' | 'down' | 'neutral' }[];
}

export type WidgetData = ChartWidgetData | StatsWidgetData;

export interface WidgetOverride {
  loading: boolean;
  content: string | null;
  model?: string;
}

interface DashboardState {
  ticker: string;
  setTicker: (ticker: string) => void;

  tickerData: any | null;
  setTickerData: (data: any | null) => void;

  activeView: string;
  setActiveView: (view: string) => void;

  chartOverride: any | null;
  setChartOverride: (override: any | null) => void;

  widgetOverrides: Record<string, WidgetOverride>;
  setWidgetOverride: (section: string, override: WidgetOverride) => void;

  activeWidget: WidgetData | null;
  setActiveWidget: (widget: WidgetData | null) => void;

  isSidebarOpen: boolean;
  toggleSidebar: () => void;

  theme: 'light' | 'dark';
  toggleTheme: () => void;

  // Chat Docking State
  chatDockPosition: 'floating' | 'left' | 'right';
  setChatDockPosition: (position: 'floating' | 'left' | 'right') => void;
  chatPosition: { x: number; y: number };
  setChatPosition: (pos: { x: number; y: number }) => void;
  isChatOpen: boolean;
  setChatOpen: (isOpen: boolean) => void;
  isChatMaximized: boolean;
  toggleChatMaximized: () => void;
  chatSidebarWidth: number;
  setChatSidebarWidth: (width: number) => void;
  isGraphOverlayOpen: boolean;
  setGraphOverlayOpen: (isOpen: boolean) => void;

  currentView: 'dashboard' | 'advanced_search';
  setCurrentView: (view: 'dashboard' | 'advanced_search') => void;

  // Shared Chat State
  topology: any | null; // Using any for now to avoid circular dependency with AgentGraph types
  setTopology: (topology: any | null) => void;

  nodeDurations: Record<string, number>;
  setNodeDurations: (durations: Record<string, number>) => void;

  nodeMetrics: Record<string, Record<string, any>>;
  setNodeMetrics: (metrics: Record<string, Record<string, any>>) => void;

  executionPath: string[];
  setExecutionPath: (path: string[]) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  ticker: 'FDS',
  setTicker: (ticker) => set({ ticker }),

  tickerData: null,
  setTickerData: (data) => set({ tickerData: data }),

  activeView: 'Snapshot',
  setActiveView: (view) => set({ activeView: view }),

  chartOverride: null,
  setChartOverride: (override) => set({ chartOverride: override }),

  widgetOverrides: {},
  setWidgetOverride: (section, override) => set((state) => ({
    widgetOverrides: { ...state.widgetOverrides, [section]: override }
  })),

  activeWidget: null,
  setActiveWidget: (widget) => set({ activeWidget: widget }),

  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  theme: 'light',
  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    if (newTheme === 'dark') {
      document.body.classList.add('dark');
      document.body.classList.add('dark-theme'); // for compatibility
    } else {
      document.body.classList.remove('dark');
      document.body.classList.remove('dark-theme');
    }
    return { theme: newTheme };
  }),

  chatDockPosition: 'right',
  setChatDockPosition: (position) => set({ chatDockPosition: position }),
  chatPosition: { x: 0, y: 0 },
  setChatPosition: (pos) => set({ chatPosition: pos }),
  isChatOpen: true,
  setChatOpen: (isOpen) => set({ isChatOpen: isOpen }),
  isChatMaximized: false,
  toggleChatMaximized: () => set((state) => ({ isChatMaximized: !state.isChatMaximized })),
  chatSidebarWidth: 450,
  setChatSidebarWidth: (width) => set({ chatSidebarWidth: width }),
  isGraphOverlayOpen: false,
  setGraphOverlayOpen: (isOpen) => set({ isGraphOverlayOpen: isOpen }),

  currentView: 'dashboard',
  setCurrentView: (view: 'dashboard' | 'advanced_search') => set({ currentView: view }),

  topology: null,
  setTopology: (topology) => set({ topology }),

  activeNodeId: null, // Add activeNodeId for shared state if needed, though mostly derived

  nodeDurations: {},
  setNodeDurations: (durations) => set({ nodeDurations: durations }),

  nodeMetrics: {},
  setNodeMetrics: (metrics) => set({ nodeMetrics: metrics }),

  executionPath: [],
  setExecutionPath: (path) => set({ executionPath: path }),
}));
