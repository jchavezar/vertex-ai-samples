/* Event vocabulary streamed by /api/credit/chat — every WebSocket message is
 * one of these. The same shape feeds both the chat UI (text deltas) and the
 * architecture pipeline (tool_call_start / tool_call_end animations). */

export type CreditTool = 'vertex_search' | 'code_execution' | 'google_search';

/** High-level lifecycle phases the agent walks through.
 *  discovery  → grounding from CCLA corpus / web
 *  reasoning  → model deciding what to do (extract rate, plan calc)
 *  compute    → BuiltInCodeExecutor running Python
 *  synthesize → streaming the final answer + chart_data */
export type AgentPhase = 'discovery' | 'reasoning' | 'compute' | 'synthesize';

export type CreditEvent =
  | { type: 'text_delta'; text: string }
  | { type: 'turn_complete' }
  | {
      type: 'tool_call_start';
      tool: CreditTool;
      callId: string;
      input?: string;
    }
  | {
      type: 'tool_call_end';
      tool: CreditTool;
      callId: string;
      summary?: string;
    }
  /** Phase boundary — emitted once when the agent transitions phases. */
  | { type: 'agent_phase'; phase: AgentPhase; tMs: number }
  /** Granular trace event — one per significant step inside a phase.
   *  `kind` identifies the kind of step (search_start, ttft, code_emit, …). */
  | {
      type: 'agent_stamp';
      phase: AgentPhase;
      kind: string;
      label: string;
      tMs: number;
      dtMs: number;
    }
  | {
      type: 'code';
      callId: string;
      language: 'PYTHON' | string;
      source: string;
    }
  | {
      type: 'code_result';
      callId: string;
      output: string;
      outcome: 'OUTCOME_OK' | 'OUTCOME_FAILED' | string;
    }
  | {
      type: 'grounding_chunk';
      kind: 'web' | 'corpus';
      uri: string;
      title: string;
      snippet?: string;
    }
  | {
      type: 'chart_data';
      payload: {
        cuotaMensual?: number;
        totalPagado?: number;
        cae?: number;
        tasaAnual?: number;
        plazoMeses?: number;
        monto?: number;
        seguroMensualPct?: number;
        comisionApertura?: number;
        bankAnual?: number;
        notas?: string;
      };
    }
  | { type: 'error'; message: string };
