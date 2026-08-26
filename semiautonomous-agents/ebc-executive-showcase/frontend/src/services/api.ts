import {
  VoiceScenario,
  VoiceExecutiveResponse,
  CreativeTemplate,
  ExecutiveCampaign,
  AgentConfig,
  SwarmMandate,
  ExecutiveDeliverable
} from '../types';

const API_BASE = '/api';

export async function fetchVoiceScenarios(): Promise<VoiceScenario[]> {
  try {
    const res = await fetch(`${API_BASE}/voice/scenarios`);
    if (!res.ok) throw new Error('Failed to fetch voice scenarios');
    const data = await res.json();
    return data.scenarios;
  } catch (error) {
    console.error('Error fetching voice scenarios:', error);
    return [];
  }
}

export async function queryVoiceAssistant(query: string): Promise<VoiceExecutiveResponse> {
  const res = await fetch(`${API_BASE}/voice/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error en consulta de voz' }));
    throw new Error(err.detail || 'Error en consulta de voz');
  }
  return res.json();
}

export async function fetchCreativeTemplates(): Promise<CreativeTemplate[]> {
  try {
    const res = await fetch(`${API_BASE}/creative/templates`);
    if (!res.ok) throw new Error('Failed to fetch creative templates');
    const data = await res.json();
    return data.templates;
  } catch (error) {
    console.error('Error fetching creative templates:', error);
    return [];
  }
}

export async function generateCampaign(topic: string): Promise<ExecutiveCampaign> {
  const res = await fetch(`${API_BASE}/creative/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error al generar campaña' }));
    throw new Error(err.detail || 'Error al generar campaña');
  }
  return res.json();
}

export async function fetchSwarmAgents(): Promise<AgentConfig[]> {
  try {
    const res = await fetch(`${API_BASE}/swarm/agents`);
    if (!res.ok) throw new Error('Failed to fetch swarm agents');
    const data = await res.json();
    return data.agents;
  } catch (error) {
    console.error('Error fetching swarm agents:', error);
    return [];
  }
}

export async function fetchSwarmMandates(): Promise<SwarmMandate[]> {
  try {
    const res = await fetch(`${API_BASE}/swarm/mandates`);
    if (!res.ok) throw new Error('Failed to fetch swarm mandates');
    const data = await res.json();
    return data.mandates;
  } catch (error) {
    console.error('Error fetching swarm mandates:', error);
    return [];
  }
}

export interface SwarmStreamCallbacks {
  onStart?: (mandate: string, agents: AgentConfig[]) => void;
  onAgentStatus?: (agentId: string, status: string, message: string) => void;
  onAgentToken?: (agentId: string, token: string) => void;
  onAgentCompleted?: (agentId: string, output: string) => void;
  onSynthesisStart?: (message: string) => void;
  onSynthesisCompleted?: (deliverable: ExecutiveDeliverable) => void;
  onDone?: () => void;
  onError?: (err: Error) => void;
}

export async function streamSwarmExecution(
  mandate: string,
  callbacks: SwarmStreamCallbacks
): Promise<() => void> {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/swarm/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mandate }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error('Error al conectar con el flujo de enjambre');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const jsonStr = trimmed.replace('data: ', '');
            try {
              const data = JSON.parse(jsonStr);
              if (data.event === 'start') {
                callbacks.onStart?.(data.mandate, data.agents);
              } else if (data.event === 'agent_status') {
                callbacks.onAgentStatus?.(data.agent_id, data.status, data.message);
              } else if (data.event === 'agent_token') {
                callbacks.onAgentToken?.(data.agent_id, data.token);
              } else if (data.event === 'agent_completed') {
                callbacks.onAgentCompleted?.(data.agent_id, data.output);
              } else if (data.event === 'synthesis_start') {
                callbacks.onSynthesisStart?.(data.message);
              } else if (data.event === 'synthesis_completed') {
                callbacks.onSynthesisCompleted?.(data.deliverable);
              } else if (data.event === 'done') {
                callbacks.onDone?.();
              }
            } catch (err) {
              console.error('Error parsing SSE event:', err, jsonStr);
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        callbacks.onError?.(err);
      }
    }
  })();

  return () => controller.abort();
}
