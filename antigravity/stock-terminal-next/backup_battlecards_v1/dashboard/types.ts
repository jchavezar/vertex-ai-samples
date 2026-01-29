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
