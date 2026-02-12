---
name: building-financial-apps
description: Enforces the 'Zero-Parsing' AI architecture (Vercel AI SDK + React 19 + Gemini) for financial applications. Use when the user asks to build, refactor, or modernize financial dashboards or chat interfaces.
---

# Financial App Building (Zero-Parsing Architecture)

## When to use this skill
- Building or refactoring `stock-terminal-next`.
- Implementing AI Chat interfaces in financial apps.
- When the user mentions "Zero-Parsing", "Protocol Fragility", or "Vercel AI SDK".
- Streaming structured data (charts, widgets) alongside text.

## Workflow
[ ] **Backend**: Implement `AIStreamProtocol` in FastAPI (SSE with Type Codes 0, 2, 9).
[ ] **Agent**: Use Gemini 3.0/1.5 with Pydantic schemas (structured output) to enforce valid JSON for widgets.
[ ] **Frontend**: Use `ai/react` (`useChat`) and `zustand` (State) instead of manual `fetch` loops.
[ ] **Testing**: Verify streaming protocol using `httpx` (backend) and `msw` (frontend).

## Instructions

### 1. The Executive Vision: Zero-Parsing
Stop parsing LLM output with Regex. Strictly separate **Content** (Text) from **Data** (Tool Calls, Charts).
- **Text** -> Stream `0: "content"`
- **Data (Widgets)** -> Stream `2: [{"chart": ...}]`
- **Tool Calls** -> Stream `9: {...}`

### 2. Backend Implementation (FastAPI)

#### Protocol Helper (`backend/protocol.py`)
```python
import json
from typing import Any

class AIStreamProtocol:
    @staticmethod
    def text(content: str) -> str:
        """Type 0: Text Part"""
        return f'0:{json.dumps(content)}\n'

    @staticmethod
    def data(payload: Any) -> str:
        """Type 2: Data Part (Widgets, Charts). Must be a list."""
        return f'2:{json.dumps([payload])}\n'

    @staticmethod
    def tool_call(call_id: str, name: str, args: dict) -> str:
        """Type 9: Tool Call"""
        payload = {"toolCallId": call_id, "toolName": name, "args": args}
        return f'9:{json.dumps(payload)}\n'
```

#### Structured Agent (`backend/agent.py`)
Use Pydantic V2 to enforce schema.
```python
class AgentResponse(BaseModel):
    part: Union[LineChart, TextResponse]

# When streaming:
# yield AIStreamProtocol.text(chunk.text)
# yield AIStreamProtocol.data(widget_object)
```

### 3. Frontend Architecture (React 19)

#### Global State (`src/store/dashboardStore.ts`)
Use **Zustand** to hold the "active chart" state, avoiding prop drilling.
```typescript
interface DashboardState {
  activeChart: ChartData | null;
  setActiveChart: (chart: ChartData | null) => void;
}
export const useDashboardStore = create<DashboardState>((set) => ({ ... }));
```

#### Custom Hook (`useTerminalChat.ts`)
Use `useChat` from Vercel AI SDK. Listen for `data` events to update global state.
```typescript
import { useChat } from 'ai/react';
export function useTerminalChat() {
  const setActiveChart = useDashboardStore((s) => s.setActiveChart);
  const { messages, data } = useChat({
    api: 'http://localhost:8001/chat',
  });

  // Effect: Update chart when new Data (Type 2) arrives
  useEffect(() => {
    if (!data) return;
    const latest = data[data.length - 1];
    if (latest && latest.type === 'line_chart') setActiveChart(latest);
  }, [data, setActiveChart]);
  
  return { messages };
}
```

### 4. Testing Strategy
- **Backend**: Use `httpx` to consume the streaming response line-by-line and assert `0:` and `2:` prefixes.
- **Frontend**: Use `msw` to mock the SSE stream (`TextEncoder` -> `controller.enqueue`).

## Resources
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs)
- [Gemini Structured Outputs](https://ai.google.dev/)
