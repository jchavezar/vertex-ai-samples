import {
  AgentQueryResponse,
  BoardMemoResponse,
  LegacyQueryResponse,
  RefactorEvent,
  ShockImpactData,
  ShockParameters,
} from '../types';

const API_BASE = '/api';

export async function fetchLegacyData(params: {
  page: number;
  page_size: number;
  search?: string;
  currency?: string;
  risk_rating?: string;
  margin_tier?: string;
  clearing_house?: string;
  sla_status?: string;
  simulate_slow_query_ms?: number;
}): Promise<LegacyQueryResponse> {
  const res = await fetch(`${API_BASE}/legacy/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Legacy Query failed: ${res.statusText}`);
  return res.json();
}

export async function exportLegacyCsv(): Promise<any> {
  const res = await fetch(`${API_BASE}/legacy/export-csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error(`Export request failed: ${res.statusText}`);
  return res.json();
}

export async function calculateShock(params: ShockParameters): Promise<ShockImpactData> {
  const res = await fetch(`${API_BASE}/shock/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Shock calculation failed: ${res.statusText}`);
  return res.json();
}

export async function queryAgent(
  query: string,
  shock_params?: ShockParameters
): Promise<AgentQueryResponse> {
  const res = await fetch(`${API_BASE}/agent/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, shock_params, use_grounding: true }),
  });
  if (!res.ok) throw new Error(`Agent query failed: ${res.statusText}`);
  return res.json();
}

export async function generateBoardMemo(
  query_context: string,
  shock_params: ShockParameters,
  memo_title?: string
): Promise<BoardMemoResponse> {
  const res = await fetch(`${API_BASE}/agent/board-memo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query_context, shock_params, memo_title }),
  });
  if (!res.ok) throw new Error(`Board memo generation failed: ${res.statusText}`);
  return res.json();
}

export function subscribeToRefactorStream(onEvent: (event: RefactorEvent) => void): () => void {
  const eventSource = new EventSource(`${API_BASE}/refactor/stream`);

  eventSource.onmessage = (e) => {
    try {
      const data: RefactorEvent = JSON.parse(e.data);
      onEvent(data);
      if (data.event === 'pipeline_finished') {
        eventSource.close();
      }
    } catch (err) {
      console.error('Failed to parse SSE refactor event:', err);
    }
  };

  eventSource.onerror = (err) => {
    console.error('SSE connection error:', err);
    eventSource.close();
  };

  return () => {
    eventSource.close();
  };
}
