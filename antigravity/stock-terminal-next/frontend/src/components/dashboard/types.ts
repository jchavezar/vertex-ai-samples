export interface NewsItem {
  id: string;
  headline: string;
  source: string;
  summary: string;
  url: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  impact_score: number;
}

export interface HistoryPoint {
  date: string;
  close: number;
  [key: string]: string | number | undefined;
}

export interface TickerData {
  ticker: string;
  price: number;
  currency: string;
  time: string;
  history: HistoryPoint[];
  marketCap: number;
  peRatio: number;
  dividendYield: number;
  fiftyTwoWeekHigh: number;
  fiftyTwoWeekLow: number;
  sector: string;
  industry: string;
  change?: number;
  percentChange?: number;
}

export interface Peer {
  ticker: string;
  name: string;
  ceo_sentiment: string;
  identity: string;
  last_launch: string;
  video_url: string;
  momentum: string;
  price: number;
  change: number;
  marketCap: string;
  upside?: number;
  vol_risk?: number;
  summary?: string;
  confidence?: number;
  ceo_posture?: string;
  visual_brand_aura?: string;
  comparison_thesis?: string;
  alpha_thesis?: string;
  valuation_gap?: string;
  key_metrics?: string[];
}

export interface CompsIntel {
  peers: Peer[];
  summary?: string;
}

export interface TopologyNode {
  id: string;
  label: string;
  type?: string;
  model?: string;
  tools?: string[];
  duration?: number;
}

export interface TopologyEdge {
  source: string;
  target: string;
}

export interface ProcessorTopology {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

export interface NodeMetrics {
  ttft?: number;
  ttlt?: number;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  latencies?: number[];
  [key: string]: string | number | boolean | number[] | undefined;
}
export interface StreamEvent {
  type: 'chart' | 'stats' | 'trace' | 'topology' | 'tool_call' | 'tool_result' | 'error' | 'dashboard_command' | 'latency' | 'dashboard_context_update' | 'news_update' | 'insights_update';
  data?: unknown;
  tool?: string;
  args?: Record<string, unknown>;
  result?: unknown;
  duration?: number;
  message?: string;
  view?: string;
  payload?: unknown;
}

export interface TraceLogPayload {
  type?: 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'error' | 'system' | 'debug' | 'system_status';
  content?: string;
  tool?: string;
  args?: Record<string, unknown>;
  result?: unknown;
  duration?: number;
  metrics?: NodeMetrics;
}

export interface DashboardCommandPayload {
  ticker?: string;
}

export interface ChartDataPoint {
  date?: string;
  close?: number;
  value?: number;
  price?: number;
  sp500_close?: number;
  label?: string;
  time?: string;
  regionRevenue?: number;
  countryRevenue?: number;
  regionName?: string;
  countryName?: string;
  isNormalized?: boolean;
  originalPrice?: number;
  [key: string]: string | number | boolean | undefined | null;
}

export interface MultiSeriesData {
  series?: Array<{
    ticker: string;
    history: ChartDataPoint[];
  }>;
  chartType?: 'line' | 'bar' | 'pie';
  ticker?: string;
  data?: ChartDataPoint[];
  history?: ChartDataPoint[];
  title?: string;
}
