export type ActiveModule = 'voice' | 'creative' | 'swarm';

// Module A: Voice Assistant
export interface VoiceKpi {
  label: string;
  value: string;
  description: string;
  trend: 'up' | 'down' | 'neutral';
}

export interface StrategicPillar {
  title: string;
  detail: string;
  timeline: string;
}

export interface VoiceExecutiveResponse {
  transcript_query: string;
  spoken_voice_script: string;
  executive_summary: string;
  kpis: VoiceKpi[];
  pillars: StrategicPillar[];
  governance_note: string;
}

export interface VoiceScenario {
  id: string;
  title: string;
  query: string;
  category: string;
  badge: string;
}

// Module B: Creative Studio
export interface StoryboardPanel {
  panel_number: number;
  title: string;
  visual_description: string;
  voiceover_script: string;
  duration_seconds: number;
  on_screen_text: string;
  artwork_theme: string;
  visual_badge: string;
}

export interface ChannelCopy {
  channel: string;
  format_type: string;
  content: string;
  target_metric: string;
}

export interface FinancialProjection {
  roi_porcentaje: string;
  cac_impact: string;
  conversion_multiplier: string;
  recommended_budget: string;
  payback_period: string;
}

export interface ExecutiveCampaign {
  campaign_title: string;
  central_concept: string;
  executive_slogan: string;
  target_audience: string;
  tone_of_voice: string;
  storyboard: StoryboardPanel[];
  channels_copy: ChannelCopy[];
  financial_projection: FinancialProjection;
}

export interface CreativeTemplate {
  id: string;
  title: string;
  topic: string;
  industry: string;
  impact: string;
}

// Module C: Agent Swarm
export interface AgentConfig {
  id: string;
  name: string;
  role: string;
  avatar: string;
  color: 'indigo' | 'fuchsia' | 'emerald' | 'blue';
  system: string;
}

export interface AgentState {
  id: string;
  status: 'idle' | 'thinking' | 'working' | 'completed';
  tokens: string;
  output?: string;
  lastMessage?: string;
}

export interface ExecutiveDeliverable {
  title: string;
  mandate: string;
  strategy_summary: string;
  creative_vision: string;
  financial_roi_summary: string;
  audit_governance_summary: string;
  board_verdict: string;
  approved_budget: string;
  expected_payback: string;
  action_items: string[];
}

export interface SwarmMandate {
  id: string;
  title: string;
  mandate: string;
  complexity: string;
  lanes: number;
}
