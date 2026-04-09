export interface Lesson {
  id: number;
  title: string;
  description: string;
  hasDemo: boolean;
  demoComponent: string | null;
  content?: string;
}

export interface AgentCard {
  name: string;
  description: string;
  url: string;
  version?: string;
  skills: AgentSkill[];
  capabilities?: Record<string, boolean>;
  defaultInputModes?: string[];
  defaultOutputModes?: string[];
}

export interface AgentSkill {
  id: string;
  name: string;
  description: string;
  tags?: string[];
  examples?: string[];
}

export interface AgentInfo {
  port: number;
  name: string;
  healthy: boolean;
  card?: AgentCard;
}

export interface TaskEvent {
  type: string;
  timestamp: number;
  data: Record<string, unknown>;
}
